"""
Quick Serper.dev (Google Search API) lookup tool.

Usage:
  python serper_search.py "exact search phrase"

Reads SERPER_API_KEY from .env in this directory. Prints the answer box
(if any), organic results, and knowledge graph info -- the closest
equivalent to what a human sees on google.com including AI Overview-style
answer boxes, which this project's other search tools cannot access.
"""
import argparse
import json
import os
import sys

import requests


def load_env():
    env_path = os.path.join(os.path.dirname(__file__), ".env")
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    os.environ.setdefault(k.strip(), v.strip())


def search(query, api_key):
    resp = requests.post(
        "https://google.serper.dev/search",
        headers={"X-API-KEY": api_key, "Content-Type": "application/json"},
        json={"q": query},
        timeout=20,
    )
    resp.raise_for_status()
    return resp.json()


def main():
    parser = argparse.ArgumentParser(description="Serper.dev Google Search lookup")
    parser.add_argument("query", help="Exact search phrase")
    parser.add_argument("--raw", action="store_true", help="Print full raw JSON")
    args = parser.parse_args()

    load_env()
    api_key = os.environ.get("SERPER_API_KEY")
    if not api_key:
        print("SERPER_API_KEY not set (checked .env and environment)", file=sys.stderr)
        sys.exit(1)

    data = search(args.query, api_key)

    if args.raw:
        print(json.dumps(data, indent=2))
        return

    print(f"Query: {args.query}\n")

    if "answerBox" in data:
        ab = data["answerBox"]
        print("=== ANSWER BOX ===")
        print(json.dumps(ab, indent=2))
        print()

    if "knowledgeGraph" in data:
        kg = data["knowledgeGraph"]
        print("=== KNOWLEDGE GRAPH ===")
        print(json.dumps(kg, indent=2))
        print()

    if "organic" in data:
        print("=== ORGANIC RESULTS ===")
        for i, r in enumerate(data["organic"][:10], 1):
            print(f"{i}. {r.get('title')}")
            print(f"   {r.get('link')}")
            if r.get("snippet"):
                print(f"   {r['snippet']}")
            print()


if __name__ == "__main__":
    main()
