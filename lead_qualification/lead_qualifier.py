"""
lead_qualifier.py

LeadQualificationAgent: applies a strict quality gate FIRST (see
quality_gate.py) to filter out obvious non-leads (Wikipedia, YouTube,
stock photo sites, PDFs, directories/portals, etc). Only leads that
pass the gate get scored with the rule-based logic in scoring_rules.py.

Adds these fields to every lead:
    - score                    (0-100)
    - qualification_status     (Qualified / Review / Rejected)
    - qualification_reason     (human-readable summary of why)
    - risk_flags                (specific red flags found, e.g. distributor)

No AI/LLM here on purpose - pure rule-based logic for Sprint 3. An
LLM-based classifier could be layered on top of this later without
changing the CSV shape.
"""

from lead_qualification import scoring_rules as rules
from lead_qualification import quality_gate


class LeadQualificationAgent:
    """Filters junk leads, then scores and qualifies the rest using simple, explainable rules."""

    def qualify_lead(self, lead: dict) -> dict:
        """
        Qualify a single lead (a dict of CSV columns) and return a NEW
        dict with all original fields preserved, plus the new
        qualification fields added. The original `lead` dict is never
        modified.
        """
        # --------------------------------------------------------------
        # Step 1: Quality gate - hard-reject obvious non-leads BEFORE
        # any scoring happens. This is what stops Wikipedia/YouTube/PDF/
        # directory pages from sneaking through just because they
        # happen to contain a keyword like "automotive" or "OEM".
        # --------------------------------------------------------------
        gate_reason = quality_gate.apply_quality_gate(lead)

        if gate_reason:
            enriched = dict(lead)
            enriched["score"] = 0
            enriched["qualification_status"] = "Rejected"
            enriched["qualification_reason"] = f"Rejected by quality gate: {gate_reason}"
            enriched["risk_flags"] = gate_reason
            return enriched

        # --------------------------------------------------------------
        # Step 2: Normal rule-based scoring (only reached if the lead
        # passed the quality gate above).
        # --------------------------------------------------------------
        score = 0
        positive_reasons = []
        risk_flags = []

        # Run every scoring rule and accumulate points + reasons
        for rule in rules.SCORING_RULES:
            points, reason = rule(lead)

            if points == 0 or not reason:
                continue  # rule didn't apply to this lead

            score += points

            if points > 0:
                positive_reasons.append(reason)
            else:
                # Negative points represent risk flags (distributor,
                # directory/listing site, missing contact info, etc.)
                risk_flags.append(reason)

        final_score = rules.clamp_score(score)
        status = rules.qualification_status(final_score)

        # Build a short, human-readable explanation of the score
        reason_parts = []
        if positive_reasons:
            reason_parts.append("Positive: " + "; ".join(positive_reasons))
        if risk_flags:
            reason_parts.append("Risks: " + "; ".join(risk_flags))
        qualification_reason = " | ".join(reason_parts) if reason_parts else "No strong signals found"

        # Copy the original lead so we never mutate the caller's dict,
        # then add the new qualification fields.
        enriched = dict(lead)
        enriched["score"] = final_score
        enriched["qualification_status"] = status
        enriched["qualification_reason"] = qualification_reason
        enriched["risk_flags"] = "; ".join(risk_flags) if risk_flags else ""

        return enriched

    def qualify_leads(self, leads: list) -> list:
        """Score a list of lead dicts, returning a new list of enriched dicts."""
        return [self.qualify_lead(lead) for lead in leads]

