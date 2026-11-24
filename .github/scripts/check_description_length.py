#!/usr/bin/env python3
"""Check changed repository descriptions against the README line limit.

Category line, with the URL hidden:

    - owner/repo — description ☆1,234

visible = 7 + len(link text) + len(description) + len(formatted stars)

The limit is 95. A length of 95 fits; 96 does not. Lengths are UTF-8 bytes,
matching Go's len() in the README generator. Link text is the yaml name, or
the canonical owner/repo from GitHub. Stars use a thousands separator.

The top and rising blocks prefix every item with "1. " instead of "- ".
That rendered line is one character longer. This check follows the category
line, which is what the description log measures.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter
from typing import Any

LIMIT = 95
OVERHEAD = 7
URL_RE = re.compile(r"^https://github\.com/([\w.-]+)/([\w.-]+)/?$", re.IGNORECASE)
HIEROGLYPHS_RE = re.compile(
    "["
    "\u1100-\u11ff"
    "\u3040-\u30ff"
    "\u3400-\u4dbf"
    "\u4e00-\u9fff"
    "\uac00-\ud7af"
    "\u0600-\u06ff"
    "\u0590-\u05ff"
    "\u0e00-\u0e7f"
    "\u0900-\u097f"
    "]"
)


def format_stars(stars: int) -> str:
    if stars < 0:
        stars = 0
    text = str(stars)
    if len(text) <= 3:
        return text
    parts: list[str] = []
    while text:
        parts.append(text[-3:])
        text = text[:-3]
    return ",".join(reversed(parts))


def nbytes(text: str) -> int:
    return len(text.encode("utf-8"))


def visible_length(link_text: str, description: str, stars_text: str) -> int:
    return OVERHEAD + nbytes(link_text) + nbytes(description) + nbytes(stars_text)


def max_description(link_text: str, stars_text: str) -> int:
    return LIMIT - OVERHEAD - nbytes(link_text) - nbytes(stars_text)


def self_test() -> None:
    assert format_stars(0) == "0"
    assert format_stars(999) == "999"
    assert format_stars(1000) == "1,000"
    assert format_stars(31622) == "31,622"
    assert format_stars(1234567) == "1,234,567"

    link = "GeminiGeorge22/google-ads-transparency-mcp"
    description = (
        "Competitor Google ads from the Google Ads Transparency Center: "
        "new, running and stopped, with first and last shown dates"
    )
    assert nbytes(link) == 42
    assert nbytes(description) == 120
    assert visible_length(link, description, "0") == 170
    assert max_description(link, "0") == 45

    etsy = "GeminiGeorge22/etsy-sales-mcp"
    etsy_description = (
        "Etsy search results by keyword, marketplace and category plus "
        "daily sales counts and growth for any Etsy shop"
    )
    assert visible_length(etsy, etsy_description, "3") == 146
    assert max_description(etsy, "3") == 58


def iter_repos(node: dict[str, Any]) -> list[dict[str, Any]]:
    found: list[dict[str, Any]] = []

    def walk(category: dict[str, Any]) -> None:
        repos = category.get("repos") or []
        if isinstance(repos, list):
            found.extend(repo for repo in repos if isinstance(repo, dict))
        for sub in category.get("subcategories") or []:
            if isinstance(sub, dict):
                walk(sub)

    for category in node.get("categories") or []:
        if isinstance(category, dict):
            walk(category)
    return found


def repo_key(url: str) -> str:
    return url.rstrip("/").lower()


def load_yaml(path: str) -> dict[str, Any]:
    import yaml

    with open(path, encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    if not isinstance(data, dict):
        raise SystemExit(f"{path}: expected a YAML mapping")
    return data


def entry_signature(repo: dict[str, Any]) -> tuple[str, str, str] | None:
    description = repo.get("description") or ""
    if not isinstance(description, str) or description == "":
        return None
    name = repo.get("name") or ""
    if not isinstance(name, str):
        name = str(name)
    return repo_key(str(repo.get("url") or "")), description, name


def changed_repos(head: dict[str, Any], base: dict[str, Any]) -> list[dict[str, Any]]:
    """Return descriptions added or edited since base.

    The same URL can appear twice with different descriptions. Matching by URL
    alone would treat the untouched copy as a change.
    """
    base_counts: Counter[tuple[str, str, str]] = Counter()
    for repo in iter_repos(base):
        signature = entry_signature(repo)
        if signature is not None:
            base_counts[signature] += 1

    head_counts: Counter[tuple[str, str, str]] = Counter()
    sample: dict[tuple[str, str, str], dict[str, Any]] = {}
    for repo in iter_repos(head):
        signature = entry_signature(repo)
        if signature is None:
            continue
        head_counts[signature] += 1
        sample[signature] = repo

    return [
        sample[signature]
        for signature, count in head_counts.items()
        if count > base_counts.get(signature, 0)
    ]


def parse_url(url: str) -> tuple[str, str] | None:
    match = URL_RE.match(url.strip())
    if match is None:
        return None
    return match.group(1), match.group(2)


def rate_limited(status: int, raw: str) -> bool:
    text = raw.lower()
    return status in (403, 429) and ("rate limit" in text or "secondary rate" in text)


def http_json(url: str, token: str) -> tuple[int, dict[str, Any] | None, str]:
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "awesome-list-description-length",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            raw = response.read().decode("utf-8")
            status = response.status
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        status = exc.code
    except urllib.error.URLError as exc:
        raise SystemExit(f"GitHub API request failed: {exc.reason}") from exc
    if status != 200:
        return status, None, raw
    try:
        body = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise SystemExit(f"GitHub API returned invalid JSON for {url}") from exc
    if not isinstance(body, dict):
        raise SystemExit(f"GitHub API returned an unexpected response for {url}")
    return status, body, raw


def fetch_metadata(repos: list[tuple[str, str]], token: str) -> dict[tuple[str, str], tuple[str, int] | None]:
    """Read the canonical name and star count from public repository metadata.

    The workflow token is limited to this repository. A public repository
    outside it is read without that token when the token is refused.
    """
    found: dict[tuple[str, str], tuple[str, int] | None] = {}
    told_fallback = False
    for pair in dict.fromkeys(repos):
        owner, name = pair
        url = "https://api.github.com/repos/{}/{}".format(
            urllib.parse.quote(owner),
            urllib.parse.quote(name),
        )
        status, body, raw = http_json(url, token)
        if token and status in (401, 403) and not rate_limited(status, raw):
            if not told_fallback:
                print("Workflow token cannot read that public repository. Retrying without it.")
                told_fallback = True
            status, body, raw = http_json(url, "")
        if rate_limited(status, raw):
            raise SystemExit("GitHub API rate limit exceeded while reading star counts")
        if status == 404:
            found[pair] = None
            continue
        if status != 200 or body is None:
            detail = " ".join(raw.split())[:300]
            raise SystemExit(f"GitHub API HTTP {status} for {owner}/{name}: {detail}")
        full_name = body.get("full_name")
        stars = body.get("stargazers_count")
        if not isinstance(full_name, str) or full_name == "":
            raise SystemExit(f"GitHub API response for {owner}/{name} has no full_name")
        if isinstance(stars, bool) or not isinstance(stars, int):
            raise SystemExit(f"GitHub API response for {owner}/{name} has no stargazers_count")
        found[pair] = (full_name, stars)
    return found


def link_text(repo: dict[str, Any], canonical: str) -> str:
    custom = repo.get("name") or ""
    if isinstance(custom, str) and custom != "":
        return custom
    return canonical


def report(repo_url: str, lines: list[str], failed: bool) -> None:
    print(repo_url)
    for line in lines:
        print(f"  {line}")
    if failed:
        message = "; ".join(lines)
        print(f"::error::{repo_url}: {message}")


def check(path: str, base_path: str, token: str) -> int:
    head = load_yaml(path)
    base = load_yaml(base_path)
    selected = changed_repos(head, base)
    print("Visible README line limit: 95")
    print("visible = 7 + len(link text) + len(description) + len(formatted stars)")
    print("max description = 88 - len(link text) - len(formatted stars)")
    print("Lengths are UTF-8 bytes. Stars use a thousands separator.")
    print(f"Changed descriptions: {len(selected)}")
    if not selected:
        return 0

    pairs: list[tuple[str, str]] = []
    for repo in selected:
        parsed = parse_url(str(repo.get("url") or ""))
        if parsed is None:
            continue
        pairs.append(parsed)
    metadata = fetch_metadata(pairs, token) if pairs else {}

    failures = 0
    for repo in selected:
        url = str(repo.get("url") or "")
        parsed = parse_url(url)
        description = str(repo.get("description") or "")
        if parsed is None:
            failures += 1
            report(url, ["URL is not a GitHub repository"], True)
            continue
        meta = metadata.get(parsed)
        if meta is None:
            failures += 1
            report(url, ["GitHub repository was not found, star count is unknown"], True)
            continue
        canonical, stars = meta
        text = link_text(repo, canonical)
        stars_text = format_stars(stars)
        limit = max_description(text, stars_text)
        actual = nbytes(description)
        lines = [
            f"link text: {text} ({nbytes(text)})",
            f"stars: {stars} -> {stars_text!r} ({nbytes(stars_text)})",
            f"max description: {limit}",
            f"description: {actual}",
        ]
        failed = False
        if HIEROGLYPHS_RE.search(description):
            failed = True
            lines.append(
                "rejected: Han, Hiragana, Katakana, Hangul, Arabic, Hebrew, Thai, or Devanagari"
            )
        if actual > limit:
            failed = True
            lines.append(f"over by: {actual - limit}")
        if not failed:
            lines.append("fits")
        else:
            failures += 1
        report(url, lines, failed)

    print(f"Checked {len(selected)}, failed {failures}.")
    return 1 if failures else 0


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("head", nargs="?", help="repositories.yaml to check")
    parser.add_argument("--base", help="previous repositories.yaml")
    parser.add_argument("--self-test", action="store_true", help="check the length formula and exit")
    args = parser.parse_args()

    self_test()
    if args.self_test:
        print("Formula self-test passed.")
        if args.head is None:
            return

    if args.head is None or args.base is None:
        raise SystemExit("usage: check_description_length.py HEAD --base BASE")

    token = os.environ.get("GITHUB_TOKEN", "")
    sys.exit(check(args.head, args.base, token))


if __name__ == "__main__":
    main()
