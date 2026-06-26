# Design Decisions

This document records important architectural and engineering decisions made during the development of the AI Sales Agent.

The purpose is to explain _why_ specific design choices were made.

---

# Decision 1

## Multi-Agent Architecture

### Decision

Build the system as multiple specialized AI agents instead of one large AI agent.

### Why?

Each agent has a single responsibility.

This makes the project:

- Easier to maintain
- Easier to debug
- Easier to extend
- Easier to test

---

# Decision 2

## Human-in-the-Loop

### Decision

Allow the AI to automatically send only the first introductory email.

Require human approval for all commercial communication after that.

### Why?

The first email is generic.

Later conversations involve:

- Technical discussions
- Pricing
- Quotations
- Product selection

These require human judgment.

---

# Decision 3

## Public Data Only

### Decision

Use only publicly available information.

### Why?

The project should respect privacy and avoid collecting private contact information.

---

# Decision 4

## Focus on End Users

### Decision

Target only industrial end-user companies.

### Why?

The business objective is to generate new customers rather than identify distributors or suppliers.

---

# Decision 5

## Modular Development

### Decision

Build one agent at a time.

### Why?

Each completed agent becomes independently testable and reduces overall project risk.

---

# Decision 6

## Knowledge-Based Product Recommendation (Future)

### Decision

Future product recommendations will be generated using the company's catalogue and technical datasheets rather than relying solely on the language model.

### Why?

This improves accuracy, keeps recommendations aligned with company products, and makes responses easier to verify.

---

This document will continue to evolve throughout the project.
