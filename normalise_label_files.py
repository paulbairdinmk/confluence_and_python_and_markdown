from pathlib import Path
from datetime import datetime

# ============================================================
# Purpose
# Standardises Confluence label source files before page-to-label correlation takes place. It is primarily used to normalise release- and archive-related page titles that use UK date formats, ensuring they match the naming conventions found in exported Confluence HTML filenames.
#
# Why this script exists
#
# During migration testing it was discovered that several label files contained page titles using the format:
#
# Plain Text
# 01/02/2021
# 24/11/2020
# 07/12/2020
# 
# whereas the corresponding Confluence-exported HTML files used:
#
# Plain Text
# 2021-02-01
# 2020-11-24
# 2020-12-07
#
# Because the formats differed, extract_labelled_pages.py could not match those pages to their labels.
# 
# This script converts date-based label entries into a format that aligns with the exported HTML pages.
#
# When to use it
# 
# Run this script whenever:
#
# A Confluence space contains release pages named as dates.
# Label files contain UK-style dates.
# Release-related pages are failing to match exported HTML files.
#
# For many spaces this script may make no changes at all, but it is recommended as a standard preprocessing step because it is safe to run and preserves the original label source files.
# ============================================================

# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).parent

SOURCE_LABELS = BASE_DIR / "labels"
OUTPUT_LABELS = BASE_DIR / "labels_normalised"

OUTPUT_LABELS.mkdir(exist_ok=True)

# ============================================================
# HELPERS
# ============================================================

def normalise_label(line):
    """
    Convert UK-style date labels:

        01/02/2021

    into:

        2021-02-01

    Everything else remains unchanged.
    """

    value = line.strip()

    if not value:
        return value

    # --------------------------------------------------------
    # Pure date
    # --------------------------------------------------------

    try:

        dt = datetime.strptime(
            value,
            "%d/%m/%Y"
        )

        return dt.strftime("%Y-%m-%d")

    except ValueError:
        pass

    # --------------------------------------------------------
    # Not a date
    # --------------------------------------------------------

    return value


# ============================================================
# PROCESS FILES
# ============================================================

for source_file in SOURCE_LABELS.glob("*.txt"):

    output_file = OUTPUT_LABELS / source_file.name

    updated_lines = []

    changes = 0

    with open(
        source_file,
        encoding="utf-8"
    ) as f:

        for line in f:

            original = line.rstrip("\n")

            updated = normalise_label(original)

            if original != updated:
                changes += 1

            updated_lines.append(updated)

    with open(
        output_file,
        "w",
        encoding="utf-8"
    ) as f:

        for line in updated_lines:

            f.write(line + "\n")

    print(
        f"{source_file.name}: "
        f"{changes} changes"
    )

print()
print("Complete")
print(f"Output folder: {OUTPUT_LABELS}")