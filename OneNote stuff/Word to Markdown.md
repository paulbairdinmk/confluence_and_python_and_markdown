This may be the most useful way of doing it, rather than hand conversion

https://github.com/firecrawl/anydoc

import anydoc

## From a file path:
markdown = anydoc.to_markdown("report.docx")

If all else fails then copy and pasting the file into the browser version works - obviously, permissions may be needed for secure stuff.

anydoc by Firecrawl

Use this command in a terminal in VS Code to run the markdown converter. It works.

python -c "import anydoc; print(anydoc.to_markdown('Harbor Solutions Restore Request Form CHN-852 MS365.docx'))" > output.md

Obviously, change the source filename and object filename. It might be possible to create a python script that asks for the source and object filenames and then runs but equally, a copy and paste job just works.

When converting Word documents to Markdown for import into Confluence, handling images correctly depends heavily on your export tool and whether you are importing manually or using a Confluence API/importer tool.

Here are the best ways to embed images in Markdown files for this workflow, ordered by reliability and efficiency.

## Option 1: Confluence Attachment Formatting (Best for Native Confluence Import)
Confluence uses a specific Markdown extension syntax for embedded attachments. Instead of using standard web URLs, you reference the file attachment directly by name.
![Image Description](image-filename.png)
 
How to set up the workflow:

 * Extract all images from your Word document into a dedicated folder (e.g., media/ or images/).
 * Keep the image file names clean and unique (e.g., architecture-diagram-01.png).
 * In your Markdown file, use standard relative image references pointing to those filenames.
 * When importing into Confluence:
   * If using the Confluence UI: Attach the image files directly to the page attachments, and the relative Markdown syntax ![Alt](filename.png) will automatically display the attached image.
   * If using Confluence CLI / REST API / Pandoc plugins: Ensure the script uploads the attachments alongside page creation.

I need to run this past Surjit to check how it works and he has any better ideas.

## Option 2: Base64 Data URI Embedding (Best for Single-File Portability)
If you want a single self-contained Markdown file without needing to manage a separate images/ folder or bulk-upload attachments, you can encode images directly into the Markdown file as Base64 strings.
![Architecture Diagram](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA...)
 
Pros & Cons:
 * Pros: Everything is contained within a single file; no broken paths or missing attachments.
 * Cons: Increases file size significantly; can make raw Markdown text difficult to read; some older Confluence Markdown importers may truncate very long lines.

## Option 3: Base64 Reference-Style Links (Best for Keeping Text Clean)
If using Base64, keep the Markdown body clean by moving the large encoded data blocks to the bottom of the document using reference links.
Here is the system layout:
 
![Architecture Diagram][fig1]
 
As seen in the diagram above...
 
<!-- Base64 definitions at the bottom of the document -->
[fig1]: data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA...
 
### Recommended Tooling for the Conversion Pipeline
To avoid manually saving every image out of Word:

 * Pandoc (Automated Word \rightarrow Markdown + Images):
   Run Pandoc with the --extract-media flag to automatically extract all embedded images into a folder and insert relative links in the resulting Markdown file:
   pandoc document.docx -o document.md --extract-media=./images
 
 * Confluence Markdown Publisher / CLI:
   Tools like confluence-publisher (npm/python) or official CLI tools can parse Markdown, upload extracted images as attachments to the target page, and map the links automatically.

**Highly unlikely that Security would ever allow these third party apps to be installed to solve these issues.**