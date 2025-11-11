# miner.py
import argparse
import json
import os
import re
import hashlib
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup
import yaml
from datetime import datetime
from models import ArticleModel
import urllib.robotparser

HEADERS = {"User-Agent": "PanaceIA-WebMiner/1.0 (+mailto:you@example.com)"}

def check_robots(url):
    parsed = urlparse(url)
    robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
    rp = urllib.robotparser.RobotFileParser()
    try:
        rp.set_url(robots_url)
        rp.read()
        allowed = rp.can_fetch(HEADERS["User-Agent"], url)
        return allowed
    except Exception:
        # if robots unavailable, be conservative and allow (or you may choose to disallow)
        return True

def fetch_html(url, timeout=15):
    resp = requests.get(url, headers=HEADERS, timeout=timeout)
    resp.raise_for_status()
    return resp.text

def join_nodes_text(nodes, join_with):
    texts = [n.get_text(strip=True) for n in nodes if n.get_text(strip=True)]
    if join_with is None:
        return texts[0] if texts else None
    # interpret join_with as literal string (not regex)
    return join_with.join(texts) if texts else None

def apply_regex(value, regex):
    if value is None or regex is None:
        return value
    m = re.search(regex, value)
    if not m:
        return None
    # if capture groups exist, return first group, else full match
    return m.group(1) if m.groups() else m.group(0)

def extract_fields(soup, schema, request_url):
    out = {}
    for field in schema.get("fields", []):
        name = field["name"]
        if field.get("source") == "request_url":
            out[name] = request_url
            continue

        selector = field.get("selector")
        attribute = field.get("attribute")
        join_with = field.get("join_with")
        regex = field.get("regex")
        value = None

        if selector:
            nodes = soup.select(selector)
            if not nodes:
                value = None
            else:
                if attribute:
                    # collect attribute values
                    vals = [n.get(attribute) for n in nodes if n.get(attribute)]
                    value = join_with.join(vals) if join_with and vals else (vals[0] if vals else None)
                else:
                    value = join_nodes_text(nodes, join_with)
        else:
            value = None

        if isinstance(value, str) and regex:
            value = apply_regex(value, regex)

        out[name] = value
    return out

def save_raw_html(output_dir, url, html):
    os.makedirs(output_dir, exist_ok=True)
    digest = hashlib.sha1(url.encode("utf-8")).hexdigest()
    fname = os.path.join(output_dir, f"{digest}.html")
    with open(fname, "w", encoding="utf-8") as f:
        f.write(html)
    return fname

def main():
    parser = argparse.ArgumentParser(description="Minimal schema-driven static web miner")
    parser.add_argument("--schema", required=True, help="Path to schema YAML file")
    parser.add_argument("--url", required=True, help="URL to scrape")
    parser.add_argument("--out", default="outputs/result.json", help="JSON output path")
    parser.add_argument("--rawdir", default="outputs/raw", help="Directory to save raw HTML")
    args = parser.parse_args()

    with open(args.schema, "r", encoding="utf-8") as f:
        schema = yaml.safe_load(f)

    # robots check
    allowed = check_robots(args.url)
    if not allowed:
        print(f"[ERROR] robots.txt disallows scraping {args.url} for user-agent {HEADERS['User-Agent']}")
        return

    html = fetch_html(args.url)
    soup = BeautifulSoup(html, "lxml")

    extracted = extract_fields(soup, schema, args.url)

    # Save raw HTML
    raw_path = save_raw_html(args.rawdir, args.url, html)

    # Validate using Pydantic model
    try:
        validated = ArticleModel(**extracted)
    except Exception as e:
        print("[VALIDATION ERROR]", e)
        # still save extracted output for inspection
        os.makedirs(os.path.dirname(args.out), exist_ok=True)
        with open(args.out, "w", encoding="utf-8") as outf:
            json.dump({"schema": schema.get("schema_name"), "extracted": extracted, "raw_html": raw_path}, outf, ensure_ascii=False, indent=2, default=str)
        return

    # write final JSON
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as outf:
        json.dump({"schema": schema.get("schema_name"), "item": validated.dict(), "raw_html": raw_path, "fetched_at": datetime.utcnow().isoformat()}, outf, ensure_ascii=False, indent=2, default=str)

    print(f"[OK] saved {args.out} and raw html at {raw_path}")

if __name__ == "__main__":
    main()
