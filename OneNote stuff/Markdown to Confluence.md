[Surjit's Git repo is extremely good](https://github.com/polarpoint-io/python-mkdocs-to-confluence/blob/main/docs/examples/showcase.md) - this is the showcase.md, but look at the rest of the repo.

## This is the whole process for bulk exporting the Confluence space pages to Git and then back to Confluence
	1. use the Space export option and select "to HTML"
	2. create the list of files in that space with a specific label using the 'Popular labels' macro and screenscraping into a text file, which is then saved under that label name, as a text file
	3. comparing that list against the exported list of HTML files and extracting any matches to a separate folder, either using python or a batch file
	4. amending the HTML_to_Markdown_bulk_converter_inc_attachments_and_html_links_converter.py program to include the specific label
	5. running that programme against the extracted files into a specific label output folder
	6. repeating for all labels
	7. the source folder should then be empty
	8. cut and paste the contents of the specific label output folders into the source folder
	9. the source folder should then contain all Markdown files with the correct labels
	10. running the Bulk_add_header_2_lines.py to add the space and parent_page variables
	11. running the YAML_validation_script.py to validate everything
	12. copying and pasting the source folder contents into C:\Workspace\cfc\platform-operations\markdown-po-docs\docs
	13. raising a ticket in ADO for the upload
	14. proceeding to upload using Git protocols, and using the ADO ticket accordingly.
	15. once approved the files should then automatically create pages 
		a. in the Confluence space specified
		b. under the parent page specified 
		c. with the labels specified
	16. this should be a one off exercise for any space - get all existing pages processed.
	17. business as usual should be that any new pages and amendments to existing pages, should be processed using VS Code changing the Markdown files held in Git. Deletions of pages will be using a specific python script.

    This process omits the space CSV export, and using the content.csv file to cross reference numeric titles against named titles. Basically, Confluence is inconsistent in its exports, sometimes files are exported with justb the text Title, sometimes with text Title and numeric page, and sometimes with just the numeric page as a Title. This then causes issues where the cross reference against the labels often fails as there is a file Title missmatch.

[GitLab Values | The GitLab Handbook - written in markdown and looks very professional](https://handbook.gitlab.com/handbook/values/)<br>
[Markdown metadata format - Stack Overflow - metadata explanations and examples](https://stackoverflow.com/questions/44215896/markdown-metadata-format)<br>