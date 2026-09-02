from langchain.tools import tool
from dotenv import load_dotenv
import requests
from langchain_tavily import TavilySearch
from bs4 import BeautifulSoup
from readability import Document

load_dotenv()


tavily_tool = TavilySearch(max_results=5)

#creating the search Agent
@tool
def web_search(query: str) -> str:
    """A web search tool that finds latest information with titles, URLs and snippets."""

    results = tavily_tool.invoke(query)

    output = []

    for o in results.get("results", []):
        output.append(
            f"Title: {o.get('title')}\n"
            f"URL: {o.get('url')}\n"
            f"Snippet: {o.get('content', '')[:300]}\n"
        )

    return "\n".join(output) if output else "No results found"


# web scraper tool using beautifulSopu
@tool
def scrape_website(url: str) -> str:
    """Scrape the main text content from a website URL using BeautifulSoup."""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "lxml")

        # Remove unwanted elements
        for tag in soup(["script", "style", "noscript", "header", "footer", "nav"]):
            tag.decompose()

        # Get text
        text = soup.get_text(separator="\n", strip=True)

        # Clean up extra empty lines
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        clean_text = "\n".join(lines)

        return clean_text[:4000] if clean_text else "No content found."

    except Exception as e:
        return f"Error scraping the website: {str(e)}"