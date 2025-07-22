# SmartSplit

SmartSplit is a Python library for intelligent, semantic chunking of large documents using Large Language Models (LLMs).

## Installation

```bash
pip install smart-split
```

## Usage

Here's a quick example of how to use SmartSplit:

```python
from smart_split import SmartSplitter
from langchain_google_genai import ChatGoogleGenerativeAI

# User provides their own configured LLM instance
llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash")

# The splitter is initialized with the user's LLM
splitter = SmartSplitter(llm=llm)

document_text = "..." # Long document text

# Split by topic (default)
chunks = splitter.split(text=document_text)

# Split using a pre-defined strategy
chunks_qa = splitter.split(text=document_text, strategy='question_answer')

# Split using a custom prompt
custom_instructions = "Divide the document into the smallest possible coherent parts. Each new chunk should represent a distinct topic or sub-topic."
chunks_custom = splitter.split(
    text=document_text,
    segmentation_criteria=custom_instructions
)
```

## Features

- **LLM-Powered Semantic Splitting**: Leverages LLMs to understand the context of your documents and split them into logically coherent chunks.
- **Flexible LLM Provider Integration**: Works with any LangChain-compatible `BaseChatModel`.
- **Custom Splitting Logic**: Guide the splitting process with natural language prompts.
- **Pre-defined Splitting Strategies**: A set of ready-to-use strategies for common use cases.
- **Handles Extremely Large Documents**: Automatically performs hierarchical splitting for documents that exceed the LLM's context window.
