# SmartSplit - Current vs Required Project Structure Analysis

## Current Project Structure

```
LLMChunker/
├── chunks.json                    # Generated output file
├── demo.py                       # Basic demo with Google Gemini
├── pyproject.toml               # Build configuration
├── README.md                    # Basic documentation
├── reconstructed_text.md        # Generated output file
├── requirements.txt             # Dependencies list
├── run_tests.py                 # Test runner script
├── demo_context/
│   ├── about_me.md             # Demo input file
│   └── reconstructed_text.md   # Generated output
└── smart_split/
    ├── __init__.py             # Package initialization (empty)
    ├── splitter.py             # Main implementation (monolithic)
    └── tests/
        └── test_splitter.py    # Basic unit tests
```

## Issues with Current Structure

### 1. Single Responsibility Principle Violations
- `splitter.py` contains multiple responsibilities:
  - LLM integration
  - Text reconstruction logic
  - Prompt management
  - Chunk validation
  - All data models

### 2. Missing Core Components
- No document format handling
- No configuration management
- No proper error handling classes
- No strategy management separation
- No validation utilities

### 3. Limited Test Coverage
- Only basic unit tests
- No integration tests
- No performance tests
- No error scenario testing

### 4. Poor Code Organization
- Hardcoded prompts mixed with business logic
- No separation between core engine and utilities
- Missing proper package structure

## Required Project Structure (PEP8 Compliant)

```
smart_split/
├── setup.py                          # Installation script
├── pyproject.toml                   # Build system configuration
├── README.md                        # Project documentation
├── LICENSE                          # License file
├── CHANGELOG.md                     # Version history
├── requirements.txt                 # Production dependencies
├── requirements-dev.txt             # Development dependencies
├── .gitignore                       # Git ignore patterns
├── .pre-commit-config.yaml         # Code quality hooks
├── docs/                           # Documentation
│   ├── api_reference.md
│   ├── user_guide.md
│   ├── examples.md
│   └── contributing.md
├── examples/                       # Usage examples
│   ├── basic_usage.py
│   ├── translation_workflow.py
│   ├── custom_strategies.py
│   └── large_documents.py
├── tests/                         # Test suite
│   ├── conftest.py               # Pytest configuration
│   ├── fixtures/                 # Test data
│   │   ├── sample_documents/
│   │   └── expected_outputs/
│   ├── unit/                     # Unit tests
│   │   ├── test_core/
│   │   ├── test_processors/
│   │   ├── test_strategies/
│   │   └── test_utils/
│   ├── integration/              # Integration tests
│   │   ├── test_llm_providers.py
│   │   └── test_end_to_end.py
│   └── performance/              # Performance tests
│       ├── test_large_documents.py
│       └── benchmark_strategies.py
└── smart_split/                  # Main package
    ├── __init__.py               # Package exports
    ├── core/                     # Core engine components
    │   ├── __init__.py
    │   ├── splitter.py          # Main SmartSplitter class
    │   ├── models.py            # Pydantic data models
    │   ├── config.py            # Configuration management
    │   └── exceptions.py        # Custom exceptions
    ├── processors/              # Input/output processing
    │   ├── __init__.py
    │   ├── document.py          # Document format handlers
    │   ├── text.py              # Text preprocessing
    │   └── file_io.py           # File operations
    ├── strategies/              # Splitting strategies
    │   ├── __init__.py
    │   ├── base.py              # Base strategy interface
    │   ├── predefined.py        # Built-in strategies
    │   ├── custom.py            # Custom strategy handling
    │   └── prompts.py           # Prompt templates
    ├── reconstruction/          # Text reconstruction
    │   ├── __init__.py
    │   ├── engine.py            # Core reconstruction logic
    │   ├── validator.py         # Chunk validation
    │   └── error_handler.py     # Error recovery
    ├── llm/                     # LLM integration
    │   ├── __init__.py
    │   ├── adapter.py           # LangChain adapter
    │   ├── providers.py         # Provider-specific optimizations
    │   └── rate_limiter.py      # Rate limiting utilities
    └── utils/                   # Utility functions
        ├── __init__.py
        ├── text_utils.py        # Text processing utilities
        ├── logging.py           # Logging configuration
        └── metrics.py           # Performance metrics
```

## Detailed Component Breakdown

### Core Package (`smart_split/core/`)

#### `splitter.py` - Main SmartSplitter Class
```python
from typing import List, Union, Optional
from pathlib import Path
from langchain_core.language_models import BaseChatModel

from .config import SplitterConfig
from .models import ChunkResult, ChunkMarker
from ..strategies import StrategyManager
from ..processors import DocumentProcessor
from ..reconstruction import ReconstructionEngine
from ..llm import LLMAdapter

class SmartSplitter:
    """Main interface for intelligent document chunking."""
    
    def __init__(
        self, 
        llm: BaseChatModel, 
        config: Optional[SplitterConfig] = None
    ):
        self.config = config or SplitterConfig()
        self.llm_adapter = LLMAdapter(llm, self.config)
        self.strategy_manager = StrategyManager()
        self.document_processor = DocumentProcessor()
        self.reconstruction_engine = ReconstructionEngine()
    
    def split(
        self, 
        text: str, 
        strategy: str = 'topic', 
        criteria: Optional[str] = None
    ) -> ChunkResult:
        """Split text into semantic chunks."""
        pass
    
    def split_file(
        self, 
        file_path: Union[str, Path], 
        **kwargs
    ) -> ChunkResult:
        """Split document file into semantic chunks."""
        pass
```

#### `models.py` - Data Models
```python
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum

class DocumentFormat(str, Enum):
    TEXT = "text"
    MARKDOWN = "markdown"  
    HTML = "html"
    PDF = "pdf"

class ChunkMarker(BaseModel):
    """Represents chunk boundary markers from LLM response."""
    chunk_index: int = Field(..., ge=0)
    start_marker: str = Field(..., min_length=1)
    end_marker: str = Field(..., min_length=1)
    summary: str = Field(..., min_length=1)
    confidence: Optional[float] = Field(None, ge=0.0, le=1.0)

class ChunkMetadata(BaseModel):
    """Metadata about the chunking process."""
    total_chunks: int
    original_length: int
    total_reconstructed_length: int
    strategy_used: str
    processing_time: float
    llm_calls: int

class ChunkResult(BaseModel):
    """Complete result of document chunking."""
    chunks: List[str]
    metadata: ChunkMetadata
    markers: List[ChunkMarker]
    validation_passed: bool
    errors: List[str] = []
```

#### `config.py` - Configuration Management
```python
from pydantic import BaseModel, Field
from typing import Optional

class SplitterConfig(BaseModel):
    """Configuration for SmartSplitter behavior."""
    
    # Chunk size limits
    max_chunk_size: int = Field(default=100000, gt=0)
    min_chunk_size: int = Field(default=100, gt=0) 
    preferred_chunk_size: int = Field(default=4000, gt=0)
    
    # Processing options
    overlap_tokens: int = Field(default=50, ge=0)
    retry_attempts: int = Field(default=3, ge=1)
    validate_reconstruction: bool = True
    enable_hierarchical_splitting: bool = True
    
    # LLM options
    llm_timeout: int = Field(default=60, gt=0)
    rate_limit_delay: float = Field(default=1.0, ge=0)
    
    # Error handling
    fail_on_reconstruction_error: bool = True
    fallback_to_character_split: bool = False
    
    class Config:
        validate_assignment = True
```

#### `exceptions.py` - Custom Exceptions
```python
class SmartSplitError(Exception):
    """Base exception for SmartSplit library."""
    pass

class ReconstructionError(SmartSplitError):
    """Raised when chunk reconstruction fails."""
    def __init__(self, message: str, chunk_index: int = None):
        super().__init__(message)
        self.chunk_index = chunk_index

class LLMError(SmartSplitError):
    """Raised when LLM interaction fails."""
    pass

class ValidationError(SmartSplitError):
    """Raised when chunk validation fails."""
    pass

class ConfigurationError(SmartSplitError):
    """Raised when configuration is invalid."""
    pass
```

### Strategy Management (`smart_split/strategies/`)

#### `base.py` - Base Strategy Interface
```python
from abc import ABC, abstractmethod
from langchain_core.prompts import PromptTemplate
from ..core.models import ChunkMarker
from typing import List

class BaseStrategy(ABC):
    """Abstract base class for splitting strategies."""
    
    @abstractmethod
    def get_prompt_template(self) -> PromptTemplate:
        """Return the prompt template for this strategy."""
        pass
    
    @abstractmethod
    def validate_markers(self, markers: List[ChunkMarker]) -> bool:
        """Validate that markers are appropriate for this strategy."""
        pass
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Strategy name."""
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """Strategy description."""
        pass
```

#### `predefined.py` - Built-in Strategies
```python
from .base import BaseStrategy
from .prompts import PromptTemplates
from langchain_core.prompts import PromptTemplate

class TopicStrategy(BaseStrategy):
    """Split by distinct topics or subtopics."""
    
    @property
    def name(self) -> str:
        return "topic"
    
    @property  
    def description(self) -> str:
        return "Divide document into distinct topics or subtopics"
    
    def get_prompt_template(self) -> PromptTemplate:
        return PromptTemplates.TOPIC_SPLITTING
    
    # ... implementation

class QuestionAnswerStrategy(BaseStrategy):
    """Split into question-answer pairs."""
    # ... implementation

# Additional predefined strategies...
```

### Document Processing (`smart_split/processors/`)

#### `document.py` - Format Handlers
```python
from pathlib import Path
from typing import Union, Optional
from ..core.models import DocumentFormat
from ..core.exceptions import SmartSplitError

class DocumentProcessor:
    """Handles different document formats and preprocessing."""
    
    def load_document(
        self, 
        source: Union[str, Path]
    ) -> tuple[str, DocumentFormat]:
        """Load document and detect format."""
        pass
    
    def preprocess_text(
        self, 
        text: str, 
        format: DocumentFormat
    ) -> str:
        """Preprocess text based on format."""
        pass
    
    def extract_structure(
        self, 
        text: str, 
        format: DocumentFormat
    ) -> dict:
        """Extract structural information from document."""
        pass
```

### Reconstruction Engine (`smart_split/reconstruction/`)

#### `engine.py` - Core Reconstruction Logic
```python
from typing import List
from ..core.models import ChunkMarker, ChunkResult
from ..core.exceptions import ReconstructionError
from .validator import ChunkValidator

class ReconstructionEngine:
    """Handles text reconstruction from chunk markers."""
    
    def __init__(self):
        self.validator = ChunkValidator()
    
    def reconstruct_chunks(
        self, 
        original_text: str, 
        markers: List[ChunkMarker]
    ) -> List[str]:
        """Reconstruct text chunks from markers."""
        pass
    
    def validate_reconstruction(
        self, 
        original: str, 
        reconstructed: List[str]
    ) -> bool:
        """Validate that reconstruction is accurate."""
        pass
```

## Migration Plan

### Phase 1: Refactor Core Components (Week 1-2)
1. Extract data models to separate files
2. Create configuration management system
3. Separate strategy management from core splitter
4. Implement proper exception hierarchy

### Phase 2: Improve Architecture (Week 3-4)
1. Create document processor for different formats
2. Implement reconstruction engine with better error handling
3. Add LLM adapter layer for provider optimizations
4. Create utility modules for common operations

### Phase 3: Enhance Testing (Week 5-6)
1. Create comprehensive test suite structure
2. Add integration tests with real LLM providers
3. Implement performance benchmarking
4. Add test fixtures and mock data

### Phase 4: Documentation & Examples (Week 7-8)
1. Create comprehensive API documentation
2. Build example gallery for common use cases
3. Write user guide and best practices
4. Add contributing guidelines

## Benefits of New Structure

### 1. Single Responsibility Principle
- Each module has a single, well-defined purpose
- Easy to understand, test, and maintain
- Supports independent development of components

### 2. Separation of Concerns
- Clear boundaries between different aspects of functionality
- Easier to modify or replace individual components
- Better testability with isolated units

### 3. Extensibility
- Easy to add new strategies without touching core logic
- Plugin architecture for document formats
- Configurable behavior without code changes

### 4. Maintainability
- Clear code organization following Python conventions
- Comprehensive test coverage
- Proper error handling and logging

### 5. Professional Standards
- Follows PEP8 and Python best practices
- Production-ready code structure
- Comprehensive documentation and examples

This restructured approach transforms the current monolithic implementation into a professional, maintainable, and extensible Python library suitable for production use.
