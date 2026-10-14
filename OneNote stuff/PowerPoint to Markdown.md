# marp-pe-gitops-platform

Marp slide deck for **How Platform Engineering ships change** — GitOps with Argo CD, Crossplane, and Key Vault on Azure.

**Author:** Surj Bains, Platform Engineering Manager  
**Owner:** CFC Platform Engineering

Repository: [marp-pe-gitops-platform](https://dev.azure.com/cfcunderwriting/Technology%20Platform/_git/marp-pe-gitops-platform)

## Contents

- [deck.md](./deck.md) — slide source (Marp markdown)
- [themes/cfc.css](./themes/cfc.css) — CFC Marp theme
- [images/](./images/) — theme backgrounds and diagram assets
- [images/external/](./images/external/) — exported PNGs (PlantUML, screenshots)

Diagram sources for several slides live in the shared PlantUML library under `service-arch/argocd/` and `service-arch/crossplane/`.

## Requirements

- Node.js (`brew install node`)
- Make
- Git
- [Marp CLI](https://github.com/marp-team/marp-cli) (installed globally by `make` if missing)
- VS Code or VSCodium (optional, for preview)

Recommended VS Code extensions:

- Marp for VS Code
- PlantUML (for regenerating diagram PNGs from the shared library)

## Usage

Edit [deck.md](./deck.md). Slide metadata, CFC theme, header logo, and footer are set in the YAML front matter.

Place theme assets in `./images` and slide images in `./images/external`.

### Build

```shell
make
```

Produces:

- `deck.pdf`
- `deck.html`
- `deck.pptx`

### Live preview

```shell
make deck.dev
```

### Clean

```shell
make clean        # remove build outputs
make clean-all    # also remove node_modules and package-lock.json
```

## CI

GitHub Actions workflow [.github/workflows/marp-to-pages.yaml](./.github/workflows/marp-to-pages.yaml) builds HTML/PDF/PPTX on push to `main` and publishes HTML to GitHub Pages when a `docs/` folder exists.

## Regenerating diagrams

PNG assets in `images/external/` are generated from PlantUML in the shared library, for example:

| Slide asset | Source |
|-------------|--------|
| `drift-correction.png` | `crossplane/drift-correction-argocd.puml` |
| `app-of-apps.png` | `argocd/app-of-apps.puml` |
| `argocd-c4-system-context.png` | `argocd/argocd-c4-system-context.puml` |
| `crossplane_architecture.png` | `crossplane/arch.puml` |
| `crossplane_argocd_grafana.png` | `crossplane/grafana.puml` |
| `crossplane_argocd_azuredevops.png` | `crossplane/github.puml` |
| `crossplane_argocd_azure.png` | `crossplane/aws.puml` |

Example:

```shell
plantuml -tpng -o /tmp/out path/to/diagram.puml
cp /tmp/out/diagram.png images/external/
make
```
