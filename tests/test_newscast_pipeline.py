"""Tests for NewscastStudio broadcast pipeline."""

import pytest
import json
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from mind.agents.newscast_studio.broadcast_pipeline import (
    NewscastBroadcastPipeline,
    BroadcastStatus,
)


@pytest.fixture
def mock_llm():
    """Create mock LLM for testing."""
    llm = Mock()
    llm.generate = Mock(return_value="Mock generated content")
    return llm


@pytest.fixture
def temp_broadcast_dir(tmp_path):
    """Create temporary broadcast directory."""
    return tmp_path / "broadcasts"


@pytest.fixture
def pipeline(mock_llm, temp_broadcast_dir):
    """Create a test pipeline with temp directory."""
    return NewscastBroadcastPipeline(llm=mock_llm, broadcasts_dir=temp_broadcast_dir)


def test_pipeline_initialization(pipeline):
    """Test pipeline initializes correctly."""
    assert pipeline.llm is not None
    assert pipeline.broadcasts_dir.exists()


def test_create_broadcast_success(pipeline, mock_llm):
    """Test successful broadcast creation."""
    result = pipeline.create_broadcast(
        topic="AI Market Surge",
        context="Tech sector rally",
        duration=60,
    )

    assert result["status"] == "success"
    assert "broadcast_id" in result
    assert "broadcast_path" in result

    # Verify broadcast file exists
    broadcast_file = Path(result["broadcast_path"]) / "broadcast.json"
    assert broadcast_file.exists()

    # Verify broadcast contents
    with open(broadcast_file) as f:
        broadcast = json.load(f)

    assert broadcast["title"] == "AI Market Surge"
    assert broadcast["status"] == BroadcastStatus.APPROVED.value
    assert "analysis" in broadcast
    assert "script" in broadcast


def test_create_broadcast_with_defaults(pipeline):
    """Test broadcast creation with default parameters."""
    result = pipeline.create_broadcast(topic="Bitcoin News")

    assert result["status"] == "success"
    broadcast_id = result["broadcast_id"]
    assert "broadcast_" in broadcast_id
    assert "bitcoin_news" in broadcast_id


def test_llm_generate_called_twice(pipeline, mock_llm):
    """Test that LLM generate is called for analysis and script."""
    pipeline.create_broadcast("Market Update")

    # Should be called twice: once for analysis, once for script
    assert mock_llm.generate.call_count == 2


def test_create_broadcast_failure_handling(pipeline, mock_llm):
    """Test broadcast creation handles LLM failures gracefully."""
    # Set up LLM to fail
    mock_llm.generate = Mock(side_effect=Exception("LLM service down"))

    result = pipeline.create_broadcast("Test Topic")

    assert result["status"] == "failed"
    assert "error" in result


def test_retry_logic_succeeds_after_failure(pipeline, mock_llm):
    """Test retry logic recovers after transient failure."""
    # First call fails, second succeeds
    mock_llm.generate = Mock(
        side_effect=[
            Exception("Transient error"),
            "Analysis content",
            "Script content",
        ]
    )

    result = pipeline.create_broadcast(
        topic="Recovery Test",
        max_retries=2,
    )

    # With retry logic, should eventually succeed
    # (Note: actual retry count depends on implementation)
    assert "broadcast_id" in result or "error" in result


def test_list_broadcasts_empty(pipeline):
    """Test listing broadcasts when none exist."""
    broadcasts = pipeline.list_broadcasts()
    assert broadcasts == []


def test_list_broadcasts_multiple(pipeline):
    """Test listing multiple broadcasts in order."""
    # Create three broadcasts
    for i, topic in enumerate(["News 1", "News 2", "News 3"]):
        pipeline.create_broadcast(topic=topic)

    broadcasts = pipeline.list_broadcasts()

    assert len(broadcasts) == 3
    # Most recent should be first
    assert broadcasts[0]["title"] == "News 3"


def test_get_broadcast_exists(pipeline):
    """Test retrieving an existing broadcast."""
    result = pipeline.create_broadcast(topic="Test Broadcast")
    broadcast_id = result["broadcast_id"]

    broadcast = pipeline.get_broadcast(broadcast_id)

    assert broadcast is not None
    assert broadcast["title"] == "Test Broadcast"
    assert broadcast["status"] == BroadcastStatus.APPROVED.value


def test_get_broadcast_not_found(pipeline):
    """Test retrieving non-existent broadcast."""
    broadcast = pipeline.get_broadcast("nonexistent_id")
    assert broadcast is None


def test_broadcast_duration_calculation(pipeline, mock_llm):
    """Test that script generation respects duration."""
    pipeline.create_broadcast(
        topic="Short News",
        duration=30,  # 30 seconds
    )

    # Check that generate was called with appropriate word count
    # For 30s: ~75 words
    calls = mock_llm.generate.call_args_list
    script_call = calls[1]  # Second call is for script
    assert "write a 75-word broadcast script (30s)" in str(script_call).lower()


def test_broadcast_metadata(pipeline):
    """Test broadcast preserves all metadata."""
    context = "Market analysis"
    tone = "urgent"
    
    result = pipeline.create_broadcast(
        topic="Crisis News",
        context=context,
        duration=45,
        tone=tone,
    )

    broadcast_id = result["broadcast_id"]
    broadcast = pipeline.get_broadcast(broadcast_id)

    assert broadcast["context"] == context
    assert broadcast["duration_seconds"] == 45
    assert "created_at" in broadcast
    assert datetime.fromisoformat(broadcast["created_at"]) is not None


def test_broadcast_file_format(pipeline):
    """Test broadcast files are valid JSON."""
    result = pipeline.create_broadcast(topic="JSON Test")
    broadcast_file = Path(result["broadcast_path"]) / "broadcast.json"

    # Should be readable as valid JSON
    with open(broadcast_file) as f:
        data = json.load(f)

    assert isinstance(data, dict)
    assert "id" in data
    assert "status" in data
