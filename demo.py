from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field

from dotenv import load_dotenv
import os
load_dotenv()



llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    max_retries=2,
)

# read all md files from r"demo_context/" folder to dict
md_files_dict = {}
folder_path = r"demo_context/"

for filename in os.listdir(folder_path):
    if filename.endswith(".md"):
        file_path = os.path.join(folder_path, filename)
        with open(file_path, 'r', encoding='utf-8') as file:
            md_files_dict[filename] = file.read()

class Chunk(BaseModel):
    """Represents a single, logical segment of a larger document."""

    chunk_index: int = Field(
        ..., 
        description="A zero-based integer representing the sequential order of the chunk. The first chunk has an index of 0, the second has 1, and so on. This field ensures the original document can be perfectly reconstructed in the correct order."
    )
    
    start_chunk: str = Field(
        ..., 
        description="A very short substring (typically 3-10 words) from the beginning of this chunk that uniquely identifies where the chunk starts. Should be minimal text - just enough to locate the chunk boundary, NOT the entire chunk content."
    )
    
    end_chunk: str = Field(
        ..., 
        description="A very short substring (typically 3-10 words) from the end of this chunk that uniquely identifies where the chunk ends. Should be minimal text - just enough to locate the chunk boundary, NOT the entire chunk content."
    )
    
    summary_chunk: str = Field(
        ..., 
        description="A concise, high-level vsery short summary of the core topic or main points contained within this specific chunk. This provides a quick, human-readable understanding of the segment's content."
    )

parser = JsonOutputParser(pydantic_object=Chunk)

SYSTEM_PROMPT="""
You are an expert in information segmentation, tasked with creating a structured manifest for a large text document. The output will be used by a script to programmatically partition the original text.

The user will provide you with a comprehensive document. Your task is to return a JSON array of objects, where each object represents a logical chunk.

Each chunk object in the JSON array must contain:

*   **`chunk_index`** (integer): The zero-based index of the chunk in the sequence (0, 1, 2, ...).
*   **`start_chunk`** (string): The EXACT first few words from the document that start this chunk. Must be actual text from the document, not numbers or indices.
*   **`end_chunk`** (string): The EXACT last few words from the document that end this chunk. Must be actual text from the document, not numbers or indices.
*   **`summary_chunk`** (string): A concise summary of the chunk's content.

**CRITICAL EXAMPLES:**

**CORRECT FORMAT:**
```json
{
  "chunk_index": 0,
  "start_chunk": "Question 1: The Elevator Pitch",
  "end_chunk": "how such things are even possible.",
  "summary_chunk": "Introduction and elevator pitch response"
}
```

**ANOTHER CORRECT EXAMPLE:**
```json
{
  "chunk_index": 1,
  "start_chunk": "Question 2: Your Dream Job",
  "end_chunk": "in one way or another.",
  "summary_chunk": "Discussion about dream job in AI field"
}
```

**WRONG FORMAT (DO NOT DO THIS):**
```json
{
  "chunk_index": 0,
  "start_chunk": 0,
  "end_chunk": 105,
  "summary_chunk": "..."
}
```

**MANDATORY RULES:**
1. **start_chunk** and **end_chunk** must be ACTUAL TEXT from the document, not numbers
2. Keep them short (3-10 words) but they must be real words from the text
3. These are literal text snippets that will be searched for in the document
4. Never use character positions, line numbers, or any numeric indices

**REMEMBER: Extract actual words from the document, not positions or numbers!**
"""

PROMPT_TEMPLATE="""
Your task is to segment the document provided below into logical chunks based on a specific set of criteria.

Your primary goal is to apply the following segmentation logic:
---
[INSTRUCTIONS]
{segmentation_criteria}
---

After applying this logic, generate the JSON output according to your core system instructions.

CRITICAL REMINDER: 
- start_chunk and end_chunk must be ACTUAL TEXT WORDS from the document
- NOT numbers, NOT character positions, NOT indices
- REAL WORDS that appear in the text

EXAMPLE of what I want:
```json
[
  {{
    "chunk_index": 0,
    "start_chunk": "Of course. Here is the complete",
    "end_chunk": "...how such things are even possible.",
    "summary_chunk": "Introduction and elevator pitch"
  }},
  {{
    "chunk_index": 1,
    "start_chunk": "Question 2: Your Dream Job",
    "end_chunk": "in one way or another.",
    "summary_chunk": "Discussion about dream job"
  }}
]
```

---
[DOCUMENT TEXT]
{document_text}
---
"""

BASIC_INSTRUCTIONS="""
"Divide the document into the smallest possible coherent parts. Each new chunk should represent a distinct topic or sub-topic discussed in the overall document."
"""
##################################################################



SystemMessage(content=SYSTEM_PROMPT),
prompt = PromptTemplate(
    SystemMessage=SYSTEM_PROMPT,
    template=PROMPT_TEMPLATE,
    input_variables=["segmentation_criteria", "document_text"],
    partial_variables={"format_instructions": parser.get_format_instructions()},
)

chain = prompt | llm | parser


response = chain.invoke({"segmentation_criteria":BASIC_INSTRUCTIONS, "document_text": md_files_dict["about_me.md"]})
print(response)
