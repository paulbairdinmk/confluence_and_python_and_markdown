from pathlib import Path
import re

# ============================================================
# Process
#
# Reads all Markdown files.
# Locates the YAML front matter.
# Adds:
# confluence_space
# confluence_parent_page
# Avoids duplicate insertion if those fields already exist.
# Produces a processing summary.
# ===========================================================

# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).parent

MARKDOWN_DIR = BASE_DIR / "Confluence-output"

CONFLUENCE_SPACE = "PO"
CONFLUENCE_PARENT_PAGE = "Imported Legacy Documentation"

# ============================================================
# PROCESS FILES
# ============================================================

updated = 0
skipped = 0
no_header = 0
errors = 0

for md_file in MARKDOWN_DIR.rglob("*.md"):

    try:

        content = md_file.read_text(
            encoding="utf-8"
        )

        # ----------------------------------------------------
        # Find YAML Header
        # ----------------------------------------------------

        match = re.match(
            r"^---\n(.*?)\n---",
            content,
            flags=re.DOTALL
        )

        if not match:

            no_header += 1
            continue

        header = match.group(1)

        # ----------------------------------------------------
        # Already injected?
        # ----------------------------------------------------

        if (
            "confluence_space:" in header
            and
            "confluence_parent_page:" in header
        ):

            skipped += 1
            continue

        # ----------------------------------------------------
        # Add fields
        # ----------------------------------------------------

        new_header = header.rstrip()

        if "confluence_space:" not in header:

            new_header += (
                f'\nconfluence_space: '
                f'"{CONFLUENCE_SPACE}"'
            )

        if "confluence_parent_page:" not in header:

            new_header += (
                f'\nconfluence_parent_page: '
                f'"{CONFLUENCE_PARENT_PAGE}"'
            )

        replacement = (
            "---\n"
            + new_header
            + "\n---"
        )

        content = re.sub(
            r"^---\n.*?\n---",
            replacement,
            content,
            flags=re.DOTALL
        )

        md_file.write_text(
            content,
            encoding="utf-8"
        )

        updated += 1

    except Exception:

        errors += 1

# ============================================================
# SUMMARY
# ============================================================

print()
print("=" * 60)
print("COMPLETE")
print("=" * 60)

print(f"Updated   : {updated}")
print(f"Skipped   : {skipped}")
print(f"No header : {no_header}")
print(f"Errors    : {errors}")