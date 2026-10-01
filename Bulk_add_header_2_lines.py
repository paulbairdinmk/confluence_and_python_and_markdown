from pathlib import Path

# ============================================================
# CONFIGURATION
# ============================================================

SOURCE_DIR = Path(r"C:\Workspace\cfc\Python scripts\Confluence-output")

CONFLUENCE_SPACE = 'confluence_space: "PO"'
CONFLUENCE_PARENT = 'confluence_parent_page: "Imported Legacy Documentation"'


# ============================================================
# PROCESS A SINGLE MARKDOWN FILE
# ============================================================

def update_markdown_file(file_path: Path) -> str:
    """
    Add or update Confluence routing metadata in YAML front matter.

    Returns:
        updated   - metadata was added or changed
        skipped   - metadata already has the requested values
        no_header - no valid YAML front matter was found
    """

    text = file_path.read_text(encoding="utf-8-sig")

    # Normalise line endings while processing
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    lines = text.splitlines()

    # File must start with YAML front matter
    if not lines or lines[0].strip() != "---":
        return "no_header"

    # Find closing ---
    closing_index = None

    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            closing_index = i
            break

    if closing_index is None:
        return "no_header"

    space_index = None
    parent_index = None

    # Find existing Confluence routing properties
    for i in range(1, closing_index):

        if lines[i].strip().startswith("confluence_space:"):
            space_index = i

        if lines[i].strip().startswith("confluence_parent_page:"):
            parent_index = i

    changed = False

    # --------------------------------------------------------
    # Update existing values
    # --------------------------------------------------------

    if space_index is not None:
        if lines[space_index] != CONFLUENCE_SPACE:
            lines[space_index] = CONFLUENCE_SPACE
            changed = True

    if parent_index is not None:
        if lines[parent_index] != CONFLUENCE_PARENT:
            lines[parent_index] = CONFLUENCE_PARENT
            changed = True

    # --------------------------------------------------------
    # Add missing values
    # --------------------------------------------------------

    new_lines = []

    if space_index is None:
        new_lines.append(CONFLUENCE_SPACE)
        changed = True

    if parent_index is None:
        new_lines.append(CONFLUENCE_PARENT)
        changed = True

    if new_lines:

        # Prefer inserting immediately before
        # confluence_properties:
        insert_index = closing_index

        for i in range(1, closing_index):
            if lines[i].strip().startswith("confluence_properties:"):
                insert_index = i
                break

        lines[insert_index:insert_index] = new_lines

    # Nothing changed
    if not changed:
        return "skipped"

    # Write modified file
    file_path.write_text(
        "\n".join(lines) + "\n",
        encoding="utf-8"
    )

    return "updated"


# ============================================================
# MAIN
# ============================================================

def main():

    updated = 0
    skipped = 0
    no_header = 0
    errors = 0

    print(f"Scanning: {SOURCE_DIR}")
    print()

    for file_path in SOURCE_DIR.rglob("*.md"):

        try:
            result = update_markdown_file(file_path)

            if result == "updated":
                updated += 1
                print(f"UPDATED   : {file_path}")

            elif result == "skipped":
                skipped += 1
                print(f"SKIPPED   : {file_path}")

            elif result == "no_header":
                no_header += 1
                print(f"NO HEADER : {file_path}")

        except Exception as exc:
            errors += 1
            print(f"ERROR     : {file_path}")
            print(f"            {exc}")

    print()
    print("=" * 60)
    print("COMPLETE")
    print("=" * 60)
    print(f"Updated   : {updated}")
    print(f"Skipped   : {skipped}")
    print(f"No header : {no_header}")
    print(f"Errors    : {errors}")


if __name__ == "__main__":
    main()