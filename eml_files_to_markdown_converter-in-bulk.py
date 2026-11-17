from pathlib import Path
from email import policy
from email.parser import BytesParser
from bs4 import BeautifulSoup


SOURCE_DIR = Path(r"C:\Workspace\cfc\Python scripts\emails")
OUTPUT_DIR = Path(r"C:\Workspace\cfc\Python scripts\markdown")


def extract_body(msg):
    """
    Extract email body.
    Prefer text/plain.
    Fall back to HTML converted to text.
    """

    plain_text = None
    html_text = None

    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            disposition = str(part.get("Content-Disposition", ""))

            if "attachment" in disposition:
                continue

            try:
                payload = part.get_content()
            except Exception:
                continue

            if content_type == "text/plain":
                plain_text = payload

            elif content_type == "text/html":
                html_text = payload

    else:
        content_type = msg.get_content_type()
        payload = msg.get_content()

        if content_type == "text/plain":
            plain_text = payload

        elif content_type == "text/html":
            html_text = payload

    if plain_text:
        return plain_text.strip()

    if html_text:
        soup = BeautifulSoup(html_text, "html.parser")
        return soup.get_text("\n", strip=True)

    return ""


def convert_eml_to_md(eml_file, md_file):
    with open(eml_file, "rb") as f:
        msg = BytesParser(policy=policy.default).parse(f)

    subject = msg.get("Subject", "")
    sender = msg.get("From", "")
    to = msg.get("To", "")
    date = msg.get("Date", "")

    body = extract_body(msg)

    markdown = f"""# {subject}

| Field | Value |
|---------|---------|
| From | {sender} |
| To | {to} |
| Date | {date} |

---

{body}
"""

    md_file.parent.mkdir(parents=True, exist_ok=True)

    with open(md_file, "w", encoding="utf-8") as f:
        f.write(markdown)


def main():
    eml_files = list(SOURCE_DIR.rglob("*.eml"))

    print(f"Found {len(eml_files)} EML files")

    for eml_file in eml_files:
        relative = eml_file.relative_to(SOURCE_DIR)

        md_file = OUTPUT_DIR / relative.with_suffix(".md")

        try:
            convert_eml_to_md(eml_file, md_file)
            print(f"Converted: {eml_file}")
        except Exception as ex:
            print(f"ERROR: {eml_file}")
            print(ex)

    print("Finished")


if __name__ == "__main__":
    main()