# LinkedIn Profile Parser

A tiny CLI that turns **offline LinkedIn profile HTML dumps** into tidy JSON – perfect for further analytics or feeding into LLM pipelines.

## Features

* Pure‑Python, zero authentication – works on any HTML you saved with your browser.
* Handles multiple roles at one company, education, headline, about, and recent activity.
* **One JSON per profile** – easy to diff & track.

---

## Installation

```bash
# Clone / copy the script then:
pip install -r requirements.txt  # bs4, click, tqdm
```

> Or just `pip install beautifulsoup4 click tqdm lxml` if you don’t use a `requirements.txt`.

---

## Usage

```bash
# General syntax
python linkedin_profile_parser.py [OPTIONS] <INPUTS>...
```

* **`INPUTS`** – One or more paths.  Each path can be:

  * a single `*.html` file, or
  * a directory (all `*.html` within will be processed – non‑recursive).

* **`-o / --output-dir`** – Target directory for the JSON files.
  *If omitted*, each JSON is written next to its source HTML.

### Parse a single file

```bash
python linkedin_profile_parser.py linkedin_georgi_georgiev.html
```

JSON will be created as `linkedin_georgi_georgiev.json` in the same folder.

### Parse every HTML in a folder

```bash
python linkedin_profile_parser.py ./profiles_html/
```

Each `*.json` drops next to the matching HTML.

### Parse a folder and write JSON elsewhere

```bash
python linkedin_profile_parser.py ./profiles_html/ -o ./json_output/
```

*Creates `./json_output/` if it doesn’t exist.*

---

## JSON Schema

```jsonc
{
  "name": "Ada Lovelace",
  "headline": "Co‑Founder at Analytical Engines | Keynote Speaker",
  "about": "Pioneer of computing, fascinated by ...",
  "activity": [
    "Ada commented on a post ...",
    "Ada liked a post ..."
  ],
  "experience": [
    {
      "company": "Analytical Engines Ltd.",
      "roles": [
        {
          "title": "Chief Algorithm Officer",
          "start": "Jan 1842",
          "end": "Present",
          "description": "Designed algorithms ..."
        },
        {
          "title": "Co‑Founder",
          "start": "Jan 1833",
          "end": "Dec 1841",
          "description": null
        }
      ]
    }
  ],
  "education": [
    {
      "school": "University of London",
      "degree": "BSc Mathematics",
      "dates": "1830 – 1832",
      "description": null
    }
  ]
}
```

---

## Troubleshooting

* **Parser returns empty fields?** LinkedIn’s DOM changes frequently – open an issue with a sample HTML.
* **Multiple roles not grouped?** Make sure the HTML wasn’t truncated during save (scroll all experience before saving).

---

## Licence

MIT – do whatever you like. 🎉
