# Building a Confluence dashboard around labels relies on a clear tagging structure paired with native reporting macros.

## Label Taxonomy Strategy
Establish a structured naming convention using prefixes to make macro filtering seamless across teams and spaces:
 * Domain / Project: proj-mobile, proj-checkout
 * Status / Stage: status-draft, status-review, status-complete
 * Content Type: doc-sop, doc-rfc, doc-meeting
 * Priority / Focus: q3-focus, blocker

## Core Native Macros
| Macro | Best For | Key Parameters |
|-----|-----|----|
| Content Report Table | Tabular listings of labelled pages | Labels: proj-mobile + status-review<br>Spaces: Specific or current |
| Page Properties Report | Rich, metadata-driven dashboards	| Labels: Target label<br>Show Comments: True/False |
| Jira Issues |	Pulling labelled Jira items into Confluence | JQL: labels = "q3-focus" AND project = "MOB" |
| Popular Labels | High-level visual tag clouds	| Number of Labels: 20<br>Scope: Space |

## Recommended Dashboard Layouts

**Layout 1: Executive / High-Level Hub (Asymmetric 2-Column)**
 * Left Column (Wide - 67%):
   * Header: Page Properties Report macro filtering for status-review across key projects.
   * Body: Content Report Table for recent deliverables (doc-rfc).
 * Right Column (Narrow - 33%):
   * Top: Panel macro with Quick Links (create new RFC, submit ticket).
   * Bottom: Recently Updated macro filtered by label family.

**Layout 2: Operational Project Tracker (3-Column Grid)**
 * Column 1: Content Report Table filtered by status-draft.
 * Column 2: Content Report Table filtered by status-review.
 * Column 3: Content Report Table filtered by status-complete.
 
## 1. Standardize Page Templates<br>
   Prerequisite for Page Properties Report
   Create Confluence templates containing a Page Properties macro at the top. Add key metadata fields inside a table (e.g., Owner, Status, Target Date).

## 2. Apply Labels via Page Settings<br>
   Apply standard labels directly to pages created from templates (or configure the template to auto-apply labels on creation).

## 3. Build the Central Dashboard Page<br>
   Create a dedicated Confluence page, apply a 2-column or 3-column section layout, and insert Page Properties Report or Content Report Table macros set to listen for your target labels.

## Links related to CQL

- [Advanced Searching using CQL](https://developer.atlassian.com/server/confluence/advanced-searching-using-cql/)<br>
- [1.3 Introduction to CQL for Confluence Administrators - Data Center/Server](https://www.youtube.com/watch?v=GWdcjrK-UpA)<br>
- [How to Use CQL to Improve Confluence Navigation with Custom Menus](https://www.youtube.com/watch?v=GNc6NgMhQ8k)<br>
- [Search by content status - Better Content Archiving for Confluence | Midori](https://www.youtube.com/watch?v=GNc6NgMhQ8k)<br>
- [CQL fields - Better Content Archiving for Confluence | Midori](https://www.midori-global.com/products/better-content-archiving-for-confluence/cloud/documentation/search-by-content-status/cql-fields)<br>
- [Solved: Where to use/write CQL in the Confluence UI to get...](https://community.atlassian.com/forums/Confluence-questions/Where-to-use-write-CQL-in-the-Confluence-UI-to-get-a-list-of/qaq-p/2826889)<br>
- [CQL Guide - MCP Atlassian](https://mcp-atlassian.soomiles.com/docs/guides/cql-guide)<br>
- [Confluence Pages - MCP Atlassian](https://mcp-atlassian.soomiles.com/docs/tools/confluence-pages)<br>

## Better approach: CQL search
You can query individual label counts using CQL:

space = CE AND label = claims
space = CE AND label = architecture-decision-record
Confluence will show the result count.
Since you're already rationalising the labels, this might be enough for a small dashboard showing:

| Label | Purpose |
|-----|-----|
| architecture-decision-record |	ADRs |
| archived | Archived pages |
| claims	| Claims content |
| bop | BOP content |
| mkdocs	| MkDocs-managed content |

**Next steps**<br>
Create a page called "Content Governance Dashboard" containing: <br>
Content by Label Macros exclusively for each of these labels

- ADRs
- Archived Content
- Claims Content
- BOP Content
and importantly:
- Pages NOT labelled mkdocs
This last one becomes your governance report for detecting pages created directly in Confluence.

https://support.atlassian.com/confluence-cloud/docs/insert-the-filter-by-label-macro/
