#!/usr/bin/env python3
"""linkedin_profile_parser.py
Parses downloaded LinkedIn profile HTML pages (as of 2025 layout) and saves
one JSON file per profile containing key profile information.

Extracted fields
================
- **name** (str)
- **headline** (str)
- **about** (str | None)
- **experience** (list[dict])
    - company (str)
    - title  (str)
    - start  (str | None)
    - end    (str | None)
    - description (str | None)
- **education** (list[dict])
    - institution (str)
    - degree      (str | None)
    - start       (str | None)
    - end         (str | None)
- **activity** (str | None)

Usage
-----
```bash
python linkedin_profile_parser.py some_profile.html other_profile.html
python linkedin_profile_parser.py /path/to/directory_with_html_files
```
If you supply a directory, the script picks up every `*.html` it finds inside.

Dependencies: **beautifulsoup4**
Note: LinkedIn’s offline HTML uses hashed class names, so the parser relies
mostly on structural cues (headings, section ordering, visible text) and some
simple regex heuristics.
"""

import argparse
import json
import re
from pathlib import Path
from bs4 import BeautifulSoup

MONTHS = (
    "Jan", "Feb", "Mar", "Apr", "May", "Jun",
    "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
)

# Matches patterns like "Jan 2020 - Present" or "Jan 2020 - Mar 2024"
DATE_RGX = re.compile(
    rf"({'|'.join(MONTHS)}) \d{{4}}\s*-\s*(Present|({'|'.join(MONTHS)}) \d{{4}})",
    re.I,
)


def _unique(seq):
    """Return list of strings with duplicates removed, preserving order."""
    seen = set()
    out = []
    for s in seq:
        if s not in seen:
            seen.add(s)
            out.append(s)
    return out


def _split_lines(block: str):
    """Split a block of text on new‑lines and deduplicate."""
    return _unique([t.strip() for t in block.split("\n") if t.strip()])


# ---------------------------------------------------------------------------
# Top‑card helpers
# ---------------------------------------------------------------------------

def _parse_name_headline(soup):
    name_tag = soup.find("h1")
    name = name_tag.get_text(strip=True) if name_tag else None
    headline_div = soup.find(
        "div", class_=lambda c: c and "text-body-medium" in c and "break-words" in c
    )
    headline = headline_div.get_text(" ", strip=True) if headline_div else None
    return name, headline


def _parse_about(soup):
    about_section = soup.find("section", id="about")
    if not about_section:
        header = soup.find(
            lambda t: t.name in ("h2", "span") and t.get_text(strip=True) == "About"
        )
        about_section = header.find_parent("section") if header else None
    if not about_section:
        return None
    spans = about_section.find_all("span")
    texts = [s.get_text(" ", strip=True) for s in spans if s.get_text(strip=True)]
    return "\n".join(_unique(texts)) if texts else None


# ---------------------------------------------------------------------------
# Experience parsing
# ---------------------------------------------------------------------------

def _parse_experience(soup):
    exp_header = soup.find(
        lambda t: t.name in ("h2", "span") and t.get_text(strip=True) == "Experience"
    )
    exp_section = exp_header.find_parent("section") if exp_header else None
    if not exp_section:
        return []

    roles = []
    for li in exp_section.find_all("li"):
        raw = li.get_text("\n", strip=True)
        if not DATE_RGX.search(raw):
            # Probably a company wrapper or irrelevant item
            continue
        lines = _split_lines(raw)
        if not lines:
            continue

        title = lines[0]
        company = None
        datestr = None
        description = []

        for idx, line in enumerate(lines[1:], start=1):
            # Date line
            if DATE_RGX.search(line) or re.match(r"\d{4}\s*-\s*(?:Present|\d{4})", line):
                datestr = line
                continue
            # Company line (first non‑date, non‑description line)
            if company is None:
                company = line.split("·", 1)[0].strip() if "·" in line else line
                continue
            # Everything after dates is description
            if datestr:
                description.append(line)

        start = end = None
        if datestr:
            if " - " in datestr:
                start, end = [x.strip() for x in datestr.split(" - ", 1)]

        roles.append(
            {
                "company": company,
                "title": title,
                "start": start,
                "end": end,
                "description": "\n".join(description) if description else None,
            }
        )

    return roles


# ---------------------------------------------------------------------------
# Education parsing
# ---------------------------------------------------------------------------

def _parse_education(soup):
    edu_header = soup.find(
        lambda t: t.name in ("h2", "span") and t.get_text(strip=True) == "Education"
    )
    edu_section = edu_header.find_parent("section") if edu_header else None
    if not edu_section:
        return []

    education = []
    for li in edu_section.find_all("li"):
        lines = _split_lines(li.get_text("\n", strip=True))
        if not lines:
            continue

        institution = lines[0]
        degree = None
        datestr = None

        for l in lines[1:]:
            if DATE_RGX.search(l) or re.match(r"\d{4}\s*-\s*\d{4}", l):
                datestr = l
            elif degree is None:
                degree = l

        start = end = None
        if datestr and " - " in datestr:
            start, end = [x.strip() for x in datestr.split(" - ", 1)]

        education.append(
            {
                "institution": institution,
                "degree": degree,
                "start": start,
                "end": end,
            }
        )

    return education


# ---------------------------------------------------------------------------
# Activity parsing
# ---------------------------------------------------------------------------

def _parse_activity(soup):
    act_header = soup.find(
        lambda t: t.name in ("h2", "span") and t.get_text(strip=True) == "Activity"
    )
    act_section = act_header.find_parent("section") if act_header else None
    if not act_section:
        return None
    lines = _split_lines(act_section.get_text("\n", strip=True))
    return " ".join(lines) if lines else None


# ---------------------------------------------------------------------------
# Wrapper
# ---------------------------------------------------------------------------

def parse_profile(path: Path):
    """Parse a single HTML profile file -> dict."""
    html = path.read_text(encoding="utf-8", errors="ignore")
    soup = BeautifulSoup(html, "html.parser")

    name, headline = _parse_name_headline(soup)

    return {
        "name": name,
        "headline": headline,
        "about": _parse_about(soup),
        "experience": _parse_experience(soup),
        "education": _parse_education(soup),
        "activity": _parse_activity(soup),
    }


# ---------------------------------------------------------------------------
# CLI helpers
# ---------------------------------------------------------------------------

def _json_out_path(in_path: Path) -> Path:
    # Try to pull the username from the original file name: linkedin_<user>_timestamp.html
    user_bit = in_path.stem.split("_", 1)[-1]
    return in_path.with_suffix(".json").with_name(f"{user_bit}.json")


def _save(data: dict, out_path: Path):
    out_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description="Parse LinkedIn profile HTML files → JSON")
    parser.add_argument(
        "paths",
        nargs="+",
        help="HTML files or directories containing them",
    )
    args = parser.parse_args()

    # Expand directories into *.html file lists
    html_paths = []
    for p in args.paths:
        pth = Path(p)
        if pth.is_dir():
            html_paths.extend(sorted(pth.glob("*.html")))
        elif pth.suffix.lower() == ".html":
            html_paths.append(pth)

    if not html_paths:
        print("❌ No HTML files found to parse.")
        return

    for html_file in html_paths:
        try:
            profile = parse_profile(html_file)
            out_file = _json_out_path(html_file)
            _save(profile, out_file)
            print(f"✅ {html_file.name} → {out_file.name}")
        except Exception as exc:
            print(f"⚠️  Error parsing {html_file}: {exc}")


if __name__ == "__main__":
    main()
