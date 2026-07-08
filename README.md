# AI Sales Operating System - Genuine Automation Products LLP

**Current version: v0.5 (Lead Registry)**

An evolving internal sales-automation system: discovers industrial
end-user leads, filters out junk, scores what's left, drafts outreach
emails for human review, and now keeps a persistent master record of
every lead across every run.

| Version  | What it does                                                                                                   |
| -------- | -------------------------------------------------------------------------------------------------------------- |
| v0.1     | **Lead Discovery** - find candidate companies via the Tavily Search API                                        |
| v0.2     | **Contact Extraction** - visit each company's site, find public emails/phones                                  |
| v0.3     | **Lead Qualification** - quality gate + rule-based scoring (Qualified/Review/Rejected)                         |
| v0.4     | **Email Draft Generation** - Claude drafts a first-contact email per Qualified lead (never sent)               |
| **v0.5** | **Lead Registry** _(current)_ - a persistent master database of every lead, plus a menu-driven pipeline runner |

Planned:

| Version | What it will do                 |
| ------- | ------------------------------- |
| v0.6    | Dashboard                       |
| v0.7    | Email Sending (human-triggered) |
| v0.8    | Reply Analysis                  |
| v0.9    | Product Recommendation          |
| v1.0    | Genuine Automation Pilot        |

**v0.1:** Lead Discovery Agent for **Genuine Automation Products LLP**
(industrial sensors: inductive, capacitive, photoelectric, magnetic,
ultrasonic, fluid level). Uses the **Tavily Search API** to find potential
**end-user** companies (factories/manufacturers) in a given region and
industry - not distributors, traders, or resellers.

**v0.2:** Contact Extraction Agent. Takes the leads found in v0.1,
visits each company's public website, and extracts publicly available
email addresses and phone numbers from likely contact/about/imprint pages.

**v0.3:** Lead Qualification and Scoring Agent. Takes the enriched
leads from v0.2 and scores each one with simple, explainable
rule-based logic - flagging likely distributors/directories and
highlighting strong end-user leads, without using any AI/LLM yet.

**v0.4:** Email Draft Generation Agent. Takes only the **Qualified**
leads from v0.3 and drafts a personalized first-contact email per
lead using Claude - for human review only. **This step never sends
anything.**

**v0.5:** Lead Registry. Every lead discovered across every run gets a
stable Lead ID and a persistent record (`data/lead_registry.csv`)
tracking its current stage, status, score, and follow-up state -
instead of that history being overwritten each time a stage's CSV
checkpoint is regenerated. Also replaces the old single-shot
`run_pipeline.py` with an interactive menu so you can run the whole
pipeline, or any single stage, or just check the registry.

## Project structure

```
lead_generation/
    __init__.py
    search_provider.py      # TavilySearchProvider - talks to Tavily API
    lead_discovery.py       # LeadDiscoveryAgent - builds queries, dedups, saves CSV
    run_lead_discovery.py   # Runnable demo (not a unit test)
contact_extraction/
    __init__.py
    website_scraper.py         # WebsiteScraper - fetches HTML for a URL
    contact_page_finder.py     # ContactPageFinder - finds likely contact/about pages
    email_extractor.py         # EmailExtractor - regex-based email & phone extraction
    run_contact_extraction.py  # Runnable demo - ties it all together, updates the CSV
lead_qualification/
    __init__.py
    quality_gate.py              # Hard-rejection checks (blocked domains, PDFs, directories) - runs FIRST
    scoring_rules.py             # Rule-based scoring functions (points, keywords, thresholds)
    lead_qualifier.py            # LeadQualificationAgent - applies gate, then rules, adds score/status
    run_lead_qualification.py    # Runnable demo - reads, qualifies, writes CSV, prints summary
email_generation/
    __init__.py
    email_templates.py          # Static company facts + safe fallback email template
    prompt_builder.py           # Builds the Claude prompt (isolated from API-calling code)
    email_generator.py          # ClaudeClient + EmailGenerationAgent - drafts one email per lead
    run_email_generation.py     # Runnable demo - filters Qualified leads, drafts, writes CSV
lead_registry/
    __init__.py
    models.py                # LeadRecord dataclass + registry CSV column order
    storage.py                # RegistryStorage interface + CsvRegistryStorage (today's backend)
    lead_registry.py          # LeadRegistry - Lead ID assignment, dedup by domain, stage updates
    registry_sync.py          # Reads each stage's CSV checkpoint and updates the registry
core/
    __init__.py
    pipeline.py              # Runs each stage (Lead Discovery -> ... -> Email Draft Generation)
docs/
    ARCHITECTURE.md          # System design overview
data/
    leads.csv                  # v0.1 output
    leads_with_contacts.csv    # v0.2 output
    qualified_leads.csv        # v0.3 output
    email_drafts.csv           # v0.4 output
    lead_registry.csv          # v0.5 output - persistent master record of every lead
run_pipeline.py             # Interactive menu: run any stage, run everything, or view the registry
requirements.txt
.env.example
```

## Quickstart: the interactive pipeline menu

Once set up (see below), run:

```bash
python run_pipeline.py
```

You'll see:

```
==================================
AI SALES OPERATING SYSTEM
==================================

1. Run Full Pipeline
2. Lead Discovery
3. Contact Extraction
4. Lead Qualification
5. Email Draft Generation
6. View Registry Summary
0. Exit
```

- **Option 1 (Run Full Pipeline)** asks for region/industry/lead count
  (with sensible defaults on Enter), then runs all four stages in
  order, printing a `✓ ... Complete` line after each one, and syncing
  the Lead Registry as it goes.
- **Options 2-5** run one stage on its own, reading whatever checkpoint
  CSV the previous stage left behind - handy for debugging a single
  stage, or re-running just one part after hand-editing a CSV.
- **Option 6** prints a summary of the Lead Registry: how many leads
  are tracked in total, broken down by current stage, qualification
  status, and email status.

Every stage still writes its own CSV checkpoint, exactly as before, so
you can open `data/leads.csv`, `data/leads_with_contacts.csv`,
`data/qualified_leads.csv`, or `data/email_drafts.csv` at any point to
see (or hand-edit) what happened at that stage. `data/lead_registry.csv`
is the new persistent record tying all of it together across runs -
see "v0.5: Lead Registry" below.

## Setup

1. Create a virtual environment and install dependencies:

   ```bash
   python -m venv venv
   source venv/bin/activate      # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. Get a Tavily API key from https://tavily.com and copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```
   Then edit `.env` and paste in your key(s):
   ```
   TAVILY_API_KEY=tvly-xxxxxxxxxxxxxxxx
   ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxxxxx
   ```
   `TAVILY_API_KEY` is only needed for v0.1 (lead discovery).
   `ANTHROPIC_API_KEY` is only needed for v0.4 (email drafting).

Then either run `python run_pipeline.py` (Quickstart above) for the
interactive menu, or run each stage's script individually as shown
below - useful for debugging one stage, or re-running just one part
after hand-editing a checkpoint CSV. See `docs/ARCHITECTURE.md` for
how the pieces fit together.

## v0.1: Run lead discovery

```bash
python -m lead_generation.run_lead_discovery
```

This runs the example (Germany / Automotive / Industrial sensors / End users
only) and writes results to `data/leads.csv`.

## Using it in your own code

Search criteria are now bundled into a `LeadDiscoveryRequest` object, and
results come back as a list of `Lead` objects (instead of plain dicts):

```python
from dotenv import load_dotenv
from lead_generation.lead_discovery import LeadDiscoveryAgent, LeadDiscoveryRequest

load_dotenv()

agent = LeadDiscoveryAgent()

request = LeadDiscoveryRequest(
    region="Germany",
    industry="Automotive",
    lead_count=10,
    product_category="Industrial sensors",
    target_type="End users only",
)

leads = agent.discover(request)          # note: discover(), not discover_leads(...)
agent.save_to_csv(leads, output_path="data/leads.csv")
```

## Output format (`data/leads.csv`)

| Column       | Description                                             |
| ------------ | ------------------------------------------------------- |
| company_name | Best guess at company name (from page title)            |
| website      | Full normalized website URL, e.g. `https://example.com` |
| country      | The region passed in (e.g. "Germany")                   |
| source_url   | Exact URL the lead was found at                         |
| search_query | Which search query produced this result                 |
| notes        | Short content snippet, for manual review                |

## v0.2: Run contact extraction

Once `data/leads.csv` exists (from v0.1), enrich it with public contact
details:

```bash
python -m contact_extraction.run_contact_extraction
```

This reads `data/leads.csv`, visits each lead's website, and writes
`data/leads_with_contacts.csv` with emails and phone numbers found on
the homepage and any likely contact/about/imprint pages.

### How it works

1. **`WebsiteScraper`** fetches a URL's HTML with a realistic browser
   User-Agent and a timeout, returning `""` on any failure instead of
   crashing.
2. **`ContactPageFinder`** scans the homepage's links for anything whose
   text or URL contains a keyword like `contact`, `about`, `imprint`, or
   `locations`, and turns relative links (e.g. `/contact`) into full
   absolute URLs. It caps the number of candidate pages per site.
3. **`EmailExtractor`** runs regex over the combined homepage + contact
   page HTML to pull out email addresses and phone numbers, removing
   duplicates and filtering out obvious placeholder emails like
   `example@example.com`.
4. **`ContactExtractionAgent`** (in `run_contact_extraction.py`) wires
   these three together for one website, and `main()` loops over every
   row in `leads.csv`, writing the enriched CSV.

### Using it in your own code

```python
from contact_extraction.run_contact_extraction import ContactExtractionAgent

agent = ContactExtractionAgent()
result = agent.extract_contacts_for_website("https://example.com")
# result = {"contact_pages": [...], "emails": [...], "phones": [...]}
```

### Output format (`data/leads_with_contacts.csv`)

Includes every v0.1 column, plus:

| Column        | Description                                                 |
| ------------- | ----------------------------------------------------------- |
| contact_pages | `; `-separated list of contact/about page URLs checked      |
| emails        | `; `-separated list of public emails found (deduped)        |
| phones        | `; `-separated list of public phone numbers found (deduped) |

## v0.3: Run lead qualification & scoring

Once `data/leads_with_contacts.csv` exists (from v0.2), score and
qualify each lead:

```bash
python -m lead_qualification.run_lead_qualification
```

This reads `data/leads_with_contacts.csv`, scores every lead with simple
rule-based logic (see below), and writes `data/qualified_leads.csv` with
the added columns `score`, `qualification_status`, `qualification_reason`,
and `risk_flags`. It also prints a summary (total / qualified / review /
rejected counts).

If `data/leads_with_contacts.csv` doesn't exist yet, the script falls
back to a small built-in sample of 3 leads so you can see it work
end-to-end before running v0.1 and v0.2 for real.

### Quality gate (runs before scoring)

Keyword scoring alone was letting junk through - a Wikipedia article or
YouTube video about "automotive manufacturing" would still rack up
scoring points just for containing the right words. `quality_gate.py`
hard-rejects these before any scoring happens:

- **Blocked domains** - Wikipedia, YouTube, stock photo sites
  (iStock/Shutterstock/Unsplash), lead-data tools (Lusha, ZoomInfo,
  ensun), industry portals (MarkLines, ACEA), and social media
  (LinkedIn, Facebook, Instagram, X/Twitter)
- **PDF results** - `source_url` ending in `.pdf` (industry reports,
  not company websites)
- **Directory/content-site language** - company name or notes containing
  things like "directory", "listing", "portal", "top 100", "company
  search", "sales leads", "industry report", "interactive map"

A lead that hits any of these gets `score = 0`,
`qualification_status = "Rejected"`, and a
`qualification_reason` starting with `"Rejected by quality gate: ..."`

- it never reaches the normal scoring rules below. Only leads that pass
  the gate get scored.

### How scoring works (for leads that pass the quality gate)

No AI/LLM is used - just keyword checks and point values, defined in
`scoring_rules.py`. Starting from 0:

**Points added:**
| Signal | Points |
|---|---|
| Notes/company/query mention manufacturing, factory, plant, production, assembly, OEM, automotive parts, or machine builder | +30 |
| Industry/search query mentions automotive | +20 |
| Website present | +15 |
| Email(s) found | +15 |
| Phone(s) found | +10 |
| Contact page(s) found | +10 |

**Points subtracted (risk flags):**
| Signal | Points |
|---|---|
| Mentions distributor, reseller, trader, supplier, dealer, catalog, or online store | -40 |
| Website/source/notes look like a directory, listing, news site, or job board | -20 |
| No email AND no phone found at all | -20 |

The total is clamped to a 0-100 range, then mapped to a status:

| Score | Status        |
| ----- | ------------- |
| >= 60 | **Qualified** |
| 40-59 | **Review**    |
| < 40  | **Rejected**  |

`qualification_reason` summarizes which positive signals and risk flags
contributed to the score, and `risk_flags` lists just the negative ones,
so a human reviewer can quickly see _why_ a lead landed where it did.

### Using it in your own code

```python
from lead_qualification.lead_qualifier import LeadQualificationAgent

agent = LeadQualificationAgent()
qualified_leads = agent.qualify_leads(list_of_lead_dicts)
# each dict now also has: score, qualification_status, qualification_reason, risk_flags
```

### Output format (`data/qualified_leads.csv`)

Includes every v0.1 + v0.2 column, plus:

| Column               | Description                                                                                |
| -------------------- | ------------------------------------------------------------------------------------------ |
| score                | Final score, 0-100 (always 0 if rejected by the quality gate)                              |
| qualification_status | `Qualified`, `Review`, or `Rejected`                                                       |
| qualification_reason | Human-readable summary of positive signals and risks, or the quality-gate rejection reason |
| risk_flags           | `; `-separated list of just the negative/risk signals found                                |

## v0.4: Run email draft generation

**Purpose:** Draft a personalized first-contact email for every
**Qualified** lead, using Claude - for a human to review and send
manually. This step **never sends anything** - there is no SMTP,
Gmail, or Outlook code anywhere in `email_generation/`.

**Input:** `data/qualified_leads.csv` (v0.3 output). Only rows
where `qualification_status == "Qualified"` are processed - `Review`
and `Rejected` rows are read but skipped.

**Output:** `data/email_drafts.csv`, with these columns (designed to
support a future dashboard tracking drafts, approvals, sends, and
follow-ups):

| Column               | Description                                                          | Default          |
| -------------------- | -------------------------------------------------------------------- | ---------------- |
| company_name         | From the lead                                                        | -                |
| website              | From the lead                                                        | -                |
| email                | First email address found for the lead (v0.2 may have found several) | -                |
| country              | From the lead                                                        | -                |
| lead_score           | The lead's score from v0.3                                           | -                |
| qualification_reason | Why v0.3 qualified this lead                                         | -                |
| subject              | Drafted email subject line                                           | -                |
| email_draft          | Drafted email body                                                   | -                |
| approval_status      | Human review status                                                  | `Pending Review` |
| email_status         | Whether it's been sent (set by a future step, not this one)          | `Not Sent`       |
| draft_created_at     | UTC timestamp when the draft was generated                           | (current time)   |
| approved_by          | Who approved it (set by a future step)                               | _(empty)_        |
| sent_at              | When it was sent (set by a future step)                              | _(empty)_        |
| follow_up_status     | Follow-up tracking (set by a future step)                            | `Not Started`    |
| notes                | Free-text notes for a human reviewer                                 | _(empty)_        |

### How to run

```bash
python -m email_generation.run_email_generation
```

If `data/qualified_leads.csv` doesn't exist yet, this falls back to a
small built-in sample (one Qualified lead, one Rejected lead) so you
can see the filtering and drafting work before running v0.1-v0.3 for
real.

### How it works

1. **`email_templates.py`** holds the only facts about Genuine
   Automation Products LLP that ever reach the prompt (`COMPANY_NAME`,
   `COMPANY_BLURB`), plus a safe static fallback email used only if
   Claude can't be reached.
2. **`prompt_builder.py`** builds the exact prompt sent to Claude,
   personalizing with only `company_name`, `country`, a best-effort
   `industry` hint (derived from the lead's `search_query`, since
   there's no dedicated industry column yet), and `qualification_reason`.
   The prompt explicitly lists what Claude must NOT do: mention
   pricing/quotes, promise compatibility, or invent facts/needs.
3. **`email_generator.py`** contains `ClaudeClient` (calls the
   Anthropic Messages API, same request/error-handling pattern as
   `TavilySearchProvider`) and `EmailGenerationAgent` (calls the prompt
   builder, then the Claude client, then falls back to the static
   template if the API call fails or returns something unparseable).
4. **`run_email_generation.py`** reads the CSV, filters to `Qualified`
   only, drafts one email per lead, and writes `data/email_drafts.csv`
   with every row defaulted to `Pending Review` / `Not Sent`.

### Using it in your own code

```python
from email_generation.email_generator import EmailGenerationAgent

agent = EmailGenerationAgent()
draft = agent.generate_email_for_lead(lead_dict)
# draft = {"subject": "...", "email_draft": "..."}
```

### Known limitations (v0.4)

- No dedicated `industry` column exists yet in the CSV pipeline, so the
  prompt uses the lead's `search_query` as a best-effort industry hint
  - it's usually accurate (e.g. "automotive assembly plants Germany")
    but is a proxy, not a real field.
- If a lead has multiple emails (from v0.2), only the first one is
  carried into `email_drafts.csv`'s `email` column.
- If the Claude API call fails (bad key, network issue, rate limit),
  the lead still gets a draft - but a generic static fallback template
  rather than a personalized one. Worth spot-checking `email_draft` for
  any row where the subject is exactly "Introduction from Genuine
  Automation Products LLP" (the fallback's fixed subject).
- No email sending, no approval workflow UI, and no CRM integration
  yet - `approval_status`, `email_status`, `approved_by`, `sent_at`,
  and `follow_up_status` are all placeholder columns for a future
  dashboard/approval step to update.
- As of v0.5, `python run_pipeline.py`'s "Run Full Pipeline" option
  _does_ include this stage - it still only ever drafts, never sends.
  Running `python -m email_generation.run_email_generation` directly
  still works too, for drafting emails without re-running earlier
  stages.

## v0.5: Lead Registry

**Purpose:** Every lead ever discovered gets a stable **Lead ID**
(`L000001`, `L000002`, ...) and a persistent record in
`data/lead_registry.csv` - unlike the per-stage checkpoint CSVs, which
only reflect the most recent run, the registry accumulates history
across every run, keyed by website domain so the same company is
recognized (not duplicated) no matter how many times it's found again.

**Registry columns:** Lead ID, Company Name, Website, Country,
Discovery Date, Last Updated, Current Stage, Current Status, Lead
Score, Qualification Status, Email Status, Follow-up Status, Notes.

**How it's kept up to date:** `python run_pipeline.py`'s menu syncs the
registry automatically after each stage - whether you run the full
pipeline (option 1) or a single stage (options 2-5). Under the hood,
`lead_registry/registry_sync.py` reads that stage's CSV checkpoint
(e.g. `data/qualified_leads.csv`) and updates the matching lead's
record.

### View the registry

```bash
python run_pipeline.py
# then choose option 6
```

Prints total leads tracked, plus breakdowns by current stage,
qualification status, and email status.

### Using it in your own code

```python
from lead_registry.lead_registry import LeadRegistry

registry = LeadRegistry()
record = registry.get_or_create("Mercedes-Benz Group AG", "https://www.mercedes-benz.com", "Germany")
print(record["lead_id"])  # e.g. "L000001" - same ID every time this domain is seen again

registry.update_stage(
    website="https://www.mercedes-benz.com",
    stage="Lead Qualification",
    qualification_status="Qualified",
    lead_score="100",
)
```

### Why CSV now, SQLite later

`LeadRegistry` never touches a file path directly - it only calls
`storage.load_all()` / `storage.save_all()` (see
`lead_registry/storage.py`). Migrating to SQLite later means writing
one new storage class implementing those two methods; nothing in
`LeadRegistry` or `registry_sync.py` would need to change. See
`docs/ARCHITECTURE.md` for more detail.

### Known limitations (v0.5)

- The registry is only synced when a stage is run through
  `run_pipeline.py`'s menu. Running a stage's script directly (e.g.
  `python -m lead_generation.run_lead_discovery`) still writes that
  stage's CSV correctly, but won't update `lead_registry.csv` until
  it's later synced via the matching menu option.
- Matching is by website domain only - two records for the same
  company under genuinely different domains (e.g. a regional subsidiary
  site) won't be merged automatically.
- No dashboard yet reads from this registry (planned for v0.6) - today
  it's viewable only via the CLI summary (option 6).

## Known limitations (by design, for v0.1)

- No automatic filtering of distributors/traders vs. true end users -
  query wording nudges toward end users (assembly plants, production
  facilities, "factories using industrial sensors", etc.), but results
  should still be spot-checked using the `notes` column.
- No email/contact extraction yet (planned for a later sprint).
- No CRM integration or lead scoring yet.
- Dedup is by website domain only.

## Known limitations (v0.2)

- Only extracts **publicly visible** emails/phones already printed on the
  page - never guesses addresses like `first.last@domain.com`.
- Only checks the homepage plus up to a few likely contact pages (capped
  per site), not the whole website.
- Some sites block scrapers, use JavaScript-rendered content, or require
  cookie consent before showing content - these will simply come back
  empty rather than causing an error.
- Phone number matching uses a loose regex and may occasionally pick up
  non-phone numeric strings (e.g. long reference numbers).
- No AI/LLM logic, no email sending, and no lead qualification/scoring
  yet - these are intentionally left for later sprints.

## Known limitations (v0.3)

- The quality gate uses a fixed blocklist of domains and keywords - a
  junk source we haven't seen yet (a new directory site, a different
  video platform) won't be caught until it's added to
  `quality_gate.py`. It's a denylist, not a general "is this a real
  company site" detector.
- **Rule-based only** - scoring relies on simple keyword matching, not
  real language understanding. A distributor that never uses words like
  "distributor" or "reseller" in its scraped text won't be flagged, and
  a genuine manufacturer with unusual phrasing might score lower than
  it should.
- Keyword matching can occasionally produce a false positive - e.g. a
  distributor's page happens to mention "automotive parts" (a positive
  keyword) and still nets some points before the distributor penalty
  brings it back down. The `qualification_reason` field is there so a
  human can see exactly why a score landed where it did.
- Thresholds (60 / 40) and point values are simple starting defaults -
  they're easy to tune in `scoring_rules.py` as you see real results.
- No AI/LLM classification, no email sending, and no CRM/database
  integration yet - intentionally left for a later version.

## Future improvements (post-v0.5)

- **v0.6 Dashboard** - a UI reading from `data/lead_registry.csv` (and
  the individual stage CSVs) so the sales team doesn't need to open
  files directly; natural home for the "View Registry Summary" data
  already available via the CLI.
- **v0.7 Email Sending** - only after human approval, updating
  `email_status`/`sent_at` in both `email_drafts.csv` and the
  registry - still requiring an explicit human trigger, never automatic.
- **v0.8 Reply Analysis** (`reply_analyzer/`) - classify prospect
  replies and update `follow_up_status`.
- **v0.9 Product Recommendation** (`product_recommendation/`) -
  draft-only suggestions for which sensor product fits a lead's use
  case, using the same human-approval pattern as email drafts.
- **v1.0 Genuine Automation Pilot** - deployed internally for the
  sales team to use day to day.
- A real `industry` column upstream in `lead_generation/`, so v0.4's
  prompt doesn't need to guess industry from `search_query` (this
  would also let `lead_registry` track industry, which it doesn't
  today).
- A `SqliteRegistryStorage` implementation once concurrent access or
  querying needs outgrow a single CSV file (see "Why CSV now, SQLite
  later" above - the swap is designed to be small).
- Have every stage's own `run_xxx.py` script sync the registry
  directly (not just the menu), so standalone runs stay consistent
  with menu-driven runs.
