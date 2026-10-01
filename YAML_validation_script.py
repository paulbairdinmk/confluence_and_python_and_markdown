from pathlib import Path
from collections import defaultdict
from urllib.parse import unquote
import re
import sys


print("VALIDATOR SCRIPT STARTED")


# ============================================================
# CONFIGURATION
# ============================================================

SOURCE_DIR = Path(
    r"C:\Workspace\cfc\Python scripts\Confluence-output"
)

# Warn if the Markdown body, excluding front matter,
# is shorter than this number of characters.
MIN_CONTENT_LENGTH = 100


# ============================================================
# REFERENCE HELPERS
# ============================================================

def is_external_reference(reference):
    """
    Return True if a reference should not be checked
    against the local filesystem.

    Includes external URLs and known Confluence
    application-relative URLs.
    """

    reference_lower = reference.strip().lower()

    external_prefixes = (
        "http://",
        "https://",
        "mailto:",
        "tel:",
        "data:",
        "#",
        "/wiki/",
        "/people/",
    )

    return reference_lower.startswith(external_prefixes)


def clean_reference(reference):
    """
    Clean a Markdown/HTML reference before checking it
    against the local filesystem.

    Important:
    Query strings and real URL fragments are removed
    BEFORE URL decoding so that encoded filename
    characters such as %23 (#) are preserved.
    """

    reference = reference.strip()

    # Remove optional Markdown title:
    #
    # image.png "Image description"
    #
    if ' "' in reference:
        reference = reference.split(' "', 1)[0]

    if " '" in reference:
        reference = reference.split(" '", 1)[0]

    # Remove optional angle brackets:
    #
    # <attachments/file.png>
    #
    if (
        reference.startswith("<")
        and reference.endswith(">")
    ):
        reference = reference[1:-1]

    # --------------------------------------------------------
    # Remove REAL query strings and fragments BEFORE decoding
    #
    # This is important because filenames exported from
    # Confluence may contain encoded characters such as:
    #
    # %23 = #
    # %27 = '
    # %2C = ,
    #
    # We do not want an encoded # in a filename to be
    # mistaken for a Markdown/URL fragment.
    # --------------------------------------------------------

    reference = reference.split("?", 1)[0]
    reference = reference.split("#", 1)[0]

    # --------------------------------------------------------
    # Decode URL-encoded filename characters AFTER removing
    # genuine query strings and fragments.
    # --------------------------------------------------------

    reference = unquote(reference)

    return reference.strip()


def find_local_references(body_text):
    """
    Extract local file/image references from Markdown
    and raw HTML contained in the Markdown.

    Returns a set to prevent the same reference being
    checked repeatedly.
    """

    references = set()

    # --------------------------------------------------------
    # Markdown references
    #
    # attachments/123/image.png
    #
    # attachments/123/file.pdf
    # --------------------------------------------------------

    markdown_pattern = re.compile(
        r"!?\[[^\]]*\]\(([^)]+)\)"
    )

    for match in markdown_pattern.finditer(body_text):

        reference = match.group(1).strip()

        if not is_external_reference(reference):
            references.add(reference)

    # --------------------------------------------------------
    # Raw HTML references
    #
    # attachments/123/image.png
    #
    # attachments/123/file.pdf
    # --------------------------------------------------------

    html_reference_pattern = re.compile(
        r"""(?:src|href)\s*=\s*[^"']+["']""",
        re.IGNORECASE,
    )

    for match in html_reference_pattern.finditer(body_text):

        reference = match.group(1).strip()

        if not is_external_reference(reference):
            references.add(reference)

    return references


def validate_local_references(
    file_path,
    body_text,
    result
):
    """
    Validate locally referenced files.

    If an exact Markdown filename cannot be found, attempt
    to locate the target using its Confluence page ID.

    This handles cases where Confluence has URL-encoded
    characters in the physical exported filename.

    Examples:

        Collecting-users'-IP-addresses_2732851314.md

    may actually exist as:

        Collecting-users%27-IP-addresses_2732851314.md
    """

    references = find_local_references(body_text)

    for raw_reference in sorted(references):

        reference = clean_reference(
            raw_reference
        )

        if not reference:
            continue

        if is_external_reference(reference):
            continue

        # ----------------------------------------------------
        # Resolve reference normally
        # ----------------------------------------------------

        if reference.startswith("/"):

            target_path = (
                SOURCE_DIR
                / reference.lstrip("/")
            )

        else:

            reference_path = Path(
                reference.replace("\\", "/")
            )

            target_path = (
                file_path.parent
                / reference_path
            )

        # ----------------------------------------------------
        # Exact target exists
        # ----------------------------------------------------

        if target_path.exists():
            continue

        # ----------------------------------------------------
        # Markdown page-ID fallback
        #
        # If this is a Markdown page reference containing a
        # Confluence numeric page ID, try locating the actual
        # file by ID rather than relying on the exact filename.
        # ----------------------------------------------------

        if reference.lower().endswith(".md"):

            filename = Path(
                reference
            ).name

            page_id_match = re.search(
                r"_([0-9]+)\.md$",
                filename,
                re.IGNORECASE
            )

            if page_id_match:

                page_id = (
                    page_id_match.group(1)
                )

                matching_files = list(
                    SOURCE_DIR.rglob(
                        f"*_{page_id}.md"
                    )
                )

                # ------------------------------------------------
                # Exactly one matching Confluence page
                # ------------------------------------------------

                if len(matching_files) == 1:

                    actual_file = (
                        matching_files[0]
                    )

                    result["warnings"].append(
                        "Linked Markdown filename differs, "
                        "but matching Confluence page ID "
                        "was found: "
                        f"{reference} -> "
                        f"{actual_file.relative_to(SOURCE_DIR)}"
                    )

                    continue

                # ------------------------------------------------
                # Multiple matching IDs would be ambiguous
                # ------------------------------------------------

                if len(matching_files) > 1:

                    matches = ", ".join(
                        str(
                            path.relative_to(
                                SOURCE_DIR
                            )
                        )
                        for path in matching_files
                    )

                    result["errors"].append(
                        "Ambiguous Markdown reference "
                        f"for Confluence page ID "
                        f"{page_id}: "
                        f"{reference}. "
                        f"Matches: {matches}"
                    )

                    continue

        # ----------------------------------------------------
        # Genuine unresolved reference
        # ----------------------------------------------------

        result["errors"].append(
            "Missing local attachment/reference: "
            f"{reference}"
        )


# ============================================================
# VALIDATE A SINGLE MARKDOWN FILE
# ============================================================

def validate_markdown_file(file_path):
    """
    Validate one Markdown file.

    Checks:
        - YAML/front matter delimiters
        - title
        - confluence_space
        - confluence_parent_page
        - duplicate metadata keys
        - document body
        - suspiciously short content
        - locally referenced files/images

    READ-ONLY:
    This function never modifies the Markdown file.
    """

    result = {
        "file": file_path,
        "title": None,
        "errors": [],
        "warnings": [],
    }

    # --------------------------------------------------------
    # Read file
    # --------------------------------------------------------

    try:

        text = file_path.read_text(
            encoding="utf-8-sig"
        )

    except Exception as exc:

        result["errors"].append(
            f"Unable to read file: {exc}"
        )

        return result

    # Normalise line endings in memory only
    text = text.replace(
        "\r\n",
        "\n"
    ).replace(
        "\r",
        "\n"
    )

    lines = text.splitlines()

    # --------------------------------------------------------
    # Empty file
    # --------------------------------------------------------

    if not lines:

        result["errors"].append(
            "File is empty."
        )

        return result

    # --------------------------------------------------------
    # Opening front-matter delimiter
    # --------------------------------------------------------

    if lines[0].strip() != "---":

        result["errors"].append(
            "File does not start with YAML "
            "front matter (---)."
        )

        return result

    # --------------------------------------------------------
    # Find closing front-matter delimiter
    # --------------------------------------------------------

    closing_index = None

    for i in range(1, len(lines)):

        if lines[i].strip() == "---":

            closing_index = i
            break

    if closing_index is None:

        result["errors"].append(
            "YAML front matter has no closing "
            "--- delimiter."
        )

        return result

    # --------------------------------------------------------
    # Separate front matter and document body
    # --------------------------------------------------------

    header_lines = lines[
        1:closing_index
    ]

    body_lines = lines[
        closing_index + 1:
    ]

    body_text = "\n".join(
        body_lines
    ).strip()

    # --------------------------------------------------------
    # Collect metadata
    # --------------------------------------------------------

    titles = []
    spaces = []
    parents = []

    for line in header_lines:

        stripped = line.strip()

        if stripped.startswith("title:"):

            value = stripped[
                len("title:"):
            ].strip()

            titles.append(value)

        elif stripped.startswith(
            "confluence_space:"
        ):

            value = stripped[
                len("confluence_space:"):
            ].strip()

            spaces.append(value)

        elif stripped.startswith(
            "confluence_parent_page:"
        ):

            value = stripped[
                len("confluence_parent_page:"):
            ].strip()

            parents.append(value)

    # ========================================================
    # TITLE
    # ========================================================

    if not titles:

        result["errors"].append(
            "Missing title."
        )

    elif len(titles) > 1:

        result["errors"].append(
            "Duplicate title fields found."
        )

    else:

        title = titles[0].strip()

        # Remove matching surrounding quotes for
        # comparison/reporting purposes.
        if (
            len(title) >= 2
            and title[0] == title[-1]
            and title[0] in ("'", '"')
        ):
            title = title[1:-1]

        result["title"] = title

        if not title:

            result["errors"].append(
                "Title exists but is blank."
            )

    # ========================================================
    # CONFLUENCE SPACE
    # ========================================================

    if not spaces:

        result["errors"].append(
            "Missing confluence_space."
        )

    elif len(spaces) > 1:

        result["errors"].append(
            "Duplicate confluence_space "
            "fields found."
        )

    else:

        space_value = (
            spaces[0]
            .strip()
            .strip("'\"")
        )

        if not space_value:

            result["errors"].append(
                "confluence_space exists "
                "but is blank."
            )

    # ========================================================
    # CONFLUENCE PARENT PAGE
    # ========================================================

    if not parents:

        result["errors"].append(
            "Missing confluence_parent_page."
        )

    elif len(parents) > 1:

        result["errors"].append(
            "Duplicate confluence_parent_page "
            "fields found."
        )

    else:

        parent_value = (
            parents[0]
            .strip()
            .strip("'\"")
        )

        if not parent_value:

            result["errors"].append(
                "confluence_parent_page exists "
                "but is blank."
            )

    # ========================================================
    # DOCUMENT CONTENT
    # ========================================================

    if not body_text:

        result["errors"].append(
            "No Markdown content exists "
            "after the front matter."
        )

    elif len(body_text) < MIN_CONTENT_LENGTH:

        result["warnings"].append(
            "Very little content after "
            f"front matter "
            f"({len(body_text)} characters)."
        )

    # ========================================================
    # LOCAL ATTACHMENTS / REFERENCES
    # ========================================================

    if body_text:

        validate_local_references(
            file_path,
            body_text,
            result
        )

    return result


# ============================================================
# CORPUS-LEVEL VALIDATION
# ============================================================

def validate_corpus(results):
    """
    Perform checks requiring comparison across the
    entire Markdown corpus.

    Currently detects duplicate page titles.
    """

    titles = defaultdict(list)

    for result in results:

        title = result["title"]

        if title:

            normalized_title = (
                title
                .strip()
                .casefold()
            )

            titles[
                normalized_title
            ].append(result)

    # --------------------------------------------------------
    # Duplicate titles
    # --------------------------------------------------------

    for matching_results in titles.values():

        if len(matching_results) <= 1:
            continue

        title = matching_results[0][
            "title"
        ]

        paths = [
            str(item["file"])
            for item in matching_results
        ]

        for result in matching_results:

            current_path = str(
                result["file"]
            )

            other_files = [
                path
                for path in paths
                if path != current_path
            ]

            result["warnings"].append(
                f'Duplicate title "{title}" '
                f'also found in: '
                + ", ".join(other_files)
            )


# ============================================================
# DISPLAY INDIVIDUAL RESULTS
# ============================================================

def print_file_results(results):

    print()
    print("=" * 60)
    print("FILE VALIDATION RESULTS")
    print("=" * 60)
    print()

    for result in results:

        file_path = result["file"]
        errors = result["errors"]
        warnings = result["warnings"]

        # ----------------------------------------------------
        # FAIL
        # ----------------------------------------------------

        if errors:

            print(
                f"FAIL    : {file_path}"
            )

            for error in errors:

                print(
                    f"          ERROR: {error}"
                )

            for warning in warnings:

                print(
                    f"          WARNING: {warning}"
                )

            print()

        # ----------------------------------------------------
        # WARNING
        # ----------------------------------------------------

        elif warnings:

            print(
                f"WARNING : {file_path}"
            )

            for warning in warnings:

                print(
                    f"          WARNING: {warning}"
                )

            print()

        # ----------------------------------------------------
        # PASS
        # ----------------------------------------------------

        else:

            print(
                f"PASS    : {file_path}"
            )


# ============================================================
# SUMMARY
# ============================================================

def print_summary(results):

    total = len(results)

    failed = sum(
        1
        for result in results
        if result["errors"]
    )

    warning_count = sum(
        1
        for result in results
        if (
            result["warnings"]
            and not result["errors"]
        )
    )

    passed = sum(
        1
        for result in results
        if (
            not result["errors"]
            and not result["warnings"]
        )
    )

    print()
    print("=" * 60)
    print("MARKDOWN VALIDATION REPORT")
    print("=" * 60)
    print()

    print(
        f"Files scanned : {total}"
    )

    print(
        f"Passed        : {passed}"
    )

    print(
        f"Warnings      : {warning_count}"
    )

    print(
        f"Failed        : {failed}"
    )

    print()

    # --------------------------------------------------------
    # Publishing recommendation
    # --------------------------------------------------------

    if failed == 0:

        print("=" * 60)

        print(
            "READY FOR CONFLUENCE IMPORT: YES"
        )

        print("=" * 60)

        if warning_count:

            print()

            print(
                "Validation passed, but review "
                "the warnings before publishing."
            )

    else:

        print("=" * 60)

        print(
            "READY FOR CONFLUENCE IMPORT: NO"
        )

        print("=" * 60)

        print()

        print(
            "One or more files failed "
            "validation. Resolve the errors "
            "before publishing."
        )


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 60)

    print(
        "MARKDOWN / CONFLUENCE VALIDATOR"
    )

    print("=" * 60)
    print()

    print("Source directory:")
    print(SOURCE_DIR)
    print()

    # --------------------------------------------------------
    # Source directory checks
    # --------------------------------------------------------

    if not SOURCE_DIR.exists():

        print(
            "ERROR: Source directory "
            "does not exist."
        )

        sys.exit(1)

    if not SOURCE_DIR.is_dir():

        print(
            "ERROR: SOURCE_DIR is not "
            "a directory."
        )

        sys.exit(1)

    # --------------------------------------------------------
    # Find Markdown files
    # --------------------------------------------------------

    markdown_files = sorted(
        SOURCE_DIR.rglob("*.md")
    )

    if not markdown_files:

        print(
            "ERROR: No Markdown files "
            "were found."
        )

        sys.exit(1)

    print(
        f"Found {len(markdown_files)} "
        "Markdown file(s)."
    )

    # --------------------------------------------------------
    # Validate files
    # --------------------------------------------------------

    results = []

    for file_path in markdown_files:

        result = validate_markdown_file(
            file_path
        )

        results.append(result)

    # --------------------------------------------------------
    # Corpus-wide checks
    # --------------------------------------------------------

    validate_corpus(results)

    # --------------------------------------------------------
    # Display results
    # --------------------------------------------------------

    print_file_results(results)

    print_summary(results)

    # --------------------------------------------------------
    # Exit code
    # --------------------------------------------------------

    failed = any(
        result["errors"]
        for result in results
    )

    if failed:
        sys.exit(1)

    sys.exit(0)


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()