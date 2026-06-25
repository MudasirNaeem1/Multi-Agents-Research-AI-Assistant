from langchain.tools import tool
import requests
from dotenv import load_dotenv
from ddgs import DDGS
from rich import print
from bs4 import BeautifulSoup
from readability import Document
import trafilatura
import re

load_dotenv()


# ── Tool 1 — Web Search via DuckDuckGo ───────────────────────────────────────
# FIX: Removed return_direct=True — it was short-circuiting the ReAct agent
#      and preventing it from reasoning about results.
# FIX: Increased max_results from 5 to 10 for broader coverage.
# FIX: Output now clearly labels each result with an index so the reader
#      agent can reference them easily.

@tool("web_search")
def web_search(query: str) -> str:
    """Search the web for recent and reliable information on a topic.
    Returns titles, URLs and snippets for up to 10 results. No API key required."""
    try:
        output = []
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=10, timeout=10))

        if not results:
            return "No results found. Try a different query."

        for i, r in enumerate(results, 1):
            title   = r.get("title",  "No title")
            url     = r.get("href",   "No URL")
            snippet = r.get("body",   "No content available")
            output.append(f"[{i}] Title: {title}\n    URL: {url}\n    Snippet: {snippet}\n")

        return "\n".join(output)

    except Exception as e:
        return f"Search failed: {str(e)}"


# ── Tool 2 — URL Scraper ──────────────────────────────────────────────────────

@tool("scrape_url")
def scrape_url(url: str) -> str:
    """Scrape and extract clean readable text content from a given URL.
    Input must be a valid URL string starting with http or https."""
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0 Safari/537.36"
        ),
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.google.com/",
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        html = response.text

        # Strategy 1 → trafilatura (best for articles/blogs)
        extracted = trafilatura.extract(html, include_comments=False, include_tables=False)
        if extracted and len(extracted) > 200:
            cleaned = re.sub(r'\s+', ' ', extracted).strip()
            return f"[Scraped from: {url}]\n\n{cleaned[:5000]}"

        # Strategy 2 → readability
        doc = Document(html)
        content = doc.summary()
        soup = BeautifulSoup(content, "html.parser")
        for tag in soup.find_all(['script', 'style', 'header', 'footer', 'nav', 'aside']):
            tag.decompose()
        text = soup.get_text(separator=' ', strip=True)
        if text and len(text.strip()) > 200:
            cleaned = re.sub(r'\s+', ' ', text)
            return f"[Scraped from: {url}]\n\n{cleaned[:5000]}"

        # Strategy 3 → full-page fallback
        soup = BeautifulSoup(html, "html.parser")
        for tag in soup(["script", "style", "nav", "footer", "header", "aside", "form"]):
            tag.decompose()
        text = soup.get_text(separator=" ", strip=True)
        cleaned = re.sub(r'\s+', ' ', text)
        if cleaned:
            return f"[Scraped from: {url}]\n\n{cleaned[:5000]}"

        return f"Could not extract meaningful content from: {url}"

    except requests.exceptions.Timeout:
        return f"Request timed out while scraping: {url}"

    except requests.exceptions.HTTPError as e:
        return f"HTTP error for {url}: {str(e)}"

    except Exception as e:
        return f"Could not scrape {url}: {str(e)}"