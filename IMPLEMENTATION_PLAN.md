# SmartSplit Implementation Plan

## Overview
This document outlines the step-by-step implementation plan to transform the current monolithic SmartSplit code into a production-ready, PEP8-compliant Python library following single responsibility principles.

## Implementation Phases

### Phase 1: Core Architecture Refactoring (Weeks 1-2)

#### 1.1 Create Core Data Models (Day 1)
**File**: `smart_split/core/models.py`

**Objective**: Extract all Pydantic models into a dedicated module.

```python
"""Core data models for SmartSplit library.

This module contains all Pydantic models used throughout the library,
following the single responsibility principle for data validation and serialization.
"""
from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional, Union
from datetime import datetime

from pydantic import BaseModel, Field, validator


class DocumentFormat(str, Enum):
    """Supported document formats."""
    TEXT = "text"
    MARKDOWN = "markdown"
    HTML = "html"
    PDF = "pdf"


class SplittingStrategy(str, Enum):
    """Available splitting strategies."""
    TOPIC = "topic"
    PAGE = "page"
    QUESTION_ANSWER = "question_answer"
    NARRATIVE_SCENE = "narrative_scene"
    SECTION = "section"
    PARAGRAPH = "paragraph"
    CUSTOM = "custom"


class ChunkMarker(BaseModel):
    """Represents chunk boundary markers returned by LLM.
    
    This model encapsulates the information needed to reconstruct
    text chunks from the original document.
    """
    chunk_index: int = Field(..., ge=0, description="Zero-based chunk index")
    start_marker: str = Field(
        ..., 
        min_length=1, 
        max_length=500,
        description="Actual text from document marking chunk start"
    )
    end_marker: str = Field(
        ..., 
        min_length=1, 
        max_length=500,
        description="Actual text from document marking chunk end"
    )
    summary: str = Field(
        ..., 
        min_length=1, 
        max_length=1000,
        description="Concise summary of chunk content"
    )
    confidence: Optional[float] = Field(
        None, 
        ge=0.0, 
        le=1.0,
        description="LLM confidence in chunk boundaries"
    )

    @validator('start_marker', 'end_marker')
    def validate_markers_not_empty(cls, v: str) -> str:
        """Ensure markers contain actual content."""
        if not v.strip():
            raise ValueError("Markers cannot be empty or whitespace only")
        return v.strip()


class ChunkMetadata(BaseModel):
    """Metadata about the chunking process and results."""
    total_chunks: int = Field(..., ge=0)
    original_length: int = Field(..., ge=0)
    total_reconstructed_length: int = Field(..., ge=0)
    strategy_used: str
    processing_time: float = Field(..., ge=0.0)
    llm_calls: int = Field(..., ge=0)
    timestamp: datetime = Field(default_factory=datetime.now)
    
    @property
    def reconstruction_accuracy(self) -> float:
        """Calculate reconstruction accuracy as percentage."""
        if self.original_length == 0:
            return 100.0
        return (self.total_reconstructed_length / self.original_length) * 100


class ValidationResult(BaseModel):
    """Result of chunk validation process."""
    is_valid: bool
    total_errors: int = 0
    errors: List[str] = []
    warnings: List[str] = []
    
    def add_error(self, error: str) -> None:
        """Add an error to the validation result."""
        self.errors.append(error)
        self.total_errors += 1
        self.is_valid = False
    
    def add_warning(self, warning: str) -> None:
        """Add a warning to the validation result."""
        self.warnings.append(warning)


class ChunkResult(BaseModel):
    """Complete result of document chunking operation."""
    chunks: List[str] = Field(..., description="Reconstructed text chunks")
    metadata: ChunkMetadata
    markers: List[ChunkMarker]
    validation: ValidationResult
    
    @property
    def is_successful(self) -> bool:
        """Check if chunking was successful."""
        return self.validation.is_valid and len(self.chunks) > 0
    
    def get_chunk_summaries(self) -> List[str]:
        """Get list of chunk summaries."""
        return [marker.summary for marker in self.markers]


class LLMResponse(BaseModel):
    """Structured response from LLM."""
    chunks: List[ChunkMarker]
    
    @validator('chunks')
    def validate_chunks_sequential(cls, v: List[ChunkMarker]) -> List[ChunkMarker]:
        """Ensure chunks have sequential indices."""
        if not v:
            return v
        
        expected_indices = list(range(len(v)))
        actual_indices = [chunk.chunk_index for chunk in v]
        
        if actual_indices != expected_indices:
            raise ValueError(
                f"Chunk indices must be sequential starting from 0. "
                f"Expected: {expected_indices}, Got: {actual_indices}"
            )
        
        return v
```

#### 1.2 Create Configuration System (Day 2)
**File**: `smart_split/core/config.py`

```python
"""Configuration management for SmartSplit library.

This module handles all configuration options and validation,
following the single responsibility principle for configuration management.
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Dict, Optional, Any, Union

from pydantic import BaseModel, Field, validator, root_validator


class LLMConfig(BaseModel):
    """Configuration for LLM interactions."""
    timeout: int = Field(default=60, ge=1, le=300, description="Request timeout in seconds")
    retry_attempts: int = Field(default=3, ge=1, le=10)
    retry_delay: float = Field(default=1.0, ge=0.1, le=10.0)
    rate_limit_delay: float = Field(default=1.0, ge=0.0, le=5.0)
    max_tokens: Optional[int] = Field(default=None, ge=1)
    temperature: float = Field(default=0.1, ge=0.0, le=2.0)


class ChunkingConfig(BaseModel):
    """Configuration for chunking behavior."""
    max_chunk_size: int = Field(default=100000, gt=0, description="Maximum characters per chunk")
    min_chunk_size: int = Field(default=100, gt=0, description="Minimum characters per chunk")
    preferred_chunk_size: int = Field(default=4000, gt=0, description="Target chunk size")
    overlap_tokens: int = Field(default=50, ge=0, description="Overlap between hierarchical chunks")
    
    @root_validator
    def validate_chunk_sizes(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        """Ensure chunk size constraints are logical."""
        min_size = values.get('min_chunk_size', 100)
        max_size = values.get('max_chunk_size', 100000)
        preferred_size = values.get('preferred_chunk_size', 4000)
        
        if min_size >= max_size:
            raise ValueError("min_chunk_size must be less than max_chunk_size")
        
        if preferred_size < min_size or preferred_size > max_size:
            raise ValueError("preferred_chunk_size must be between min and max chunk sizes")
        
        return values


class ProcessingConfig(BaseModel):
    """Configuration for document processing."""
    enable_hierarchical_splitting: bool = Field(default=True)
    validate_reconstruction: bool = Field(default=True)
    fail_on_reconstruction_error: bool = Field(default=True)
    fallback_to_character_split: bool = Field(default=False)
    preserve_whitespace: bool = Field(default=True)
    normalize_unicode: bool = Field(default=True)


class LoggingConfig(BaseModel):
    """Configuration for logging behavior."""
    level: str = Field(default="INFO", regex=r"^(DEBUG|INFO|WARNING|ERROR|CRITICAL)$")
    format: str = Field(default="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    file_path: Optional[Path] = None
    max_file_size: int = Field(default=10485760, gt=0)  # 10MB default
    backup_count: int = Field(default=5, ge=0)


class SplitterConfig(BaseModel):
    """Main configuration class for SmartSplitter.
    
    This class aggregates all configuration options and provides
    validation and default value management.
    """
    llm: LLMConfig = Field(default_factory=LLMConfig)
    chunking: ChunkingConfig = Field(default_factory=ChunkingConfig)
    processing: ProcessingConfig = Field(default_factory=ProcessingConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    
    # Global settings
    debug_mode: bool = Field(default=False)
    cache_enabled: bool = Field(default=True)
    cache_dir: Optional[Path] = Field(default=None)
    
    class Config:
        """Pydantic configuration."""
        validate_assignment = True
        extra = "forbid"
        
    @classmethod
    def from_file(cls, config_path: Union[str, Path]) -> SplitterConfig:
        """Load configuration from JSON or YAML file."""
        import json
        
        config_path = Path(config_path)
        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        
        with open(config_path, 'r', encoding='utf-8') as f:
            if config_path.suffix.lower() == '.json':
                data = json.load(f)
            else:
                raise ValueError(f"Unsupported configuration file format: {config_path.suffix}")
        
        return cls(**data)
    
    @classmethod
    def from_env(cls) -> SplitterConfig:
        """Load configuration from environment variables."""
        env_config = {}
        
        # Map environment variables to config structure
        env_mappings = {
            'SMARTSPLIT_LLM_TIMEOUT': ('llm', 'timeout'),
            'SMARTSPLIT_MAX_CHUNK_SIZE': ('chunking', 'max_chunk_size'),
            'SMARTSPLIT_MIN_CHUNK_SIZE': ('chunking', 'min_chunk_size'),
            'SMARTSPLIT_DEBUG': ('debug_mode',),
            'SMARTSPLIT_LOG_LEVEL': ('logging', 'level'),
        }
        
        for env_var, config_path in env_mappings.items():
            value = os.getenv(env_var)
            if value is not None:
                # Navigate nested config structure
                current = env_config
                for key in config_path[:-1]:
                    if key not in current:
                        current[key] = {}
                    current = current[key]
                
                # Convert value to appropriate type
                final_key = config_path[-1]
                if env_var in ['SMARTSPLIT_LLM_TIMEOUT', 'SMARTSPLIT_MAX_CHUNK_SIZE', 'SMARTSPLIT_MIN_CHUNK_SIZE']:
                    current[final_key] = int(value)
                elif env_var == 'SMARTSPLIT_DEBUG':
                    current[final_key] = value.lower() in ('true', '1', 'yes', 'on')
                else:
                    current[final_key] = value
        
        return cls(**env_config)
    
    def save_to_file(self, file_path: Union[str, Path]) -> None:
        """Save configuration to JSON file."""
        import json
        
        file_path = Path(file_path)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(self.dict(), f, indent=2, default=str)
```

#### 1.3 Create Exception Hierarchy (Day 3)
**File**: `smart_split/core/exceptions.py`

```python
"""Custom exceptions for SmartSplit library.

This module defines all custom exceptions used throughout the library,
following the single responsibility principle for error handling.
"""
from typing import Optional, List, Any


class SmartSplitError(Exception):
    """Base exception for all SmartSplit errors.
    
    All custom exceptions in the library inherit from this base class
    to provide consistent error handling and identification.
    """
    
    def __init__(self, message: str, details: Optional[dict] = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}
    
    def __str__(self) -> str:
        if self.details:
            return f"{self.message} | Details: {self.details}"
        return self.message


class ConfigurationError(SmartSplitError):
    """Raised when configuration is invalid or missing."""
    
    def __init__(self, message: str, config_field: Optional[str] = None):
        super().__init__(message, {"config_field": config_field})
        self.config_field = config_field


class DocumentProcessingError(SmartSplitError):
    """Raised when document processing fails."""
    
    def __init__(self, message: str, document_path: Optional[str] = None, format_type: Optional[str] = None):
        super().__init__(message, {
            "document_path": document_path,
            "format_type": format_type
        })
        self.document_path = document_path
        self.format_type = format_type


class LLMError(SmartSplitError):
    """Raised when LLM interaction fails."""
    
    def __init__(self, message: str, provider: Optional[str] = None, retry_count: int = 0):
        super().__init__(message, {
            "provider": provider,
            "retry_count": retry_count
        })
        self.provider = provider
        self.retry_count = retry_count


class LLMTimeoutError(LLMError):
    """Raised when LLM request times out."""
    pass


class LLMRateLimitError(LLMError):
    """Raised when LLM rate limit is exceeded."""
    
    def __init__(self, message: str, retry_after: Optional[int] = None, **kwargs):
        super().__init__(message, **kwargs)
        self.retry_after = retry_after


class LLMResponseError(LLMError):
    """Raised when LLM returns invalid or unparseable response."""
    
    def __init__(self, message: str, response_content: Optional[str] = None, **kwargs):
        super().__init__(message, **kwargs)
        self.response_content = response_content


class ReconstructionError(SmartSplitError):
    """Raised when chunk reconstruction fails."""
    
    def __init__(
        self, 
        message: str, 
        chunk_index: Optional[int] = None, 
        marker_text: Optional[str] = None,
        original_text_length: Optional[int] = None
    ):
        super().__init__(message, {
            "chunk_index": chunk_index,
            "marker_text": marker_text,
            "original_text_length": original_text_length
        })
        self.chunk_index = chunk_index
        self.marker_text = marker_text
        self.original_text_length = original_text_length


class MarkerNotFoundError(ReconstructionError):
    """Raised when chunk markers cannot be found in original text."""
    
    def __init__(self, marker_text: str, chunk_index: int, search_position: int = 0):
        message = f"Marker '{marker_text}' not found in text for chunk {chunk_index}"
        super().__init__(
            message, 
            chunk_index=chunk_index, 
            marker_text=marker_text
        )
        self.search_position = search_position


class ValidationError(SmartSplitError):
    """Raised when chunk validation fails."""
    
    def __init__(self, message: str, validation_errors: Optional[List[str]] = None):
        super().__init__(message, {"validation_errors": validation_errors or []})
        self.validation_errors = validation_errors or []


class StrategyError(SmartSplitError):
    """Raised when splitting strategy encounters an error."""
    
    def __init__(self, message: str, strategy_name: Optional[str] = None):
        super().__init__(message, {"strategy_name": strategy_name})
        self.strategy_name = strategy_name


class InvalidStrategyError(StrategyError):
    """Raised when an invalid or unknown strategy is specified."""
    
    def __init__(self, strategy_name: str, available_strategies: Optional[List[str]] = None):
        message = f"Unknown strategy: '{strategy_name}'"
        if available_strategies:
            message += f". Available strategies: {', '.join(available_strategies)}"
        super().__init__(message, strategy_name)
        self.available_strategies = available_strategies or []


class TextTooLargeError(SmartSplitError):
    """Raised when input text exceeds maximum processing limits."""
    
    def __init__(self, text_length: int, max_length: int):
        message = f"Text length ({text_length:,} chars) exceeds maximum limit ({max_length:,} chars)"
        super().__init__(message, {
            "text_length": text_length,
            "max_length": max_length
        })
        self.text_length = text_length
        self.max_length = max_length


class ChunkSizeError(SmartSplitError):
    """Raised when chunk size constraints are violated."""
    
    def __init__(self, chunk_size: int, min_size: int, max_size: int):
        message = f"Chunk size ({chunk_size}) outside valid range [{min_size}, {max_size}]"
        super().__init__(message, {
            "chunk_size": chunk_size,
            "min_size": min_size,
            "max_size": max_size
        })
        self.chunk_size = chunk_size
        self.min_size = min_size
        self.max_size = max_size
```

#### 1.4 Refactor Main Splitter Class (Days 4-5)
**File**: `smart_split/core/splitter.py`

```python
"""Main SmartSplitter class implementing the core chunking functionality.

This module contains the primary interface for the SmartSplit library,
following single responsibility principle for document chunking orchestration.
"""
from __future__ import annotations

import logging
import time
from pathlib import Path
from typing import List, Optional, Union

from langchain_core.language_models import BaseChatModel

from .config import SplitterConfig
from .exceptions import (
    ConfigurationError,
    DocumentProcessingError,
    SmartSplitError,
    TextTooLargeError
)
from .models import ChunkResult, ChunkMetadata, ValidationResult, SplittingStrategy
from ..llm import LLMAdapter
from ..processors import DocumentProcessor
from ..reconstruction import ReconstructionEngine
from ..strategies import StrategyManager
from ..utils.logging import setup_logger


class SmartSplitter:
    """Main interface for intelligent document chunking.
    
    This class orchestrates the entire chunking process by coordinating
    between different components while maintaining a simple public API.
    
    Example:
        >>> from smart_split import SmartSplitter
        >>> from langchain_openai import ChatOpenAI
        >>> 
        >>> llm = ChatOpenAI(model="gpt-3.5-turbo")
        >>> splitter = SmartSplitter(llm)
        >>> 
        >>> text = "Your large document text here..."
        >>> result = splitter.split(text, strategy="topic")
        >>> print(f"Created {len(result.chunks)} chunks")
    """
    
    def __init__(
        self, 
        llm: BaseChatModel, 
        config: Optional[SplitterConfig] = None
    ):
        """Initialize SmartSplitter with LLM and configuration.
        
        Args:
            llm: LangChain-compatible language model
            config: Optional configuration object. Uses defaults if not provided.
            
        Raises:
            ConfigurationError: If configuration is invalid
        """
        self.config = config or SplitterConfig()
        self.logger = setup_logger(__name__, self.config.logging)
        
        # Initialize components
        try:
            self.llm_adapter = LLMAdapter(llm, self.config.llm)
            self.strategy_manager = StrategyManager()
            self.document_processor = DocumentProcessor(self.config.processing)
            self.reconstruction_engine = ReconstructionEngine(self.config.processing)
            
            self.logger.info("SmartSplitter initialized successfully")
            
        except Exception as e:
            raise ConfigurationError(f"Failed to initialize SmartSplitter: {str(e)}") from e
    
    def split(
        self, 
        text: str, 
        strategy: str = SplittingStrategy.TOPIC, 
        criteria: Optional[str] = None
    ) -> ChunkResult:
        """Split text into semantic chunks.
        
        Args:
            text: Text to split into chunks
            strategy: Splitting strategy to use
            criteria: Custom splitting criteria (overrides strategy)
            
        Returns:
            ChunkResult containing chunks and metadata
            
        Raises:
            TextTooLargeError: If text exceeds maximum processing limits
            DocumentProcessingError: If text preprocessing fails
            SmartSplitError: For other processing errors
        """
        start_time = time.time()
        
        try:
            # Validate input
            self._validate_input(text, strategy)
            
            # Preprocess text
            processed_text = self.document_processor.preprocess_text(text)
            
            # Choose splitting approach based on text size
            if len(processed_text) > self.config.chunking.max_chunk_size:
                chunks = self._hierarchical_split(processed_text, strategy, criteria)
            else:
                chunks = self._direct_split(processed_text, strategy, criteria)
            
            # Create metadata
            processing_time = time.time() - start_time
            metadata = self._create_metadata(
                text, chunks, strategy, processing_time
            )
            
            # Validate results
            validation = self._validate_chunks(text, chunks)
            
            result = ChunkResult(
                chunks=chunks,
                metadata=metadata,
                markers=self.reconstruction_engine.last_markers,
                validation=validation
            )
            
            self.logger.info(
                f"Successfully split text into {len(chunks)} chunks "
                f"in {processing_time:.2f}s using '{strategy}' strategy"
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to split text: {str(e)}")
            if isinstance(e, SmartSplitError):
                raise
            raise SmartSplitError(f"Unexpected error during splitting: {str(e)}") from e
    
    def split_file(
        self, 
        file_path: Union[str, Path], 
        **kwargs
    ) -> ChunkResult:
        """Split document file into semantic chunks.
        
        Args:
            file_path: Path to document file
            **kwargs: Additional arguments passed to split()
            
        Returns:
            ChunkResult containing chunks and metadata
            
        Raises:
            DocumentProcessingError: If file cannot be loaded or processed
        """
        try:
            text, doc_format = self.document_processor.load_document(file_path)
            self.logger.info(f"Loaded {doc_format} document: {file_path}")
            
            return self.split(text, **kwargs)
            
        except Exception as e:
            raise DocumentProcessingError(
                f"Failed to process file {file_path}: {str(e)}",
                document_path=str(file_path)
            ) from e
    
    def _validate_input(self, text: str, strategy: str) -> None:
        """Validate input parameters."""
        if not text or not text.strip():
            raise DocumentProcessingError("Input text cannot be empty")
        
        # Check text size limits
        max_total_size = self.config.chunking.max_chunk_size * 100  # Reasonable upper limit
        if len(text) > max_total_size:
            raise TextTooLargeError(len(text), max_total_size)
        
        # Validate strategy
        if not self.strategy_manager.is_valid_strategy(strategy):
            available = self.strategy_manager.get_available_strategies()
            raise ConfigurationError(
                f"Invalid strategy '{strategy}'. Available: {available}"
            )
    
    def _direct_split(
        self, 
        text: str, 
        strategy: str, 
        criteria: Optional[str]
    ) -> List[str]:
        """Perform direct LLM-based splitting."""
        # Get strategy prompt
        prompt_template = self.strategy_manager.get_strategy_prompt(strategy, criteria)
        
        # Get LLM response
        markers = self.llm_adapter.get_chunk_markers(text, prompt_template)
        
        # Reconstruct chunks
        chunks = self.reconstruction_engine.reconstruct_chunks(text, markers)
        
        return chunks
    
    def _hierarchical_split(
        self, 
        text: str, 
        strategy: str, 
        criteria: Optional[str]
    ) -> List[str]:
        """Perform hierarchical splitting for large documents."""
        self.logger.info(f"Performing hierarchical split for {len(text):,} character document")
        
        # First pass: coarse splitting
        coarse_chunks = self.document_processor.coarse_split(
            text, self.config.chunking.max_chunk_size
        )
        
        # Second pass: semantic splitting of each coarse chunk
        final_chunks = []
        for i, coarse_chunk in enumerate(coarse_chunks):
            self.logger.debug(f"Processing coarse chunk {i+1}/{len(coarse_chunks)}")
            
            try:
                semantic_chunks = self._direct_split(coarse_chunk, strategy, criteria)
                final_chunks.extend(semantic_chunks)
            except Exception as e:
                self.logger.warning(f"Failed to split coarse chunk {i}: {e}")
                # Fallback to including the coarse chunk as-is
                final_chunks.append(coarse_chunk)
        
        return final_chunks
    
    def _create_metadata(
        self, 
        original_text: str, 
        chunks: List[str], 
        strategy: str, 
        processing_time: float
    ) -> ChunkMetadata:
        """Create metadata for the chunking result."""
        total_reconstructed = sum(len(chunk) for chunk in chunks)
        
        return ChunkMetadata(
            total_chunks=len(chunks),
            original_length=len(original_text),
            total_reconstructed_length=total_reconstructed,
            strategy_used=strategy,
            processing_time=processing_time,
            llm_calls=self.llm_adapter.call_count
        )
    
    def _validate_chunks(self, original_text: str, chunks: List[str]) -> ValidationResult:
        """Validate that chunks maintain text integrity."""
        if not self.config.processing.validate_reconstruction:
            return ValidationResult(is_valid=True)
        
        return self.reconstruction_engine.validate_reconstruction(original_text, chunks)
    
    @property
    def available_strategies(self) -> List[str]:
        """Get list of available splitting strategies."""
        return self.strategy_manager.get_available_strategies()
    
    def get_strategy_description(self, strategy: str) -> str:
        """Get description of a splitting strategy."""
        return self.strategy_manager.get_strategy_description(strategy)
```

### Phase 2: Component Implementation (Weeks 3-4)

#### 2.1 Implement Strategy Management (Days 6-8)
**File**: `smart_split/strategies/manager.py`

```python
"""Strategy management for different splitting approaches.

This module handles the registration, validation, and execution of
splitting strategies, following single responsibility principle.
"""
from __future__ import annotations

from typing import Dict, List, Optional

from langchain_core.prompts import PromptTemplate

from .base import BaseStrategy
from .predefined import (
    TopicStrategy,
    PageStrategy, 
    QuestionAnswerStrategy,
    NarrativeSceneStrategy,
    SectionStrategy,
    ParagraphStrategy
)
from .custom import CustomStrategy
from .prompts import PromptTemplates
from ..core.exceptions import InvalidStrategyError, StrategyError
from ..core.models import SplittingStrategy


class StrategyManager:
    """Manages splitting strategies and their execution.
    
    This class provides a central registry for splitting strategies
    and handles their instantiation and validation.
    """
    
    def __init__(self):
        self._strategies: Dict[str, BaseStrategy] = {}
        self._register_predefined_strategies()
    
    def _register_predefined_strategies(self) -> None:
        """Register all predefined strategies."""
        predefined = [
            TopicStrategy(),
            PageStrategy(),
            QuestionAnswerStrategy(), 
            NarrativeSceneStrategy(),
            SectionStrategy(),
            ParagraphStrategy()
        ]
        
        for strategy in predefined:
            self._strategies[strategy.name] = strategy
    
    def get_strategy_prompt(
        self, 
        strategy_name: str, 
        custom_criteria: Optional[str] = None
    ) -> PromptTemplate:
        """Get prompt template for a strategy.
        
        Args:
            strategy_name: Name of the strategy
            custom_criteria: Custom criteria to override strategy
            
        Returns:
            PromptTemplate for the strategy
            
        Raises:
            InvalidStrategyError: If strategy is not found
        """
        if custom_criteria:
            custom_strategy = CustomStrategy(custom_criteria)
            return custom_strategy.get_prompt_template()
        
        if strategy_name not in self._strategies:
            raise InvalidStrategyError(
                strategy_name, 
                list(self._strategies.keys())
            )
        
        return self._strategies[strategy_name].get_prompt_template()
    
    def is_valid_strategy(self, strategy_name: str) -> bool:
        """Check if strategy name is valid."""
        return strategy_name in self._strategies
    
    def get_available_strategies(self) -> List[str]:
        """Get list of available strategy names."""
        return list(self._strategies.keys())
    
    def get_strategy_description(self, strategy_name: str) -> str:
        """Get description of a strategy."""
        if strategy_name not in self._strategies:
            raise InvalidStrategyError(strategy_name, list(self._strategies.keys()))
        
        return self._strategies[strategy_name].description
    
    def register_strategy(self, strategy: BaseStrategy) -> None:
        """Register a custom strategy.
        
        Args:
            strategy: Strategy instance to register
            
        Raises:
            StrategyError: If strategy is invalid
        """
        if not isinstance(strategy, BaseStrategy):
            raise StrategyError("Strategy must inherit from BaseStrategy")
        
        if not strategy.name:
            raise StrategyError("Strategy must have a non-empty name")
        
        self._strategies[strategy.name] = strategy
```

#### 2.2 Implement Reconstruction Engine (Days 9-11)

This would continue with the detailed implementation of each component...

## Key Implementation Principles

### 1. Single Responsibility Principle
- Each class has one reason to change
- Clear separation of concerns between modules
- Focused interfaces with minimal dependencies

### 2. PEP8 Compliance
- Proper naming conventions (snake_case for functions/variables, PascalCase for classes)
- Appropriate line length and formatting
- Comprehensive docstrings following Google/NumPy style
- Type hints for all public interfaces

### 3. Error Handling Strategy
- Custom exception hierarchy for different error types
- Graceful degradation where possible
- Comprehensive logging for debugging
- Clear error messages with actionable suggestions

### 4. Testing Strategy
- Unit tests for each component with >90% coverage
- Integration tests with real LLM providers
- Performance benchmarks for large documents
- Error scenario testing

### 5. Documentation Requirements
- Comprehensive API documentation
- Usage examples for common scenarios
- Architecture documentation
- Contributing guidelines

This implementation plan transforms the current monolithic code into a professional, maintainable library suitable for production use while maintaining the core functionality and improving extensibility.
