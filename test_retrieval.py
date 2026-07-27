from pawpal_system import Pet
from retrieval import NoteRetriever


def make_pet(*note_texts, name="Rex"):
    pet = Pet(name=name, species="dog", age=3)
    for text in note_texts:
        pet.addCareNote(text)
    return pet


def test_no_notes_returns_empty_list():
    pet = make_pet()
    retriever = NoteRetriever()

    assert retriever.retrieve(pet, "any question") == []


def test_most_relevant_note_ranks_first():
    pet = make_pet(
        "Rex is allergic to peanuts and should avoid any peanut butter treats.",
        "Rex enjoys long walks in the park every morning.",
        "Rex had his nails trimmed at the groomer last week.",
    )
    retriever = NoteRetriever()

    results = retriever.retrieve(pet, "is Rex allergic to peanuts?")

    assert results[0].text.startswith("Rex is allergic to peanuts")


def test_respects_k_limit():
    pet = make_pet(
        "Rex loves chasing squirrels in the yard.",
        "Rex chased a squirrel again today and got very muddy.",
        "Rex tried to chase a squirrel up a tree this morning.",
    )
    retriever = NoteRetriever()

    results = retriever.retrieve(pet, "squirrel chasing", k=2)

    assert len(results) == 2


def test_retrieval_is_scoped_to_the_given_pet():
    rex = make_pet("Rex has a broken leg and needs to rest for six weeks.", name="Rex")
    whiskers = make_pet("Whiskers loves tuna and naps all afternoon.", name="Whiskers")
    retriever = NoteRetriever()

    results = retriever.retrieve(whiskers, "broken leg recovery")

    assert results == []
    assert all(note in rex.careNotes for note in retriever.retrieve(rex, "broken leg"))


def test_unrelated_query_returns_no_notes():
    pet = make_pet("Rex needs his heartworm medication every month.")
    retriever = NoteRetriever()

    assert retriever.retrieve(pet, "what is the capital of france") == []
