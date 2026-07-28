import pytest

from pawpal_system import CARE_NOTE_MAX_LENGTH, Pet


def make_pet(name="Rex"):
    return Pet(name=name, species="dog", age=3)


def test_add_care_note_stores_stripped_text():
    pet = make_pet()

    note = pet.addCareNote("  Rex needs his heartworm pill.  ")

    assert note.text == "Rex needs his heartworm pill."
    assert pet.careNotes == [note]


def test_add_care_note_rejects_empty_text():
    pet = make_pet()

    with pytest.raises(ValueError):
        pet.addCareNote("")

    assert pet.careNotes == []


def test_add_care_note_rejects_whitespace_only_text():
    pet = make_pet()

    with pytest.raises(ValueError):
        pet.addCareNote("   \n\t  ")

    assert pet.careNotes == []


def test_add_care_note_rejects_text_over_max_length():
    pet = make_pet()

    with pytest.raises(ValueError):
        pet.addCareNote("a" * (CARE_NOTE_MAX_LENGTH + 1))

    assert pet.careNotes == []


def test_add_care_note_allows_text_at_max_length():
    pet = make_pet()

    note = pet.addCareNote("a" * CARE_NOTE_MAX_LENGTH)

    assert len(note.text) == CARE_NOTE_MAX_LENGTH


def test_add_care_note_rejects_text_without_letters():
    pet = make_pet()

    with pytest.raises(ValueError):
        pet.addCareNote("123 !@# 456")

    assert pet.careNotes == []


def test_add_care_note_allows_non_english_letters():
    pet = make_pet()

    note = pet.addCareNote("猫は元気です")

    assert note.text == "猫は元気です"
