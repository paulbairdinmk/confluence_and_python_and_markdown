from pathlib import Path
from bs4 import BeautifulSoup
from markdownify import markdownify as md
import shutil
import re


# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).parent

SOURCE_DIR = BASE_DIR / "Confluence-input"
OUTPUT_DIR = BASE_DIR / "Confluence-output"

SOURCE_ATTACHMENTS_DIR = SOURCE_DIR / "attachments"
OUTPUT_ATTACHMENTS_DIR = OUTPUT_DIR / "attachments"

OUTPUT_DIR.mkdir(exist_ok=True)

# Labels to add to every converted page
STANDARD_LABELS = [
    "change-enablement",
    "migrated-from-confluence"
]


# ============================================================
# YAML HELPERS
# ============================================================

def yaml_safe_string(value):
    """
    Make a string safe for use inside YAML double quotes.
    """

    value = value.replace("\\", "\\\\")
    value = value.replace('"', '\\"')
    value = value.replace("\r", " ")
    value = value.replace("\n", " ")

    return value


# ============================================================
# LINK CONVERSION
# ============================================================

def convert_local_html_links(markdown):
    """
    Convert local Confluence-export HTML links to Markdown links.

    Example:

        Some-Page_12345.html

    becomes:

        Some-Page_12345.md

    External URLs are unaffected because this operation only
    targets references ending in .html.
    """

    # --------------------------------------------------------
    # Markdown links
    #
    # Example:
    #
    # Some-Page_12345.html
    #
    # becomes:
    #
    # Some-Page_12345.md
    # --------------------------------------------------------

    markdown_link_pattern = re.compile(
        r'(\]\()([^)\s]+?)\.html((?:[?#][^)]*)?\))',
        re.IGNORECASE
    )

    markdown = markdown_link_pattern.sub(
        r'\1\2.md\3',
        markdown
    )

    # --------------------------------------------------------
    # Raw HTML href references
    #
    # Normally markdownify will already have converted these,
    # but this provides a safeguard for HTML that remains in
    # the Markdown.
    #
    # href="Some-Page_12345.html"
    #
    # becomes:
    #
    # href="Some-Page_12345.md"
    # --------------------------------------------------------

    html_href_pattern = re.compile(
        r'(href=["\'])([^"\']+?)\.html'
        r'((?:[?#][^"\']*)?["\'])',
        re.IGNORECASE
    )

    markdown = html_href_pattern.sub(
        r'\1\2.md\3',
        markdown
    )

    return markdown


# ============================================================
# COUNTERS
# ============================================================

converted = 0
failed = 0
attachments_copied = False
links_updated = 0


# ============================================================
# PROCESS HTML FILES
# ============================================================

for html_file in SOURCE_DIR.rglob("*.html"):

    relative_path = html_file.relative_to(SOURCE_DIR)

    output_file = (
        OUTPUT_DIR / relative_path
    ).with_suffix(".md")

    output_file.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    try:

        # ----------------------------------------------------
        # Read HTML file
        # ----------------------------------------------------

        with open(
            html_file,
            encoding="utf-8",
            errors="ignore"
        ) as f:
            html = f.read()

        # ----------------------------------------------------
        # Parse Confluence HTML
        # ----------------------------------------------------

        soup = BeautifulSoup(
            html,
            "html.parser"
        )

        # ----------------------------------------------------
        # Extract Confluence page title
        # ----------------------------------------------------

        title = soup.find(
            id="title-text"
        )

        if title:

            page_title = title.get_text(
                " ",
                strip=True
            )

        else:

            # Fallback to filename if the Confluence
            # page title cannot be identified.
            page_title = html_file.stem

        yaml_title = yaml_safe_string(
            page_title
        )

        # ----------------------------------------------------
        # Extract main Confluence page content
        # ----------------------------------------------------

        content = soup.find(
            "div",
            {"id": "main-content"}
        )

        if content:

            markdown = md(
                str(content)
            )

        else:

            # Fallback to converting complete HTML
            markdown = md(
                html
            )

        # ----------------------------------------------------
        # Convert local HTML page links to Markdown links
        # ----------------------------------------------------

        original_markdown = markdown

        markdown = convert_local_html_links(
            markdown
        )

        if markdown != original_markdown:

            links_updated += 1

        # ----------------------------------------------------
        # Build YAML front matter
        # ----------------------------------------------------

        front_matter = "---\n"

        front_matter += (
            f'title: "{yaml_title}"\n'
        )

        front_matter += "labels:\n"

        for label in STANDARD_LABELS:

            front_matter += (
                f"  - {label}\n"
            )

        front_matter += "---\n\n"

        # ----------------------------------------------------
        # Build final Markdown document
        # ----------------------------------------------------

        markdown = (
            front_matter
            + f"# {page_title}\n\n"
            + markdown
        )

        # ----------------------------------------------------
        # Write Markdown file
        # ----------------------------------------------------

        output_file.write_text(
            markdown,
            encoding="utf-8"
        )

        converted += 1

        print(
            f"Converted: {html_file}"
        )

    except Exception as e:

        failed += 1

        print(
            f"Failed: {html_file}"
        )

        print(
            f"Error: {e}"
        )


# ============================================================
# COPY CONFLUENCE ATTACHMENTS
# ============================================================

print()
print("=" * 60)
print("ATTACHMENTS")
print("=" * 60)

if SOURCE_ATTACHMENTS_DIR.exists():

    try:

        shutil.copytree(
            SOURCE_ATTACHMENTS_DIR,
            OUTPUT_ATTACHMENTS_DIR,
            dirs_exist_ok=True
        )

        attachments_copied = True

        print()
        print(
            "Attachments copied successfully."
        )

        print()

        print(
            f"Source : {SOURCE_ATTACHMENTS_DIR}"
        )

        print(
            f"Target : {OUTPUT_ATTACHMENTS_DIR}"
        )

    except Exception as e:

        print()
        print(
            "ERROR: Attachment copying failed."
        )

        print(
            f"Error: {e}"
        )

else:

    print()
    print(
        "No attachments directory found."
    )

    print(
        "Nothing to copy."
    )


# ============================================================
# SUMMARY
# ============================================================

print()
print("=" * 60)
print("CONVERSION COMPLETE")
print("=" * 60)

print(
    f"Converted         : {converted}"
)

print(
    f"Failed            : {failed}"
)

print(
    f"Pages with links  : {links_updated}"
)

if attachments_copied:

    print(
        "Attachments       : Copied"
    )

else:

    print(
        "Attachments       : None copied"
    )

print("=" * 60)