import math
import re
from collections import Counter
from typing import Dict, List

from pawpal_system import CareNote, Pet

_TOKEN_RE = re.compile(r"[a-z0-9]+")


def _tokenize(text: str) -> List[str]:
    """Lowercase and split text into alphanumeric tokens."""
    return _TOKEN_RE.findall(text.lower())


def _cosine_similarity(a: Dict[str, float], b: Dict[str, float]) -> float:
    shared_terms = a.keys() & b.keys()
    dot = sum(a[term] * b[term] for term in shared_terms)
    norm_a = math.sqrt(sum(weight * weight for weight in a.values()))
    norm_b = math.sqrt(sum(weight * weight for weight in b.values()))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


class NoteRetriever:
    """Retrieves the care notes most relevant to a query, via TF-IDF + cosine similarity.

    The vocabulary and document frequencies are built fresh from a single pet's
    notes on every call, scoping retrieval to that pet - one pet's notes never
    surface as context for a question about a different pet.
    """

    def retrieve(self, pet: Pet, query: str, k: int = 3) -> List[CareNote]:
        notes = pet.careNotes
        if not notes:
            return []

        tokenized_notes = [_tokenize(note.text) for note in notes]
        doc_frequency = Counter()
        for tokens in tokenized_notes:
            doc_frequency.update(set(tokens))

        num_notes = len(notes)

        def idf(term: str) -> float:
            df = doc_frequency.get(term, 0)
            return math.log((1 + num_notes) / (1 + df)) + 1

        def tfidf_vector(tokens: List[str]) -> Dict[str, float]:
            term_counts = Counter(tokens)
            return {term: count * idf(term) for term, count in term_counts.items()}

        note_vectors = [tfidf_vector(tokens) for tokens in tokenized_notes]
        query_vector = tfidf_vector(_tokenize(query))

        scored = [
            (_cosine_similarity(query_vector, note_vector), note)
            for note_vector, note in zip(note_vectors, notes)
        ]
        relevant = [(score, note) for score, note in scored if score > 0]
        relevant.sort(key=lambda pair: pair[0], reverse=True)
        return [note for _, note in relevant[:k]]
