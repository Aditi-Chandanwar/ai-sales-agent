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
Lead Discovery Agent	Finds companies matching the target region and industry	Region, Industry, Product Category	List of potential companies
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


Agent Details

1. Lead Discovery Agent

Purpose:

Find companies that match the selected region, industry, and product category.

Inputs:

Region / Country
Industry
Product Category
Lead Count

Example input:

Find 10 automotive end-user companies in Germany that may use industrial sensors.

Possible data sources:

Search engines
Business directories
Industry associations
Company websites
Public company listings

Output:

Company Name
Website
Country
Source URL

2. Lead Qualification Agent

Purpose:

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

Purpose:

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

Purpose:

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

Purpose:

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
