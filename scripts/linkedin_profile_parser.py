#!/usr/bin/env python3
"""
Fixed LinkedIn Profile Parser
Addresses issues found during debugging
"""

import argparse, json, re, sys, unicodedata
from pathlib import Path
from bs4 import BeautifulSoup

# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #

MONTHS = r"""Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec"""

# FIXED: Added proper grouping for the alternation
DATE_LINE_RGX = re.compile(
    fr"(?P<start>(?:{MONTHS}) \d{{4}}|\d{{4}})"
    fr"\s*(?:[–-]|\s+to\s+)"  # Fixed: wrapped alternation in non-capturing group
    fr"\s*(?P<end>Present|(?:{MONTHS}) \d{{4}}|\d{{4}})"
    fr"(?:\s*[·•\-]\s*(?P<duration>[\w\s]+))?", re.I)

SIMPLE_YEAR_RANGE = re.compile(r"(?P<start>\d{4})\s*[-–]\s*(?P<end>\d{4})", re.I)

def _unique(seq):
    """Return list of unique items in order."""
    seen = set()
    out = []
    for s in seq:
        if s not in seen:
            seen.add(s)
            out.append(s)
    return out

def _split_lines(block):
    """Split a block of text into de‑duplicated, stripped lines."""
    return _unique([l.strip() for l in block.split("\n") if l.strip()])

def _normalise(s: str) -> str:
    return unicodedata.normalize("NFKC", s.strip())

# --------------------------------------------------------------------------- #
# Parsers
# --------------------------------------------------------------------------- #

def _parse_name_headline(soup):
    name = soup.find("h1")
    name = _normalise(name.get_text(" ", strip=True)) if name else None
    headline_div = soup.find("div", class_=lambda c: c and "text-body-medium" in c and "break-words" in c)
    headline = _normalise(headline_div.get_text(" ", strip=True)) if headline_div else None
    return name, headline

def _parse_about(soup):
    # Try multiple methods to find About section
    about_section = None
    
    # Method 1: By ID
    about_section = soup.find("section", id="about")
    
    # Method 2: By heading text
    if not about_section:
        about_header = soup.find(lambda t: t.name in ("h2","span") and t.get_text(strip=True) == "About")
        if about_header:
            about_section = about_header.find_parent("section")
    
    if not about_section:
        return None
        
    # Extract text more carefully to avoid duplicates
    paragraphs = about_section.find_all("span")
    texts = []
    for p in paragraphs:
        text = p.get_text(" ", strip=True)
        # Skip if it's just "About" or empty
        if text and text != "About":
            texts.append(text)
    
    return "\n".join(_unique(texts)) if texts else None

# ------------------------- EXPERIENCE -------------------------------------- #

def _extract_dates(line):
    """Extract dates with fixed regex"""
    m = DATE_LINE_RGX.search(line)
    if m:
        return m.group("start"), m.group("end"), m.group("duration")
    m2 = SIMPLE_YEAR_RANGE.search(line)
    if m2:
        return m2.group("start"), m2.group("end"), None
    return None, None, None

def _parse_experience(soup):
    # Find Experience section with multiple methods
    exp_section = None
    
    # Method 1: By section ID
    exp_section = soup.find("section", id="experience")
    
    # Method 2: By heading
    if not exp_section:
        exp_header = soup.find(lambda t: t.name in ("h2","span") and "Experience" in t.get_text(strip=True))
        if exp_header:
            exp_section = exp_header.find_parent("section")
    
    # Method 3: Look for common experience patterns
    if not exp_section:
        for section in soup.find_all(["section", "div"]):
            text = section.get_text()
            if "Experience" in text and any(month in text for month in ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]):
                exp_section = section
                break
    
    if not exp_section:
        print("[DEBUG] No experience section found")
        return []

    roles = []
    
    # Find all list items within the experience section
    # Look for li elements that contain experience data
    # First, find the main list that contains experience items
    exp_list = exp_section.find("ul", class_=lambda c: c and "pvs-list" in c)
    if not exp_list:
        exp_list = exp_section.find("ul")
    
    if not exp_list:
        print("[DEBUG] No experience list found")
        return []
    
    # Get direct children li elements of the main list
    all_li_items = exp_list.find_all("li", recursive=False)
    print(f"[DEBUG] Found {len(all_li_items)} direct li elements in experience list")
    
    # Process each li to determine if it's a role or company group
    processed_items = set()  # Track processed items to avoid duplicates
    
    for li in all_li_items:
        # Skip if already processed as part of a sub-component
        if id(li) in processed_items:
            continue
            
        # Get the text to check if this looks like an experience item
        text = li.get_text().strip()
        if not text:
            continue
        
        # Check if this contains a date pattern (month-based or year-only)
        has_date = False
        for line in text.split('\n'):
            if DATE_LINE_RGX.search(line) or SIMPLE_YEAR_RANGE.search(line):
                has_date = True
                break
        
        if not has_date:
            continue
        
        # Check if this li contains sub-components (multiple roles at same company)
        # Look for sub-components that actually contain a list of roles
        sub_components = None
        sub_div = li.find("div", class_=lambda c: c and "pvs-entity__sub-components" in c)
        if sub_div:
            # Make sure it contains an actual list with multiple items
            sub_list = sub_div.find("ul")
            if sub_list and len(sub_list.find_all("li", recursive=False)) > 0:
                sub_components = sub_div
        
        if sub_components:
            # This is a company with multiple roles
            print("[DEBUG] Found company group with sub-components")
            
            # Extract company name - look for the company link or bold text before sub-components
            company_name = None
            
            # Try to find company name in various ways
            # Method 1: Look for a link with company name before sub-components
            company_link = li.find("a", href=lambda h: h and "/company/" in h)
            if company_link:
                # LinkedIn often has two spans with same text for accessibility
                # Use the first visible span only
                company_spans = company_link.find_all("span", {"aria-hidden": "true"})
                if company_spans:
                    company_text = company_spans[0].get_text(strip=True)
                    if company_text and not DATE_LINE_RGX.search(company_text):
                        company_name = _normalise(company_text)
                else:
                    # Fallback to regular span
                    company_span = company_link.find("span")
                    if company_span:
                        company_text = company_span.get_text(strip=True)
                        if company_text and not DATE_LINE_RGX.search(company_text):
                            company_name = _normalise(company_text)
            
            # Method 2: Look for company text pattern (usually after the title and before dates)
            if not company_name:
                # Get all text before sub-components
                text_elements = []
                for elem in li.children:
                    if elem == sub_components:
                        break
                    if hasattr(elem, 'get_text'):
                        text_elements.append(elem.get_text("\n", strip=True))
                
                all_text = "\n".join(text_elements)
                lines = _split_lines(all_text)
                
                # Company is usually the line with total duration (e.g., "9 yrs 3 mos")
                for i, line in enumerate(lines):
                    if re.search(r'\d+\s*yrs?\s*\d*\s*mos?', line):
                        # Company name should be before this line
                        if i > 0:
                            company_name = _normalise(lines[i-1])
                            break
            
            print(f"[DEBUG] Company name: {company_name}")
            
            # Find all role items within sub-components
            sub_list = sub_components.find("ul")
            if sub_list:
                role_items = sub_list.find_all("li", recursive=False)
                print(f"[DEBUG] Found {len(role_items)} roles in company group")
                
                for role_li in role_items:
                    processed_items.add(id(role_li))
                    role = _parse_single_role(role_li, default_company=company_name)
                    if role:
                        roles.append(role)
        else:
            # This is a single role entry
            print(f"[DEBUG] Found single role entry, first 100 chars: {text[:100]}...")
            role = _parse_single_role(li)
            if role:
                roles.append(role)
            else:
                print("[DEBUG] Single role parsing returned None")
    
    return roles


def _parse_single_role(li, default_company=None):
    """Parse a single role from a list item"""
    raw_text = li.get_text("\n", strip=True)
    raw_text = re.sub(r'<!---->', '', raw_text)
    
    lines = _split_lines(raw_text)
    if not lines:
        return None

    # Quick filter: must contain a date range
    date_idx = None
    for i, line in enumerate(lines):
        if DATE_LINE_RGX.search(line) or SIMPLE_YEAR_RANGE.search(line):
            date_idx = i
            break
            
    if date_idx is None:
        print(f"[DEBUG] No date found in role, skipping")
        return None

    print(f"[DEBUG] Processing role with {len(lines)} lines, date at index {date_idx}")
    for i, line in enumerate(lines[:min(10, len(lines))]):
        print(f"  Line {i}: {line[:80]}...")

    # Extract title - usually the first substantial line
    title = None
    title_idx = 0
    
    for i, line in enumerate(lines[:date_idx]):
        # Skip empty lines and known non-title patterns
        if (line and 
            line != default_company and 
            line.lower() not in ["full-time", "part-time", "contract", "freelance", "internship"] and
            not line.endswith(" logo") and
            "skills" not in line.lower()):
            title = _normalise(line)
            title_idx = i
            break
    
    if not title:
        print("[DEBUG] No title found, skipping")
        return None
    
    # Extract company
    company = default_company
    if not company:
        # Look for company in lines between title and date
        for i in range(title_idx + 1, date_idx):
            line = lines[i]
            # Skip employment type indicators
            if line.lower() in ["full-time", "part-time", "contract", "freelance", "internship"]:
                continue
            # If line contains · or " at ", it might have company info
            if "·" in line or " at " in line:
                company = _normalise(line.split("·")[0].replace(" at ", " ").strip())
                break
            # Otherwise, it might just be the company name
            elif not DATE_LINE_RGX.search(line) and line != title:
                company = _normalise(line)
                break
    
    # Extract dates
    start, end, duration = _extract_dates(lines[date_idx])
    
    # Extract location (look for line with location indicators after date)
    location = ""
    location_idx = None
    for i in range(date_idx + 1, min(date_idx + 5, len(lines))):
        if i < len(lines):
            line = lines[i]
            # Common location patterns
            if any(indicator in line for indicator in [",", "United Kingdom", "UK", "London", "Area", "Remote", "Hybrid", "China"]):
                location = _normalise(line.split("·")[0])
                location_idx = i
                break
    
    # Extract description
    desc_start_idx = location_idx + 1 if location_idx else date_idx + 1
    
    description_lines = []
    for i in range(desc_start_idx, len(lines)):
        line = lines[i]
        # Skip common non-description lines
        if (DATE_LINE_RGX.search(line) or
            "helped me get this job" in line.lower() or
            line.startswith("Show all") or
            line.endswith("skills") or
            "…see more" in line or
            line == title or
            line == company or
            line == location or
            line.lower() in ["full-time", "part-time"]):
            continue
        description_lines.append(line)
    
    description = "\n".join(description_lines).strip()

    role = {
        "company": company,
        "title": title,
        "start": start,
        "end": end,
        "time_in_role": duration,
        "location": location,
        "description": description
    }
    
    print("[EXPERIENCE]", role)
    return role

# ------------------------- EDUCATION --------------------------------------- #

EDU_IGNORE_RGX = re.compile(r"(Course covers|skill|Skills|Licenses|Certifications|Exam qualified|first time pass)", re.I)

def _parse_education(soup):
    # Similar improvements as experience section
    edu_section = None
    
    # Try multiple methods
    edu_section = soup.find("section", id="education")
    
    if not edu_section:
        edu_header = soup.find(lambda t: t.name in ("h2","span") and "Education" in t.get_text(strip=True))
        if edu_header:
            edu_section = edu_header.find_parent("section")
    
    if not edu_section:
        print("[DEBUG] No education section found")
        return []

    entries = []
    for li in edu_section.find_all("li", recursive=True):
        raw_text = li.get_text("\n", strip=True)
        raw_text = re.sub(r'<!---->', '', raw_text)
        
        lines = _split_lines(raw_text)
        if not lines or EDU_IGNORE_RGX.search(lines[0]):
            continue

        print(f"[DEBUG] Processing education item with {len(lines)} lines")
        for i, line in enumerate(lines[:5]):
            print(f"  Line {i}: {line[:80]}...")

        institution = _normalise(lines[0])
        
        # Skip if this doesn't look like an educational institution
        if not any(word in institution.lower() for word in [
            "university", "college", "school", "institute", "academy", 
            "kaplan", "icaew", "acca", "cima", "imperial", "mba", "phd"
        ]):
            continue
            
        # Remove duplicate institution names
        while len(lines) > 1 and lines[1] == institution:
            lines.pop(1)

        # Find course/degree
        course = None
        for line in lines[1:]:
            if not (DATE_LINE_RGX.search(line) or SIMPLE_YEAR_RANGE.search(line)):
                course = _normalise(line)
                break

        # Find dates
        start = end = None
        for line in lines:
            if DATE_LINE_RGX.search(line) or SIMPLE_YEAR_RANGE.search(line):
                start, end, _ = _extract_dates(line)
                break

        entry = {
            "institution": institution,
            "course": course,
            "start": start,
            "end": end
        }
        print("[EDUCATION]", entry)
        entries.append(entry)

    return entries

# ------------------------- ACTIVITY ---------------------------------------- #

def _parse_activity(soup):
    act_section = None
    
    act_section = soup.find("section", id="activity")
    
    if not act_section:
        act_header = soup.find(lambda t: t.name in ("h2","span") and "Activity" in t.get_text(strip=True))
        if act_header:
            act_section = act_header.find_parent("section")
    
    if not act_section:
        return None
        
    text = act_section.get_text("\n", strip=True)
    lines = _unique([l.strip() for l in text.split("\n") if l.strip()])
    return " ".join(lines) if lines else None

# --------------------------------------------------------------------------- #
# API
# --------------------------------------------------------------------------- #

def parse_profile(html_path: Path):
    """Parse a single LinkedIn HTML profile -> dict."""
    soup = BeautifulSoup(html_path.read_text(encoding="utf-8", errors="ignore"), "html.parser")

    name, headline = _parse_name_headline(soup)
    print(f"\n=== Parsing {html_path.name} | {name} ===")
    data = {
        "name": name,
        "headline": headline,
        "about": _parse_about(soup),
        "experience": _parse_experience(soup),
        "education": _parse_education(soup),
        "activity": _parse_activity(soup),
    }
    return data

def main(argv=None):
    argv = argv or sys.argv[1:]
    p = argparse.ArgumentParser(description="Parse LinkedIn profile HTML files -> JSON.")
    p.add_argument("paths", nargs="+", help="One or more HTML files or directories containing them.")
    args = p.parse_args(argv)

    paths = []
    for pth in map(Path, args.paths):
        if pth.is_dir():
            paths.extend(pth.glob("*.html"))
        elif pth.suffix.lower() == ".html":
            paths.append(pth)
    if not paths:
        print("No HTML files found.")
        sys.exit(1)

    for html_file in paths:
        data = parse_profile(html_file)
        out_file = html_file.with_suffix(".json")
        out_file.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        print("Wrote", out_file)

if __name__ == "__main__":
    main()