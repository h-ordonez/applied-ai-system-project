# PawPal+ RAG

This project builds on the PawPal+ task management app. The original PawPal+ app enabled pet owners to create and schedule tasks for each one of their pets. It would also check for schdeduling conflicts and warn the user accordingly.

This iteration of the PawPal+ app preserves the original functionality and adds a Retrieval-Augmented Generation (RAG) feature that is coupled to another added feature that provides a section for pet owners to create and store notes for each pet. Together, these features allow pet owners to ask PawPal questions regarding their pets. PawPal then checks the pet's notes and provides a response. This helps pet owners stay informed about their pets needs.

## Architecture Overview

PawPal+ RAG has four main components:

- Streamlit UI
- Input Validation
- Knowledge Base
- RAG (Google Gemini)

From the Streamlit UI, pet owners can create and schedule tasks for their pets, as well as save notes regarding a specific pet. The Streamlit UI handles input validation edge cases where pet owners may attempt to store empty notes. The notes are then passed to the input validation component where checks are made to strip extra white-space and verify that alphabetical characters are present. If the note passes inspection, it is stored in the knowledge base, i.e., with the pet.

A pet owner can ask a question using the Ask PawPal feature. The question is first passed through the same input validation component to mitigate against junk questions being passed to the API. After passing input validation, the pet and its notes are sent to the RAG component. From here, the RAG component sends its response back the Streamlit UI for the pet owner to review.

## Setup Instructions

1. Clone the repository and navigate into the project directory.

2. Create and activate a virtual environment

   ```bash
   python -m venv .venv
   # Windows
   .venv\Scripts\activate
   # macOS/Linux
   source .venv/bin/activate
   ```

3. Install dependencies
    ```bash
    pip install -r requirements.txt
    ```

4. Configure your Gemini API key

    Create a .env file in the project root with:
    ```bash
    GEMINI_API_KEY=your_api_key_here
    ```

    You can obtain a key from Google AI Studio. The app will run without this key, but the "Ask PawPal" feature will be disabled and a warning will be shown.

5. Run the app

    ```bash
    streamlit run app.py
    ```
    This opens the PawPal+ UI in your browser.

6. (Optional) Run the test suite

    ```bash
    pytest
    ```
    
## Sample Interactions

**Example 1 - Note available**
- Input care note for Rex:
    ```
    The Vet says Rex needs to walk for at least 20 minutes per day.
    ```
- Input question for Ask PawPal:
    ```
    How long should I walk Rex for?
    ```
- AI output:
    ```
    According to Rex's care notes, the vet says Rex needs to walk for at least 20 minutes per day.
    ```

**Example 2 - Note unavailable**
- No input care notes for Mochi

- Input question for Ask PawPal:
    ```
    What type of diet should I feed Mochi?
    ```
- AI output:
    ```
    I don't have any care notes for Mochi yet that relate to this question. Add a care note below, or check with your vet directly.
    ```

## Design Decisions

This project was built this way to help pet owner's make notes and get answers to their questions based on these notes. The Ask PawPal feature only provides responses based on these notes so that the AI does not mislead pet owners by providing information that has not been recorded for a specific pet. It also provides pet owners with the notes that it used to formulate its response so that the owner's themselves can discern whether or not the response provided by the AI is grounded in information stored by pet owners. If a pet owner asks a question regarding something urgent for their pet like pain, then the AI responds by having the pet owner defer to a veterinarian. This is because the AI is not equipped to make diagnoses.

## Testing Summary

I performed a number of different tests for this project. The AI was very good at answering questions if I used keywords in the notes that it could very easily identify. However, it struggled to answer questions if the question was not directly related to a note. For example, I created a note that said, "The vet says Rex should eat a bland diet," but when I asked PawPal, "Should I feed Rex rice and chicken?", it said it did not have any notes related to that question. This taught me that even though the AI is good at answering some questions, it still needs to be guided with appropriately phrased questions.

### Human Evaluation of AI

| Test Input | Evaluation Criteria | Result |
|---|---|---|
| "How long should I walk Rex for?" | Accurate response for time to walk | Pass |
| "What type of diet should I feed Mochi?" - No notes exist | Indicates to user that a note does not exist | Pass |
| Empty input | Informs user that empty input cannot be used | Pass |


## Reflection

I learned a lot about AI and it's limitations related to RAG. For instance, it needs a lot of information from which it can formulate appropriate responses. It illustrates how important it is to make sure that accurate and detailed information is stored for these types of systems. Otherwise, if garbage goes in, garbage comes out.