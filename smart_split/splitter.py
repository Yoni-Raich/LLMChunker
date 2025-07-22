from pydantic import BaseModel, Field
from typing import List, Optional
from langchain_core.language_models import BaseChatModel
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_text_splitters import RecursiveCharacterTextSplitter


class Chunk(BaseModel):
    """Represents a single, logical segment of a larger document."""
    chunk_index: int = Field(...)
    start_chunk: str = Field(..., description="A short substring (3-10 words) from the beginning of this chunk...")
    end_chunk: str = Field(..., description="A short substring (3-10 words) from the end of this chunk...")
    summary_chunk: str = Field(..., description="A concise summary of the chunk's content.")

class ChunkList(BaseModel):
    chunks: List[Chunk]

SYSTEM_PROMPT = """
You are an expert in information segmentation. Your task is to divide a given document into a series of coherent, logical chunks. You will be provided with the document text and a specific instruction on how to segment it.

You MUST identify the start and end points of each chunk within the original text. Your output will be a JSON object containing a list of these identified chunks.

CRITICAL PAYLOAD FORMAT:
Your output MUST be a JSON object with a single key, "chunks", which contains a list of chunk objects. Each chunk object must conform to the following Pydantic schema:

class Chunk(BaseModel):
    '''Represents a single, logical segment of a larger document.'''
    chunk_index: int
    start_chunk: str # A short substring (3-10 words) from the beginning of this chunk
    end_chunk: str # A short substring (3-10 words) from the end of this chunk
    summary_chunk: str # A concise summary of the chunk's content.

CRITICAL EXAMPLES:
CORRECT FORMAT:
{
  "chunks": [
    {
      "chunk_index": 0,
      "start_chunk": "Question 1: The Elevator Pitch",
      "end_chunk": "how such things are even possible.",
      "summary_chunk": "Introduction and elevator pitch response"
    },
    {
      "chunk_index": 1,
      "start_chunk": "Question 2: Your Dream Job",
      "end_chunk": "in one way or another.",
      "summary_chunk": "Discussion about dream job"
    }
  ]
}

MANDATORY RULES:
1.  **`start_chunk` and `end_chunk` must be ACTUAL TEXT from the document.** They must be unique and sequential. Do not invent text that is not present.
2.  The chunks must cover the ENTIRE document. The `end_chunk` of one chunk should logically precede the `start_chunk` of the next. There should be no gaps or overlaps.
3.  The `chunk_index` must be a sequential integer starting from 0.
4.  Your entire response must be a single, valid JSON object. Do not include any explanatory text before or after the JSON.
"""

PREDEFINED_STRATEGIES = {
    'topic': "Divide the document into the smallest possible coherent parts. Each new chunk should represent a distinct topic or sub-topic.",
    'page': "Split the document based on logical page breaks or major sections. Each chunk should correspond to a natural division in the document's structure.",
    'question_answer': "Segment the document into question-and-answer pairs. Each chunk should contain exactly one question and its corresponding answer.",
    'narrative_scene': "Split the story into distinct scenes. Each chunk should represent a continuous block of action or dialogue in a single location."
}


class SmartSplitter:
    def __init__(self, llm: BaseChatModel, max_chunk_size: int = 10000):
        self.llm = llm
        self.max_chunk_size = max_chunk_size

    def split(self, text: str, strategy: str = 'topic', segmentation_criteria: Optional[str] = None) -> List[str]:
        if segmentation_criteria:
            criteria = segmentation_criteria
        elif strategy in PREDEFINED_STRATEGIES:
            criteria = PREDEFINED_STRATEGIES[strategy]
        else:
            raise ValueError(f"Unknown strategy: {strategy}. Please provide a custom `segmentation_criteria` or use one of the predefined strategies: {list(PREDEFINED_STRATEGIES.keys())}")

        if len(text) > self.max_chunk_size:
            # Hierarchical splitting
            coarse_splitter = RecursiveCharacterTextSplitter(chunk_size=self.max_chunk_size, chunk_overlap=200)
            super_chunks = coarse_splitter.split_text(text)

            final_chunks = []
            for super_chunk in super_chunks:
                final_chunks.extend(self._split_chunk(super_chunk, criteria))
            return final_chunks
        else:
            return self._split_chunk(text, criteria)

    def _split_chunk(self, text: str, criteria: str) -> List[str]:
        parser = JsonOutputParser(pydantic_object=ChunkList)

        prompt = ChatPromptTemplate.from_messages([
            ("system", SYSTEM_PROMPT),
            ("human", "Here is the document:\n\n---\n\n{document}\n\n---\n\nSegment the document based on the following criteria: {segmentation_criteria}")
        ])

        chain = prompt | self.llm | parser

        response = chain.invoke({
            "document": text,
            "segmentation_criteria": criteria
        })

        return self._reconstruct_chunks(text, response['chunks'])

    def _reconstruct_chunks(self, text: str, chunks: List[Chunk]) -> List[str]:
        reconstructed_chunks = []
        current_pos = 0
        for i, chunk_info in enumerate(chunks):
            try:
                # Find the start of the chunk.
                start_index = text.index(chunk_info.start_chunk, current_pos)

                # Find the end of the chunk.
                # We search from the start_index to ensure we get the correct end marker
                # in case of duplicate end markers in the text.
                end_index = text.index(chunk_info.end_chunk, start_index) + len(chunk_info.end_chunk)

                reconstructed_chunks.append(text[start_index:end_index])
                current_pos = end_index

            except ValueError as e:
                raise ValueError(f"Could not find start/end for chunk {i}: '{chunk_info.start_chunk}' / '{chunk_info.end_chunk}'") from e

        return reconstructed_chunks
