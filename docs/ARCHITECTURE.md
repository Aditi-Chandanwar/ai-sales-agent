# AI Sales Agent Architecture

## Project Objective

The AI Sales Agent helps **Genuine Automation Products LLP** discover qualified industrial end-user leads, extract publicly available contact information, and send the first introduction email automatically.

The system is designed for industrial automation and sensor sales, with an initial MVP focused on automotive end users in Germany and Southeast Asia.

---

## High-Level Workflow

```text
User Input
↓
Lead Discovery Agent
↓
Lead Qualification Agent
↓
Contact Extraction Agent
↓
Lead Scoring Agent
↓
Lead Database
↓
Outreach Agent
↓
Email Status Tracking

User Input

The user provides:

Target Region / Country
Target Industry
Target Type
Product Category
Number of Leads Required

Example:

Region: Germany
Industry: Automotive
Target Type: End Users Only
Product Category: Industrial Sensors
Lead Count: 10
AI Agent Summary
Agent	Responsibility	Input	Output
Lead Discovery Agent	Finds companies matching the target region and industry	LeadDiscoveryRequest	List of potential Lead objects
Lead Qualification Agent	Checks whether the company is an end user	Company details, website content	Qualified / Rejected status with reason
Contact Extraction Agent	Extracts publicly available contact information	Company website	Email, phone, contact page, contact person if available
Lead Scoring Agent	Scores lead quality and relevance	Qualified lead data	Lead score and scoring reason
Outreach Agent	Sends the first general introduction email	Qualified lead + email template	Email sent status
Response Analysis Agent	Future: analyzes customer replies	Customer email reply	Requirement summary
Product Recommendation Agent	Future: recommends relevant sensors	Customer requirements + catalogue data	Suggested products and draft response
System Workflow Diagram
                       AI Sales Agent

                            │
                            ▼
                       User Input
        Region + Industry + Product Category + Lead Count
                            │
                            ▼
                  Lead Discovery Agent
                            │
                            ▼
                 Potential Company List
                            │
                            ▼
                Lead Qualification Agent
                            │
              ┌─────────────┴─────────────┐
              ▼                           ▼
        Qualified Lead              Rejected Lead
              │                           │
              ▼                           ▼
 Contact Extraction Agent            Store Reason
              │
              ▼
        Lead Scoring Agent
              │
              ▼
          Lead Database
              │
              ▼
         Outreach Agent
              │
              ▼
     First Introduction Email Sent
              │
              ▼
       Email Status Tracking
Current Sprint Detail: Sprint 1 - Lead Discovery

Sprint 1 focuses only on discovering potential companies and saving them in a structured format.

LeadDiscoveryRequest
        ↓
Query Builder
        ↓
Tavily Search Provider
        ↓
Search Results
        ↓
Result Processing
        ↓
Domain-Based Deduplication
        ↓
Lead Objects
        ↓
CSV Export
Current Data Models
LeadDiscoveryRequest

Represents the user's search request.

Fields:

region
industry
lead_count
product_category
target_type

Example:

region = Germany
industry = Automotive
lead_count = 10
product_category = Industrial Sensors
target_type = End Users Only
Lead

Represents one discovered lead.

Fields:

company_name
website
country
source_url
search_query
notes
Agent Details
1. Lead Discovery Agent
Purpose

Find companies that match the selected region, industry, and product category.

Current Implementation

The Lead Discovery Agent currently uses:

LeadDiscoveryRequest dataclass for input
Lead dataclass for output
Tavily Search API as the search provider
Query generation biased toward end users
Domain-based deduplication
CSV export
Inputs
Region / Country
Industry
Product Category
Target Type
Lead Count

Example input:

Find 10 automotive end-user companies in Germany that may use industrial sensors.
Search Query Strategy

The agent creates search queries such as:

automotive assembly plants Germany
automotive manufacturing plants Germany
automotive production facilities Germany
automotive component manufacturers Germany
industrial automation users automotive Germany
factories using industrial sensors automotive Germany

These queries are designed to find end users rather than distributors or traders.

Possible Data Sources
Tavily Search API
Search engines
Business directories
Industry associations
Company websites
Public company listings
Output
Company Name
Website
Country
Source URL
Search Query
Notes
2. Lead Qualification Agent
Purpose

Decide whether a discovered company is a valid end-user lead.

Accept companies such as:

Automotive manufacturers
Automotive plants
Machine builders
Manufacturing companies
Industrial automation users

Reject companies such as:

Sensor distributors
Traders
Resellers
Component suppliers
Irrelevant companies

Output:

Qualification Status: Qualified / Rejected
Reason
Confidence Score

Example:

Qualified because the company manufactures automotive parts and likely uses automation sensors in production lines.
3. Contact Extraction Agent
Purpose

Visit the company website and extract publicly available contact information.

Extract:

Email address
Contact page URL
Phone number
Contact person, if available
Source URL

Rules:

Use only publicly available information.
Do not guess private email addresses.
Prefer official company contact emails.
Store the source URL for traceability.
4. Lead Scoring Agent
Purpose

Rank leads based on relevance and outreach quality.

Scoring factors:

Industry match
Region match
End-user confidence
Contact information availability
Website credibility
Relevance to industrial sensor applications

Output:

Lead Score
Scoring Reason

Example scoring:

Score: 85/100
Reason: Automotive manufacturer, official website found, public email available, high relevance to industrial automation sensors.
5. Outreach Agent
Purpose

Send the first introduction email to qualified leads.

Sender email:

marketing@genuineautomation.com

Rules:

Send only the first general introduction email automatically.
Include company introduction and general catalogue/services.
Do not send quotations automatically.
Do not send pricing automatically.
Do not send technical product recommendations automatically.
Track email sent status.

Output:

Email Sent / Failed
Timestamp
Recipient Email
Lead ID
Lead Database

The MVP should maintain a structured lead database.

Suggested fields:

Field	Description
Lead ID	Unique lead identifier
Company Name	Name of the company
Country	Company country
Industry	Target industry
Website	Company website
Contact Email	Public email found
Contact Person	Person name if available
Contact Page URL	Source contact page
Qualification Status	Qualified / Rejected
Qualification Reason	Why the lead was accepted or rejected
Lead Score	Relevance score
Email Status	Not Sent / Sent / Failed
Last Updated	Timestamp
Human-in-the-Loop Rules

The system may automatically send the first general introduction email only when:

The company is classified as an end user.
Public contact information is available.
Lead confidence score is acceptable.
The email is a general introduction, not a technical or commercial offer.

Human approval is required for:

Second email response
Product recommendation
Pricing
Quotations
Negotiation
Technical commitments
Knowledge Base: Future Component

Future versions will include a company knowledge base containing:

Product catalogue
Technical datasheets
Sensor specifications
Application notes
Company profile
Industry-specific use cases

This knowledge base will support response analysis and product recommendation.

Future flow:

Customer Reply
↓
Response Analysis Agent
↓
Product Catalogue / Datasheet Knowledge Base
↓
Product Recommendation Agent
↓
Draft Response
↓
Human Approval
↓
Final Email
MVP Output

The MVP should generate a structured lead table:

Company	Country	Website	Email	Contact Person	Lead Score	Qualification Reason	Email Status
MVP Success Criteria

The MVP will be considered successful if it can:

Generate 10 qualified automotive end-user leads
Extract publicly available contact information
Avoid distributors and suppliers
Send the first outreach email
Track email status in a structured format
Current Progress
 Sprint 1 - Lead Discovery Agent
 Sprint 2 - Contact Page Discovery
 Sprint 3 - Email Extraction
 Sprint 4 - Lead Qualification
 Sprint 5 - Lead Scoring
 Sprint 6 - First Email Outreach
 Sprint 7 - Reply Analysis
 Sprint 8 - Product Recommendation
Future Architecture

Future versions may include:

Customer reply monitoring
Response Analysis Agent
Product Recommendation Agent
Catalogue-based retrieval system
Human approval dashboard
CRM integration
Follow-up scheduler
Sales analytics dashboard
```

# AI Sales Operating System - Architecture

**Current version: v0.5 (Lead Registry)**

## Vision

An internal tool for **Genuine Automation Products LLP**'s sales team.
It automates the repetitive parts of prospecting (finding companies,
finding contact info, filtering out junk, scoring leads, drafting
outreach) so engineers spend their time on conversations, not
searching - while keeping a human in control of every outbound action.

Every stage still writes a **CSV checkpoint**: you can inspect,
hand-edit, or re-run any single stage without touching the others.
Nothing is ever sent or acted upon automatically without a human step
in between.

## Modules (one folder = one responsibility)

| Folder                | Responsibility                                                                            | Reads                                            | Writes                                    |
| --------------------- | ----------------------------------------------------------------------------------------- | ------------------------------------------------ | ----------------------------------------- |
| `lead_generation/`    | Find candidate companies via search                                                       | Region, industry, product category, target type  | `data/leads.csv`                          |
| `contact_extraction/` | Visit each company site, find public contact info                                         | `data/leads.csv`                                 | `data/leads_with_contacts.csv`            |
| `lead_qualification/` | Reject junk (quality gate), score the rest                                                | `data/leads_with_contacts.csv`                   | `data/qualified_leads.csv`                |
| `email_generation/`   | Draft (never send) a personalized first email per Qualified lead, using Claude            | `data/qualified_leads.csv` (Qualified rows only) | `data/email_drafts.csv`                   |
| `lead_registry/`      | Persistent master record of every lead ever seen, synced from each stage's CSV checkpoint | All four CSVs above                              | `data/lead_registry.csv`                  |
| `core/`               | Runs each stage as an in-memory function call, still writing that stage's CSV             | Called by `run_pipeline.py`                      | Same four CSVs above                      |
| `run_pipeline.py`     | Interactive menu: run any single stage, run everything, or view the registry              | User menu choice                                 | (delegates to `core/` + `lead_registry/`) |

Planned, not yet built:

| Folder                    | Responsibility                                               |
| ------------------------- | ------------------------------------------------------------ |
| `reply_analyzer/`         | Read/classify prospect replies (future)                      |
| `product_recommendation/` | Suggest which sensor product fits a lead's use case (future) |

## Design rules (unchanged since the project brief)

1. **Never send emails automatically.** Draft first, human approves.
2. **Never guess contact info.** Only use what's publicly published.
3. **Never auto-recommend products.** Draft only, human approves.
4. **Every stage writes a CSV checkpoint.**
5. **Every agent runs independently** - `python -m <package>.run_<name>`
   works standalone, with no dependency on the pipeline runner or the
   registry.

## How a full run works

```
run_pipeline.py  (interactive menu)
      |
      | option 1: Run Full Pipeline
      v
  for each stage:
      core.pipeline.run_<stage>_stage(...)   -> writes that stage's CSV
      lead_registry.registry_sync.sync_<stage>(registry, csv_path)  -> updates data/lead_registry.csv
      print "✓ <Stage> Complete"

  Pipeline Finished Successfully
```

`core/pipeline.py` contains no business logic of its own - it only
calls each agent (`LeadDiscoveryAgent`, `ContactExtractionAgent`,
`LeadQualificationAgent`, `EmailGenerationAgent`) in order and writes
their CSVs. It also has **no knowledge of the Lead Registry** - that
stays a separate concern, synced in by `run_pipeline.py` after each
stage. This split matters: any script that writes one of the four
stage CSVs (whether that's `core/pipeline.py`, or one of the
`run_xxx.py` scripts run standalone) can have its output synced into
the registry independently, by calling the matching
`lead_registry.registry_sync.sync_*()` function against that CSV path.

## The Lead Registry (v0.5)

Before v0.5, the four stage CSVs were the only record of a pipeline
run - each one only reflects the _most recent_ run of that stage, and
running Lead Discovery again would overwrite `leads.csv` with a
different set of companies. There was no single place tracking "what
has ever happened to this lead."

`lead_registry/` fixes that:

- **`models.py`** - the `LeadRecord` dataclass: one row per unique
  company (Lead ID, name, website, country, discovery date, last
  updated, current stage/status, score, qualification status, email
  status, follow-up status, notes).
- **`storage.py`** - `RegistryStorage` (an abstract interface with
  `load_all()`/`save_all()`) and `CsvRegistryStorage` (today's only
  implementation, storing one row per lead in `data/lead_registry.csv`).
- **`lead_registry.py`** - `LeadRegistry`, the business logic: assigns
  a new Lead ID (`L000001`, `L000002`, ...) the first time a website
  domain is seen, returns the existing one on every later sighting, and
  applies stage/status updates in place.
- **`registry_sync.py`** - one function per stage
  (`sync_lead_discovery`, `sync_contact_extraction`,
  `sync_lead_qualification`, `sync_email_generation`), each reading a
  stage's CSV checkpoint and calling `get_or_create()` /
  `update_stage()` for every row. This is the _only_ file that knows
  each stage CSV's specific column names - if a stage's CSV columns
  ever change, only this file needs updating, not `LeadRegistry` itself.

Leads are matched **by website domain**, not by name (company names can
vary slightly between mentions; a normalized domain is a much more
reliable natural key), using the same normalization approach
(lowercase, strip `www.`) already used in `lead_qualification/quality_gate.py`
and `lead_generation/lead_discovery.py`.

### Why CSV now, SQLite later

`LeadRegistry` only ever calls `self.storage.load_all()` /
`self.storage.save_all()` - it never touches a file path or SQL
directly. Migrating to SQLite later means writing one new
`SqliteRegistryStorage` class that implements those two methods against
a database table with the same columns as `REGISTRY_FIELDNAMES`
(defined once, in `models.py`), then constructing
`LeadRegistry(storage=SqliteRegistryStorage(...))` instead of the
default. Nothing in `lead_registry.py`, `registry_sync.py`, or
`run_pipeline.py` would need to change.

## Architecture review notes (v0.5)

A few things worth calling out, evaluated against "does fixing this
clearly improve maintainability" rather than fixed on principle:

- **Fixed:** `core/pipeline.py` used to expose a `run_full_pipeline()`
  convenience function that only chained 3 of the 4 stages. Once
  `run_pipeline.py`'s menu took over full-pipeline orchestration
  (needed anyway, to interleave registry syncs and progress
  checkmarks between stages), that function became dead code that
  could silently drift out of sync with the real 4-stage flow. It's
  been removed in favor of the menu owning that responsibility.
- **Accepted tradeoff, not fixed:** `core/pipeline.py`'s stage
  functions and each package's own `run_xxx.py` script both know how
  to read/write the same CSV shape (e.g. contact fields, qualification
  fields). This is intentional duplication, not an oversight - it's
  what lets every agent run 100% standalone (`python -m
package.run_xxx`, no dependency on `core/`) while also being
  chainable in-memory for a full pipeline run. Sprint 4's stage
  function already resolves the one place this duplication was
  cheapest to remove (it imports `build_output_row`/`save_email_drafts`
  from `email_generation/run_email_generation.py` rather than
  redefining them). Unifying the other three stages the same way is a
  reasonable future cleanup, not urgent today.
- **Known limitation, documented rather than "fixed":** the registry is
  only synced when a stage is run through `run_pipeline.py`'s menu. If
  someone runs `python -m lead_generation.run_lead_discovery` directly,
  `leads.csv` is written correctly but `lead_registry.csv` is not
  updated until that CSV is later synced (e.g. by choosing the matching
  menu option). This keeps every individual agent's script untouched
  and fully backward compatible, at the cost of the registry only being
  "eventually consistent" rather than always current. Worth revisiting
  if standalone script usage becomes the norm rather than the
  exception.

## Why rule-based first, AI later

Deterministic tasks (does this domain match a blocklist? does this text
contain "distributor"?) are handled with plain Python - fast, free,
and fully explainable to a sales engineer asking "why was this
rejected?". Claude is reserved for the one stage that genuinely needs
language generation (drafting a personalized email) - not as a blanket
replacement for logic that a simple rule already handles reliably.
