"""Hybrid extraction router — trafilatura fast path, Playwright fallback."""

import asyncio
import logging
from .models import ExtractionResult
from .trafilatura_ext import extract_with_trafilatura, extract_from_html
from . import playwright_ext

logger = logging.getLogger("interdeep.extraction")

MIN_CONTENT_LENGTH = 200  # below this, try playwright fallback


def extract_hybrid(url: str = "", html: str = "", timeout: int = 10) -> ExtractionResult:
    """Extract content using trafilatura first, Playwright fallback if needed."""
    if html:
        result = extract_from_html(html, url=url)
        if result.content_length >= MIN_CONTENT_LENGTH:
            return result
    elif url:
        result = extract_with_trafilatura(url, timeout=timeout)
        if result.content_length >= MIN_CONTENT_LENGTH:
            return result
    else:
        return ExtractionResult(url="", content="", method="failed",
                                metadata={"error": "no url or html provided"})

    if url and playwright_ext.is_available():
        logger.info("trafilatura insufficient (%d chars), falling back to Playwright: %s",
                     result.content_length, url)
        try:
            pw_result = asyncio.run(playwright_ext.extract_with_playwright(url, timeout=timeout * 1000))
            if pw_result.content_length > result.content_length:
                return pw_result
        except Exception as e:
            logger.warning("Playwright fallback failed: %s", e)

    return result


async def extract_hybrid_async(url: str = "", html: str = "",
                                timeout: int = 10) -> ExtractionResult:
    """Async version of extract_hybrid."""
    if html:
        result = extract_from_html(html, url=url)
        if result.content_length >= MIN_CONTENT_LENGTH:
            return result
    elif url:
        result = extract_with_trafilatura(url, timeout=timeout)
        if result.content_length >= MIN_CONTENT_LENGTH:
            return result
    else:
        return ExtractionResult(url="", content="", method="failed",
                                metadata={"error": "no url or html provided"})

    if url and playwright_ext.is_available():
        logger.info("trafilatura insufficient, falling back to Playwright: %s", url)
        pw_result = await playwright_ext.extract_with_playwright(url, timeout=timeout * 1000)
        if pw_result.content_length > result.content_length:
            return pw_result

    return result


async def extract_batch_async(urls: list[str], max_concurrent: int = 5) -> list[ExtractionResult]:
    """Extract content from multiple URLs concurrently."""
    semaphore = asyncio.Semaphore(max_concurrent)

    async def _extract(url: str) -> ExtractionResult:
        async with semaphore:
            return await extract_hybrid_async(url=url)

    return await asyncio.gather(*[_extract(url) for url in urls])
