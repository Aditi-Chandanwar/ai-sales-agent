"""
run_lead_discovery.py

A simple, runnable demo showing how to use LeadDiscoveryAgent end-to-end
with the LeadDiscoveryRequest dataclass. This is a demo script, not a
unit test.

Run it with:
    python -m lead_generation.run_lead_discovery

Make sure you have a .env file in the project root with:
    TAVILY_API_KEY=your_key_here
"""

from dotenv import load_dotenv

from lead_generation.lead_discovery import LeadDiscoveryAgent, LeadDiscoveryRequest

# Load TAVILY_API_KEY (and any other env vars) from a .env file
load_dotenv()


def main():
    # --- Example MVP input (matches the business use case) ---
    # Instead of passing 5 separate arguments around, we bundle them into
    # one LeadDiscoveryRequest object. This keeps the agent's method
    # signature stable even if we add more fields later (Sprint 2+).
    request = LeadDiscoveryRequest(
        region="Germany",
        industry="Automotive",
        lead_count=10,
        product_category="Industrial sensors",
        target_type="End users only",
    )

    print("Starting Lead Discovery Agent")
    print(f"Region: {request.region} | Industry: {request.industry} | Target: {request.target_type}")
    print("-" * 50)

    agent = LeadDiscoveryAgent()

    leads = agent.discover(request)

    agent.save_to_csv(leads, output_path="data/leads.csv")

    print("-" * 50)
    print("Done. Check data/leads.csv for results.")


if __name__ == "__main__":
    main()
