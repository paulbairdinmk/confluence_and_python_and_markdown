from pathlib import Path
import re

# Directory containing markdown files
directory = Path(".")

for md_file in directory.glob("*.md"):
    content = md_file.read_text(encoding="utf-8")

    # Replace 3 or more spaces with exactly 2 spaces
    updated_content = re.sub(r" {3,}", "  ", content)

    if updated_content != content:
        md_file.write_text(updated_content, encoding="utf-8")
        print(f"Updated: {md_file}")
    else:
        print(f"No changes: {md_file}")