import pytest
from unittest.mock import MagicMock
from ..splitter import SmartSplitter, Chunk, ChunkList

@pytest.fixture
def mock_llm():
    return MagicMock()

def test_split_basic(mock_llm):
    # Arrange
    text = "This is the first sentence. This is the second sentence."
    strategy = 'topic'

    mock_response = {
        "chunks": [
            {"chunk_index": 0, "start_chunk": "This is the first", "end_chunk": "first sentence.", "summary_chunk": "First part"},
            {"chunk_index": 1, "start_chunk": "This is the second", "end_chunk": "second sentence.", "summary_chunk": "Second part"}
        ]
    }
    mock_llm.invoke.return_value = mock_response

    splitter = SmartSplitter(llm=mock_llm)

    # Act
    chunks = splitter.split(text, strategy=strategy)

    # Assert
    assert len(chunks) == 2
    assert chunks[0] == "This is the first sentence."
    assert chunks[1] == " This is the second sentence."
    mock_llm.invoke.assert_called_once()

def test_custom_segmentation(mock_llm):
    # Arrange
    text = "A; B"
    custom_criteria = "Split by semicolon"

    mock_response = {
        "chunks": [
            {"chunk_index": 0, "start_chunk": "A", "end_chunk": "A", "summary_chunk": "A"},
            {"chunk_index": 1, "start_chunk": "B", "end_chunk": "B", "summary_chunk": "B"}
        ]
    }
    mock_llm.invoke.return_value = mock_response

    splitter = SmartSplitter(llm=mock_llm)

    # Act
    chunks = splitter.split(text, segmentation_criteria=custom_criteria)

    # Assert
    assert len(chunks) == 2
    assert chunks[0] == "A"
    assert chunks[1] == "; B"

    # Check that the custom criteria were passed to the prompt
    called_with_args = mock_llm.invoke.call_args[0][0]
    assert called_with_args['segmentation_criteria'] == custom_criteria

def test_unknown_strategy(mock_llm):
    # Arrange
    text = "Some text"
    strategy = "unknown_strategy"
    splitter = SmartSplitter(llm=mock_llm)

    # Act & Assert
    with pytest.raises(ValueError):
        splitter.split(text, strategy=strategy)

def test_reconstruction_error(mock_llm):
    # Arrange
    text = "This is a test."
    mock_response = {
        "chunks": [
            {"chunk_index": 0, "start_chunk": "This is", "end_chunk": "not in text", "summary_chunk": "summary"}
        ]
    }
    mock_llm.invoke.return_value = mock_response
    splitter = SmartSplitter(llm=mock_llm)

    # Act & Assert
    with pytest.raises(ValueError):
        splitter.split(text, strategy='topic')

def test_hierarchical_split(mock_llm):
    # Arrange
    text = "A" * 20000  # Exceeds max_chunk_size
    splitter = SmartSplitter(llm=mock_llm, max_chunk_size=10000)

    # Mock response for each super-chunk
    mock_response_1 = {
        "chunks": [{"chunk_index": 0, "start_chunk": "A" * 10, "end_chunk": "A" * 10, "summary_chunk": "Part 1"}]
    }
    mock_response_2 = {
        "chunks": [{"chunk_index": 0, "start_chunk": "A" * 10, "end_chunk": "A" * 10, "summary_chunk": "Part 2"}]
    }
    mock_llm.invoke.side_effect = [mock_response_1, mock_response_2]

    # Act
    chunks = splitter.split(text, strategy='topic')

    # Assert
    assert mock_llm.invoke.call_count == 2
    # This is a simplified check; a real test would verify chunk content
    assert len(chunks) == 2
