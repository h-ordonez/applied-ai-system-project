## Limitations or Biases of PawPal+ RAG

One limitation in this system is the ability of the AI to glean the context for itself from a limited number of notes. If a question is asked that does not make direct reference to a saved note, then the AI's response will be that a relevant note does not exist. This is a limitation because the information may be present, but if there isn't enough information for the AI to connect the dots, it will not.

## Potential for Misuse

The system is currently susceptible to prompt injection. This is because the only data validation that occurs for adding notes and asking questions is limited to a character limit and checking for at least one letter. There is no mecahnism in place to check for instruction patterns that may be placed in the notes or questions.

Currently, the severity of prompt injection is limited by the fact that this is a single user system. The pet owner is the only person who can add notes or ask questions. However, if other parties are granted permissions to use these features, the severity increases.

## AI Reliability

One thing that surprised me about the AI's reliability was its abliity to discern between questions regarding non-urgent matters and urgent matters. For example, the AI was able to correctly defer the pet owner to a veterenarian if the pet owner had questions regarding pain.

## AI Project Collaboration

I collaborated with Claude on how to best integrate Retrievaal Augmented Generation. I had the idea that the knowledge base could be care notes that a pet owner creates for each pet.

Claude was helpful when it suggested that pet care notes should be stored with each pet. My initial idea was that pet owners would own the care notes, but Claude suggested that pets should own their notes because it would simplify the Ask PawPal feature. This would also prevent notes from other pets to be inadvertently used.

One instance where Claude made a mistake had to do with the output message it produced when there are no care notes present and the user asks a question. The message prompts the user to enter a care note below, however, the correct place to enter a care note is above.