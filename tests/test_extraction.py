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


def test_hybrid_extract_uses_trafilatura_first():
    """Hybrid should try trafilatura before playwright."""
    from interdeep.extraction.hybrid import extract_hybrid

    html = "<html><body><article><p>Simple content here that is long enough to pass the minimum content length threshold for hybrid extraction.</p><p>Adding more content to ensure we exceed the 200 character minimum requirement for the extraction to be considered successful.</p></article></body></html>"
    result = extract_hybrid(html=html, url="https://example.com")
    assert result.method == "trafilatura"
    assert result.content_length > 0


def test_hybrid_extract_no_input():
    """Hybrid with no url or html should return failed."""
    from interdeep.extraction.hybrid import extract_hybrid

    result = extract_hybrid()
    assert result.method == "failed"


def test_extract_batch_async():
    """Batch extraction should return results for each URL."""
    import asyncio
    from unittest.mock import patch as mock_patch
    from interdeep.extraction.hybrid import extract_batch_async

    async def mock_extract(url="", html="", timeout=10):
        return ExtractionResult(url=url, content="x" * 300, method="trafilatura")

    with mock_patch("interdeep.extraction.hybrid.extract_hybrid_async", side_effect=mock_extract):
        results = asyncio.run(extract_batch_async(["https://a.com", "https://b.com"]))
        assert len(results) == 2
        assert all(r.method == "trafilatura" for r in results)


def test_playwright_is_available():
    """playwright_ext.is_available() should return a boolean."""
    from interdeep.extraction.playwright_ext import is_available
    assert isinstance(is_available(), bool)
