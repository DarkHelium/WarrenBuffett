#!/usr/bin/env python3
"""
buffett_transcript_fetcher.py

Fetch Warren Buffett interview / lecture transcripts (HTML or PDF) and save each
as a cleaned .txt file for downstream knowledge-graph ingestion.

Requirements:
    pip install requests beautifulsoup4 pdfminer.six lxml

Usage:
    python buffett_transcript_fetcher.py

You can adapt the TRANSCRIPT_URLS list or pass a text file of URLs.
"""

import os
import re
import time
import json
import pathlib
import logging
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup

# PDF parsing
from io import BytesIO
from pdfminer.high_level import extract_text as pdf_extract_text

# ---------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------
OUTPUT_DIR = pathlib.Path("transcripts_raw")
OUTPUT_DIR.mkdir(exist_ok=True)

USER_AGENT = (
    "Mozilla/5.0 (compatible; BuffettTranscriptBot/1.0; +https://example.com/contact)"
)

# Seed list: mix of HTML + PDF transcripts (replace / extend as needed)
TRANSCRIPT_URLS = [
    # Annual meeting transcripts / mirrors
    "https://steadycompounding.com/transcript/brk-2025/",
    "https://steadycompounding.com/transcript/brk-2024/",
    "https://www.good-investing.net/2025/05/17/berkshire-hathaway-annual-meeting-2025-transcript/",
    "https://www.good-investing.net/2025/04/20/warren-buffett-berkshires-2024-annual-shareholder-meeting/",
    "https://www.good-investing.net/2025/04/22/berkshire-hathaway-annual-meeting-2024-transcript-afternoon-session/",
    "https://www.reddit.com/r/ValueInvesting/comments/1cs1ugw/2024_berkshire_annual_meeting_full_transcript_pdf/",
    "https://buffett.cnbc.com/2022-berkshire-hathaway-annual-meeting/",
    "https://www.gurufocus.com/news/2238063/berkshire-hathaway-inc-annual-shareholders-meeting-transcript",
    "https://berkshire.memorex.ai/",

    # University lecture
    "https://tilsonfunds.com/BuffettUofFloridaspeech.pdf",

    # Government / FCIC interview
    "https://fraser.stlouisfed.org/files/docs/historical/fct/fcic/fcic_interview_buffett_20100526.pdf",
    "https://elischolar.library.yale.edu/ypfs-documents/5982/",

    # Charlie Rose & other media interviews
    "https://charlierose.com/videos/22046",
    "https://charlierose.com/episodes/31221",
    "https://charlierose.com/videos/29774",
    "https://www.rbcpa.com/warren-e-buffett/charlie-rose-interview-with-warren-buffett-on-november-13-2009/",
    "https://www.kingswell.io/p/warren-buffett-q-and-a-transcript-30a",

    # Additional annual meeting mirrors / summaries
    "https://www.granitefirm.com/blog/us/2025/05/04/2025-berkshire-shareholder-meeting/",
    "https://videotobe.com/blog/transcript-of-berkshire-hathaway-2025-annual-meeting-warren-buffett",

    # 2023 meeting (partial transcript)
    "https://azjadelana.medium.com/berkshires-2023-annual-shareholder-meeting-transcript-q-a-part-1-531f714aca4e",
]

REQUEST_TIMEOUT = 30
SLEEP_SECONDS = 2  # polite delay between requests

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s"
)

# ---------------------------------------------------------------------
# Utility functions
# ---------------------------------------------------------------------
def slugify(text: str) -> str:
    text = re.sub(r"[^\w\s-]", "", text).strip().lower()
    return re.sub(r"[-\s]+", "-", text)


def fetch(url: str) -> requests.Response:
    headers = {"User-Agent": USER_AGENT}
    resp = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
    resp.raise_for_status()
    return resp


def is_pdf(response: requests.Response, url: str) -> bool:
    ctype = response.headers.get("Content-Type", "").lower()
    return "application/pdf" in ctype or url.lower().endswith(".pdf")


def clean_whitespace(text: str) -> str:
    text = re.sub(r"\r", "\n", text)
    text = re.sub(r"\n{2,}", "\n\n", text)  # collapse big gaps
    text = re.sub(r"[ \t]+", " ", text)
    return text.strip()


def normalize_speakers(text: str) -> str:
    """
    Convert SPEAKER NAMES IN ALL CAPS to Title Case for readability.
    e.g., 'WARREN BUFFETT:' -> 'Warren Buffett:'
    """
    def repl(match):
        name = match.group(1)
        return f"{name.title()}:"
    return re.sub(r"\b([A-Z][A-Z \.-]{2,})\s*:", repl, text)


# ---------------------------------------------------------------------
# Domain-specific cleaning
# ---------------------------------------------------------------------
def extract_from_html(url: str, html: str) -> str:
    soup = BeautifulSoup(html, "lxml")

    # Remove scripts/styles/nav
    for tag in soup(["script", "style", "noscript", "header", "footer", "aside"]):
        tag.decompose()

    text = ""

    domain = urlparse(url).netloc

    # Known site heuristics
    if "steadycompounding.com" in domain:
        # Transcript inside article
        article = soup.find("article") or soup
        text = article.get_text(separator="\n")
    elif "charlierose.com" in domain:
        # Transcript text usually under a div with class 'transcript' or similar
        trans = soup.find(class_=re.compile("transcript", re.I))
        text = trans.get_text(separator="\n") if trans else soup.get_text("\n")
    elif "kingswell.io" in domain:
        # Ghost/Newsletter platform
        article = soup.find("article") or soup
        text = article.get_text("\n")
    elif "fraser.stlouisfed.org" in domain:
        # Some transcripts have HTML landing page (PDF handled separately)
        main = soup.find("main") or soup
        text = main.get_text("\n")
    else:
        # Fallback: grab main body
        main = soup.find("article") or soup.find("main") or soup.body or soup
        text = main.get_text("\n")

    # Basic cleanup
    text = re.sub(r"\n{3,}", "\n\n", text)
    # Remove cookie / share clutter
    text = re.sub(r"(?i)subscribe|share this post.*", "", text)
    return text.strip()


def extract_from_pdf(raw: bytes) -> str:
    return pdf_extract_text(BytesIO(raw))


def post_process(text: str) -> str:
    text = clean_whitespace(text)
    text = normalize_speakers(text)
    return text


def save_text(url: str, text: str):
    # Derive filename from URL + first words
    parsed = urlparse(url)
    base = slugify(parsed.path.strip("/") or parsed.netloc)
    if not base:
        base = slugify(parsed.netloc)
    fname = f"{base or 'transcript'}.txt"
    out_path = OUTPUT_DIR / fname
    with out_path.open("w", encoding="utf-8") as f:
        f.write(f"Source URL: {url}\n\n{text}")
    logging.info("Saved %s (%d chars)", out_path, len(text))


# ---------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------
def process_url(url: str):
    try:
        logging.info("Fetching %s", url)
        resp = fetch(url)
        if is_pdf(resp, url):
            logging.info("Parsing PDF...")
            raw_text = extract_from_pdf(resp.content)
        else:
            raw_text = extract_from_html(url, resp.text)
        cleaned = post_process(raw_text)
        if len(cleaned) < 200:
            logging.warning("Very short transcript (%d chars) for %s", len(cleaned), url)
        save_text(url, cleaned)
    except Exception as e:
        logging.error("Failed %s: %s", url, e)


def main():
    for url in TRANSCRIPT_URLS:
        process_url(url)
        time.sleep(SLEEP_SECONDS)


if __name__ == "__main__":
    main()
