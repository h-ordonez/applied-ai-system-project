from dataclasses import dataclass, field
from typing import List

from google.genai import types

from pawpal_system import CareNote, Pet
from retrieval import NoteRetriever

DEFAULT_MODEL = "gemini-3.5-flash-lite"

QUESTION_MAX_LENGTH = 300

NO_NOTES_ANSWER = (
    "I don't have any care notes for {pet_name} yet that relate to this question. "
    "Add a care note below, or check with your vet directly."
)

SYSTEM_PROMPT = """You are a pet care assistant helping an owner understand their pet's care notes.

Answer the owner's question using ONLY the care notes provided below for {pet_name} \
(a {pet_age}-year-old {pet_species}). Do not rely on general knowledge about pets, and do not \
guess at anything the notes don't cover - say so plainly if the notes don't have enough information.

This is not a substitute for veterinary care: if the question describes something urgent, \
worsening, or that would need a diagnosis, tell the owner to contact their vet instead of \
speculating."""


@dataclass
class AssistantAnswer:
    answer: str
    cited_notes: List[CareNote] = field(default_factory=list)


class CareAssistant:
    """Answers owner questions about a pet, grounded in that pet's retrieved care notes."""

    def __init__(self, client, retriever: NoteRetriever = None, model: str = DEFAULT_MODEL):
        self.client = client
        self.retriever = retriever or NoteRetriever()
        self.model = model

    def ask(self, pet: Pet, question: str) -> AssistantAnswer:
        stripped = question.strip()
        if not stripped:
            raise ValueError("Question cannot be empty.")
        if len(stripped) > QUESTION_MAX_LENGTH:
            raise ValueError(f"Question cannot exceed {QUESTION_MAX_LENGTH} characters.")
        if not any(c.isalpha() for c in stripped):
            raise ValueError("Question must contain at least one letter.")

        cited_notes = self.retriever.retrieve(pet, stripped)
        if not cited_notes:
            return AssistantAnswer(answer=NO_NOTES_ANSWER.format(pet_name=pet.name), cited_notes=[])

        notes_block = "\n".join(f"- ({note.date}) {note.text}" for note in cited_notes)
        user_content = f"Care notes for {pet.name}:\n{notes_block}\n\nQuestion: {stripped}"

        response = self.client.models.generate_content(
            model=self.model,
            contents=user_content,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT.format(
                    pet_name=pet.name, pet_age=pet.age, pet_species=pet.species
                ),
                max_output_tokens=512,
            ),
        )
        return AssistantAnswer(answer=response.text, cited_notes=cited_notes)
