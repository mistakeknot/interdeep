"""Tests for content extraction layer."""

from unittest.mock import patch

import pytest
from interdeep.extraction.trafilatura_ext import extract_with_trafilatura, extract_from_html
from interdeep.extraction.models import ExtractionResult

SAMPLE_HTML = """
<html><body>
<article><h1>Test Title</h1><p>This is the main content of the article.</p></article>
<footer>Copyright 2026</footer>
</body></html>
"""


def test_extract_with_trafilatura_returns_result():
    """Extraction should return an ExtractionResult with method=trafilatura on success."""
    with patch("trafilatura.fetch_url", return_value=SAMPLE_HTML):
        result = extract_with_trafilatura("https://example.com")
    assert isinstance(result, ExtractionResult)
    assert result.url == "https://example.com"
    assert result.method == "trafilatura"
    assert result.content_length > 0


def test_extract_with_trafilatura_fetch_failure():
    """When fetch returns None, result should be failed."""
    with patch("trafilatura.fetch_url", return_value=None):
        result = extract_with_trafilatura("https://unreachable.invalid")
    assert isinstance(result, ExtractionResult)
    assert result.method == "failed"
    assert result.metadata.get("error") == "fetch returned None"


def test_extract_with_trafilatura_empty_url():
    """Empty URL should return a failed result."""
    result = extract_with_trafilatura("")
    assert result.method == "failed"
    assert result.content == ""


def test_extract_from_html():
    """Direct HTML extraction should work without network."""
    result = extract_from_html(SAMPLE_HTML, url="https://example.com/test")
    assert result.content_length > 0
    assert "main content" in result.content
    assert result.method == "trafilatura"


def test_extract_from_html_empty():
    """Empty HTML should return a failed result."""
    result = extract_from_html("", url="https://example.com/empty")
    assert result.method == "failed"


def test_extraction_result_content_length():
    """ExtractionResult should auto-compute content_length."""
    result = ExtractionResult(url="https://example.com", content="hello world")
    assert result.content_length == 11
