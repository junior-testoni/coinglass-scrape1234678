"""Simple scraper for Coinglass public API.

This script demonstrates how to retrieve a few example indicators from the
Coinglass open API and write them to CSV files. The endpoints and field
names used here are based on public documentation and may require
adjustments if Coinglass changes their API.

A Coinglass API key can be provided via the ``--api-key`` option if
the endpoint requires authentication.
"""

import argparse
import csv
import json
import os
from api_utils import fetch



# Example endpoints. Additional endpoints can be added to this mapping.
# Each entry contains the endpoint path and a list of required parameters.
ENDPOINTS = {
    "fear_and_greed_history": {
        "path": "/api/index/fear-greed-history",
        "params": [],
    },
    # Funding rates typically require a symbol parameter
    "funding_rates": {
        "path": "/api/futures/funding-rate/history",
        "params": ["symbol"],
    },
    # Open interest history also expects a symbol
    "open_interest_history": {
        "path": "/api/futures/open-interest/history",
        "params": ["symbol"],
    },
    # Options max pain requires both symbol and exchange
    "option_max_pain": {
        "path": "/api/option/max-pain",
        "params": ["symbol", "exchange"],
    },
}




def save_list_of_dicts(items: list[dict], filepath: str) -> None:
    """Write a list of dictionaries to ``filepath`` as CSV."""
    if not items:
        return
    fieldnames = list(items[0].keys())
    with open(filepath, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(items)


def main() -> None:
    parser = argparse.ArgumentParser(description="Scrape data from Coinglass and store as CSV files")
    env_key = os.getenv("COINGLASS_API_KEY")
    parser.add_argument("--api-key", help="Coinglass API key")
    parser.add_argument("--exchange", help="Exchange for option data", default="Deribit")
    parser.add_argument("--symbol", help="Symbol to query (e.g. BTC)", default="BTC")
    parser.add_argument("--output-dir", help="Directory to store CSV files", default="data")
    args = parser.parse_args()

    api_key = args.api_key or env_key
    if not api_key:
        parser.error("An API key is required. Use --api-key or set COINGLASS_API_KEY.")

    os.makedirs(args.output_dir, exist_ok=True)

    for name, meta in ENDPOINTS.items():
        endpoint = meta["path"]
        params = {p: getattr(args, p) for p in meta.get("params", [])}
        try:
            data = fetch(endpoint, params=params, api_key=api_key)
            if isinstance(data, dict):
                content = data.get("data") or data
            else:
                content = data
            if isinstance(content, list):
                save_list_of_dicts(content, os.path.join(args.output_dir, f"{name}.csv"))
                print(f"Saved {name} data to {name}.csv")
            else:
                print(f"Unexpected format for {name}: {content}")
        except Exception as exc:
            print(f"Failed to fetch {name}: {exc}")


if __name__ == "__main__":
    main()
