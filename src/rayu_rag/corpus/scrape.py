import json
import re
import time
from collections import deque
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urldefrag, urljoin, urlparse
from urllib.robotparser import RobotFileParser

import httpx
from bs4 import BeautifulSoup
from markdownify import markdownify as md

START_URL = "[https://rayucode.com/docs](https://rayucode.com/docs)"
ALLOWED_NETLOC = "rayucode.com"
ALLOWED_PATH_PREFIX = "/docs"
DOCS_DIR = Path("data/docs")
SOURCES_META_PATH = Path("data/scrape_sources.json")
USER_AGENT = "CADT-IR-RAG-Crawler/1.0"


def get_robot_parser(start_url: str) -> RobotFileParser:
    rp = RobotFileParser()
    rp.set_url(urljoin(start_url, "/robots.txt"))
    try:
        rp.read()
    except Exception:
        pass
    return rp


def normalize_docs_url(base: str, href: str) -> str | None:
    resolved = urljoin(base, href)
    clean_url, _ = urldefrag(resolved)
    parsed = urlparse(clean_url)

    if parsed.scheme not in ("http", "https"):
        return None
    if parsed.netloc != ALLOWED_NETLOC:
        return None

    # Restrict strictly to /docs and /docs/...
    path = parsed.path.rstrip("/")
    if path != ALLOWED_PATH_PREFIX and not path.startswith(f"{ALLOWED_PATH_PREFIX}/"):
        return None

    return f"{parsed.scheme}://{parsed.netloc}{path}"


def url_to_filename(url: str) -> str:
    """Convert [https://rayucode.com/docs/getting-started](https://rayucode.com/docs/getting-started) -> getting-started.md"""
    path = urlparse(url).path.rstrip("/")
    rel = path[len(ALLOWED_PATH_PREFIX):].strip("/")
    slug = rel.replace("/", "_") if rel else "index"
    slug = re.sub(r"[^a-zA-Z0-9_-]+", "-", slug).strip("-") or "index"
    return f"{slug}.md"


def extract_clean_markdown(html: str, url: str) -> str:
    soup = BeautifulSoup(html, "html.parser")

    # Strip navigation, sidebars, footers, scripts
    for tag in soup(["nav", "footer", "header", "aside", "script", "style"]):
        tag.decompose()

    main = soup.find("article") or soup.find("main") or soup.body
    if not main:
        return ""

    # Ensure there is a top-level H1 for chunker.py
    h1 = main.find("h1") or soup.find("h1")
    h1_text = h1.get_text(" ", strip=True) if h1 else ""

    raw_md = md(
        str(main),
        heading_style="ATX",
        code_language_callback=lambda el: (
            el.get("class")[0].replace("language-", "")
            if el.get("class") and el.get("class")[0].startswith("language-")
            else ""
        ),
    )

    # Normalize trailing whitespace and collapse 3+ newlines into 2
    lines = [line.rstrip() for line in raw_md.splitlines()]
    body = re.sub(r"\n{3,}", "\n\n", "\n".join(lines)).strip()

    if h1_text and not body.startswith("# "):
        body = f"# {h1_text}\n\n{body}"

    return f"{body}\n"


def scrape_rayucode_docs(max_pages: int = 50, delay: float = 0.8) -> dict[str, str]:
    rp = get_robot_parser(START_URL)
    queue = deque([START_URL])
    visited: set[str] = set()
    scraped_files: dict[str, str] = {}   # filename -> markdown content
    source_map: dict[str, str] = {}      # filename -> source_url

    with httpx.Client(
        headers={"User-Agent": USER_AGENT},
        timeout=15.0,
        follow_redirects=True,
    ) as client:
        while queue and len(visited) < max_pages:
            url = queue.popleft()
            if url in visited:
                continue
            if not rp.can_fetch(USER_AGENT, url):
                print(f"[SKIP robots.txt] {url}")
                continue

            visited.add(url)
            print(f"[{len(visited)}] Scraping {url}")

            try:
                resp = client.get(url)
                resp.raise_for_status()
            except httpx.HTTPError as exc:
                print(f"[WARN] Failed {url}: {exc}")
                continue

            md_text = extract_clean_markdown(resp.text, url)
            if md_text:
                fname = url_to_filename(url)
                scraped_files[fname] = md_text
                source_map[fname] = url

            soup = BeautifulSoup(resp.text, "html.parser")
            for link in soup.find_all("a", href=True):
                nxt = normalize_docs_url(url, link["href"])
                if nxt and nxt not in visited:
                    queue.append(nxt)

            time.sleep(delay)

    if not scraped_files:
        raise RuntimeError("No pages scraped from [rayucode.com/docs](https://rayucode.com/docs); aborting before deleting old docs.")

    # Wipe old data/docs/*.md only after successful scrape
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    for old_md in DOCS_DIR.glob("*.md"):
        old_md.unlink()

    for fname, content in scraped_files.items():
        (DOCS_DIR / fname).write_text(content, encoding="utf-8")

    SOURCES_META_PATH.parent.mkdir(parents=True, exist_ok=True)
    SOURCES_META_PATH.write_text(
        json.dumps(
            {
                "base_url": START_URL,
                "scraped_at": datetime.now(timezone.utc).isoformat(),
                "files": source_map,
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    print(f"Saved {len(scraped_files)} Markdown files to {DOCS_DIR}/")
    return source_map


if __name__ == "__main__":
    scrape_rayucode_docs()