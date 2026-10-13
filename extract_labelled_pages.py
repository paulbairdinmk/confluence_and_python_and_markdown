from pathlib import Path
import shutil
import re
import urllib.parse
import csv
import json
from collections import defaultdict

import pandas as pd

# ============================================================
# Purpose:
# Correlates exported Confluence HTML pages with Confluence labels and prepares the content for migration to Git/Markdown.
#
# Inputs
#
# Confluence-input\ – HTML export of the Confluence space.
# labels\ (or labels_normalised\) – text files containing page titles for each Confluence label. This can be obtained from Confluence using the "Filer by Label" macro, setting the label and space, and then screenscraping the content into a text file. The text file name is taken from the label.
# WARNING - Confluence can treat filenames from the space export and the label text files differently - it not consistent. The exported HTML filenames are URL-encoded and may contain a Confluence page ID suffix. The label text files contain the page titles as they appear in Confluence. This script normalises both to improve matching.
#
# Process
#
# Reads all exported HTML files.
# Reads all label text files.
# Normalises page titles and filenames to improve matching.
# Matches pages to one or more labels.
# Copies matched HTML pages into the extracted\ folder.
# Generates migration metadata and audit reports.
#
# Outputs
#
# extracted\ – HTML pages that have been successfully correlated to labels.
# exports\page_metadata.json – page title and label mapping used later for Markdown label injection.
# reports\matched_files.csv – pages successfully matched.
# reports\multiple_labels.csv – pages with more than one label.
# reports\missing_pages.txt – pages that could not be matched.
# reports\possible_matches.csv – fuzzy matches identified during processing.
#reports\unlabelled_html.txt – exported HTML pages that have no recognised label.
#
# Role in the migration process - This is the primary reconciliation and metadata-generation step. It links Confluence page content to Confluence labels and produces the metadata required for subsequent HTML-to-Markdown conversion and YAML label injection.
# ============================================================


# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).parent

SOURCE_HTML_DIR = BASE_DIR / "Confluence-input"
LABELS_DIR = BASE_DIR / "labels"
EXTRACTED_DIR = BASE_DIR / "extracted"
REPORTS_DIR = BASE_DIR / "reports"

CONTENT_MAP_FILE = BASE_DIR / "content.xlsx"

EXTRACTED_DIR.mkdir(exist_ok=True)
REPORTS_DIR.mkdir(exist_ok=True)

# ============================================================
# HELPERS
# ============================================================

def normalise(text):
    """
    Convert Confluence page titles and exported filenames
    into comparable values.
    """

    text = urllib.parse.unquote(str(text))

    text = Path(text).stem

    # Remove Confluence page ID suffix
    text = re.sub(r'_[0-9]+$', '', text)

    # Remove Keep--- prefix
    text = re.sub(
        r'^Keep---',
        '',
        text,
        flags=re.IGNORECASE
    )

    # Standardise separators
    text = text.replace('---', ' ')
    text = text.replace('--', ' ')
    text = text.replace('-', ' ')
    text = text.replace('&', ' and ')

    text = text.lower()

    text = re.sub(r'[^a-z0-9 ]+', ' ', text)

    text = re.sub(r'\s+', ' ', text)

    return text.strip()


# ============================================================
# LOAD CONTENT.XLSX LOOKUP
# ============================================================

content_lookup = {}

if CONTENT_MAP_FILE.exists():

    print(f"Loading content map: {CONTENT_MAP_FILE.name}")

    try:

        df = pd.read_excel(
            CONTENT_MAP_FILE,
            engine="openpyxl"
        )

        df.columns = [
            str(c).strip().lower()
            for c in df.columns
        ]

        print("Columns found:")
        print(list(df.columns))

        required = {"contentid", "title"}

        if required.issubset(df.columns):

            for _, row in df.iterrows():

                contentid = str(
                    row["contentid"]
                ).strip()

                title = str(
                    row["title"]
                ).strip()

                if (
                    contentid
                    and contentid != "nan"
                    and title
                    and title != "nan"
                ):

                    content_lookup[contentid] = title

            print(
                f"Loaded {len(content_lookup)} content mappings"
            )

        else:

            print()
            print(
                "WARNING: content.xlsx must contain "
                "'contentid' and 'title' columns"
            )

    except Exception as ex:

        print()
        print(
            f"ERROR reading content.xlsx: {ex}"
        )

else:

    print()
    print("WARNING: content.xlsx not found")

# ============================================================
# BUILD HTML FILE INDEX
# ============================================================

html_index = {}

numeric_files = []

for html_file in SOURCE_HTML_DIR.rglob("*.html"):

    filename_key = normalise(html_file.name)

    html_index[filename_key] = html_file

    if re.fullmatch(r"\d+\.html", html_file.name):

        numeric_files.append(html_file)

print()
print(f"Loaded {len(html_index)} HTML files")
print(f"Found {len(numeric_files)} numeric HTML files")

# ============================================================
# INDEX NUMERIC FILES USING CONTENT.XLSX
# ============================================================

numeric_matches = 0

for html_file in numeric_files:

    contentid = html_file.stem

    if contentid not in content_lookup:
        continue

    title = content_lookup[contentid]

    key = normalise(title)

    if key not in html_index:

        html_index[key] = html_file

        numeric_matches += 1

print(
    f"Indexed {numeric_matches} numeric files "
    f"using content.xlsx"
)

# ============================================================
# BUILD PAGE -> LABEL MAP
# ============================================================

page_labels = defaultdict(list)

label_files = sorted(
    LABELS_DIR.glob("*.txt")
)

for label_file in label_files:

    label_name = label_file.stem

    print(f"Loading label file: {label_name}")

    with open(
        label_file,
        encoding="utf-8"
    ) as f:

        for line in f:

            page_title = line.strip()

            if not page_title:
                continue

            page_labels[
                page_title
            ].append(label_name)

total_label_assignments = sum(
    len(v)
    for v in page_labels.values()
)

print()
print(
    f"Loaded {len(page_labels)} unique page titles"
)

print(
    f"Loaded {total_label_assignments} label assignments"
)

# ============================================================
# PROCESS PAGES
# ============================================================

matched = []
missing = []
multiple_labels = []
possible_matches = []

metadata = {}

for page_title, labels in sorted(page_labels.items()):

    key = normalise(page_title)

    source_file = None

    # --------------------------------------------------------
    # Exact Match
    # --------------------------------------------------------

    if key in html_index:

        source_file = html_index[key]

    else:

        # ----------------------------------------------------
        # Fuzzy Match
        # ----------------------------------------------------

        candidates = []

        for html_key, html_file in html_index.items():

            if (
                key in html_key
                or html_key in key
            ):

                candidates.append(
                    html_file
                )

        if len(candidates) == 1:

            source_file = candidates[0]

            possible_matches.append([
                page_title,
                source_file.name
            ])

    # --------------------------------------------------------
    # Still no match
    # --------------------------------------------------------

    if source_file is None:

        missing.append(page_title)

        continue

    # --------------------------------------------------------
    # Copy matched file
    # --------------------------------------------------------

    target_file = (
        EXTRACTED_DIR /
        source_file.name
    )

    if not target_file.exists():

        shutil.copy2(
            source_file,
            target_file
        )

    metadata[source_file.name] = {

        "page_title": page_title,
        "labels": labels
    }

    matched.append([

        page_title,
        source_file.name,
        "|".join(labels)

    ])

    if len(labels) > 1:

        multiple_labels.append([

            page_title,
            "|".join(labels)

        ])

# ============================================================
# IDENTIFY UNLABELLED HTML FILES
# ============================================================

matched_html_files = {

    row[1]
    for row in matched

}

unlabelled_html = []

for html_file in SOURCE_HTML_DIR.rglob("*.html"):

    if html_file.name not in matched_html_files:

        unlabelled_html.append(
            html_file.name
        )

# ============================================================
# REPORTS
# ============================================================

with open(
    REPORTS_DIR / "matched_files.csv",
    "w",
    newline="",
    encoding="utf-8"
) as f:

    writer = csv.writer(f)

    writer.writerow([
        "Page Title",
        "HTML File",
        "Labels"
    ])

    writer.writerows(matched)

with open(
    REPORTS_DIR / "missing_pages.txt",
    "w",
    encoding="utf-8"
) as f:

    for item in sorted(missing):

        f.write(item + "\n")

with open(
    REPORTS_DIR / "multiple_labels.csv",
    "w",
    newline="",
    encoding="utf-8"
) as f:

    writer = csv.writer(f)

    writer.writerow([
        "Page Title",
        "Labels"
    ])

    writer.writerows(
        multiple_labels
    )

with open(
    REPORTS_DIR / "possible_matches.csv",
    "w",
    newline="",
    encoding="utf-8"
) as f:

    writer = csv.writer(f)

    writer.writerow([
        "Page Title",
        "Matched HTML File"
    ])

    writer.writerows(
        possible_matches
    )

with open(
    REPORTS_DIR / "unlabelled_html.txt",
    "w",
    encoding="utf-8"
) as f:

    for item in sorted(
        unlabelled_html
    ):

        f.write(item + "\n")

with open(
    REPORTS_DIR / "page_metadata.json",
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        metadata,
        f,
        indent=2,
        ensure_ascii=False
    )

# ============================================================
# SUMMARY
# ============================================================

print()
print("=" * 60)
print("COMPLETE")
print("=" * 60)

print(
    f"Matched pages      : {len(matched)}"
)

print(
    f"Missing pages      : {len(missing)}"
)

print(
    f"Multiple labels    : {len(multiple_labels)}"
)

print(
    f"Possible matches   : {len(possible_matches)}"
)

print(
    f"Unlabelled HTML    : {len(unlabelled_html)}"
)

print()
print("Reports written to:")
print(REPORTS_DIR)