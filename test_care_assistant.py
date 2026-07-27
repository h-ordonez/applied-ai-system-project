from unittest.mock import MagicMock

from care_assistant import DEFAULT_MODEL, CareAssistant
from pawpal_system import Pet


def make_pet(*note_texts, name="Rex"):
    pet = Pet(name=name, species="dog", age=3)
    for text in note_texts:
        pet.addCareNote(text)
    return pet


def make_client(answer_text: str) -> MagicMock:
    client = MagicMock()
    client.models.generate_content.return_value = MagicMock(text=answer_text)
    return client


def test_no_notes_short_circuits_without_calling_the_api():
    client = make_client("unused")
    assistant = CareAssistant(client=client)
    pet = make_pet()

    result = assistant.ask(pet, "should I be worried about Rex?")

    client.models.generate_content.assert_not_called()
    assert result.cited_notes == []
    assert pet.name in result.answer


def test_ask_grounds_the_prompt_in_only_this_pets_retrieved_notes():
    client = make_client("Keep Rex away from peanut butter and watch for swelling.")
    assistant = CareAssistant(client=client)
    pet = make_pet(
        "Rex is allergic to peanuts and should avoid peanut butter treats.",
        "Rex enjoys long walks in the park every morning.",
    )

    result = assistant.ask(pet, "peanut allergy symptoms")

    assert result.answer == "Keep Rex away from peanut butter and watch for swelling."
    assert len(result.cited_notes) == 1
    assert "peanut" in result.cited_notes[0].text

    client.models.generate_content.assert_called_once()
    call_kwargs = client.models.generate_content.call_args.kwargs
    assert call_kwargs["model"] == DEFAULT_MODEL
    assert pet.name in call_kwargs["config"].system_instruction

    user_content = call_kwargs["contents"]
    assert "peanut" in user_content
    assert "long walks" not in user_content
