from pathlib import Path
from bs4 import BeautifulSoup
import re

#==========================================================
# Files exported from Confluence have the space name as part of the page title eg "Change Enablement : Page Title"
# This script will remove the space name from the title and rename the HTML file accordingly.
# ==========================================================


# Folder containing the HTML files
HTML_FOLDER = r"C:\Workspace\cfc\Python scripts\Title_corrections"

# Prefix to remove from titles
PREFIX = "Change Enablement : "

# Invalid Windows filename characters
INVALID_CHARS = r'[<>:"/\\|?*]'


def clean_filename(name):
    """Remove invalid filename characters and tidy whitespace."""
    name = re.sub(INVALID_CHARS, "-", name)
    name = re.sub(r"\s+", " ", name).strip()
    return name


folder = Path(HTML_FOLDER)

for html_file in folder.glob("*.html"):
    try:
        with open(html_file, "r", encoding="utf-8", errors="ignore") as f:
            soup = BeautifulSoup(f, "html.parser")

        if not soup.title or not soup.title.string:
            print(f"No title found: {html_file.name}")
            continue

        title = soup.title.string.strip()

        # Remove prefix if present
        if title.startswith(PREFIX):
            title = title[len(PREFIX):]

        new_name = clean_filename(title) + ".html"
        new_path = html_file.with_name(new_name)

        # Avoid overwriting files
        counter = 1
        while new_path.exists() and new_path != html_file:
            new_name = f"{clean_filename(title)}_{counter}.html"
            new_path = html_file.with_name(new_name)
            counter += 1

        if new_path != html_file:
            html_file.rename(new_path)
            print(f"Renamed: {html_file.name} -> {new_path.name}")

    except Exception as e:
        print(f"Error processing {html_file.name}: {e}")

print("Done.")