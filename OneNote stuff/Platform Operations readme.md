# Platform Operations
![Platform Operations change management](docs/assets/images/hero.png)
Markdown documentation for Platform Operations change management, which is a sub-section of the Change Enablement space in Confluence. Published to Confluence (`CE` space, under `Change Enablement`) on merges to `main` via `azure-pipelines-confluence.yml`.
## Repository layout
```text
markdown-po-docs/
├── docs/
│   ├── assets/images/           # Documentation images (hero banner)
│   ├── kb/                      # Knowledge base articles
│   ├── runbooks/                # Operational runbooks
│   └── templates/               # KB and runbook templates
├── azure-pipelines-confluence.yml
├── mkdocs.yaml
├── mkdocs-confluence.yml
└── requirements.txt
```
## Local preview
```bash
pip install -r requirements.txt
mkdocs serve -f mkdocs-confluence.yml
```
Do not set `MKDOCS_TO_CONFLUENCE` for a local preview. Publishing runs in the pipeline on `main`.
## Documentation
- [Home](docs/index.md)
- [Platform Engineering Setup](docs/kb/kb_platform_engineering_setup.md)
- [Setting Up the CATO CA](docs/kb/kb_setting_up_cato_ca.md)
- [Installing Homebrew](docs/kb/kb_installing_homebrew.md)
- [Using Brewfile](docs/kb/kb_using_brewfile.md)