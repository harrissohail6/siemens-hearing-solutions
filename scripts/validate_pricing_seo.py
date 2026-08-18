"""Validate the pricing answer cluster against the published catalog contract."""

from __future__ import annotations

import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

from bs4 import BeautifulSoup


ROOT = Path(__file__).resolve().parents[1]
SITE = "https://www.siemenshearingsolutions.com"

ARTICLE_PATHS = [
    "blog/signia-motion-bte-price-pakistan.html",
    "blog/signia-pure-312-x-price-pakistan.html",
    "blog/signia-insio-cic-price-pakistan.html",
    "blog/signia-silk-x-price-pakistan.html",
    "blog/signia-rechargeable-price-pakistan.html",
    "blog/hearing-aid-price-pakistan-2026.html",
    "blog/hearing-aid-price-islamabad.html",
    "blog/hearing-aid-channels-explained.html",
    "blog/german-vs-china-hearing-aid.html",
]

LEGACY_PRICE_PATHS = [
    "blog/affordable-hearing-aids-pakistan.html",
    "blog/cheapest-hearing-aid-pakistan.html",
    "blog/expensive-vs-cheap-hearing-aid.html",
    "blog/hearing-aid-price-comparison-pakistan.html",
    "blog/hearing-aid-price-installment.html",
    "blog/hearing-aid-price-rawalpindi.html",
    "blog/how-much-hearing-aid-cost-pakistan.html",
    "blog/why-hearing-aids-expensive.html",
    "blog/signia-intuis-3-review.html",
    "blog/signia-prompt-review.html",
]

BTE = {
    "Signia Prompt": ("Rs.35,000", "Rs.118,000", "Rs.150,000", "unit"),
    "Signia Intuis 3": ("Rs.65,000", "Rs.310,000", "Rs.330,000", "unit"),
    "Signia Intuis 4.2": ("Rs.70,000", "Rs.350,000", "Rs.370,000", "unit"),
    "Signia Motion 1Nx": ("Rs.85,000", "Rs.335,000", "Rs.495,000", "unit"),
    "Signia Motion 3Nx": ("Rs.145,000", "Rs.385,000", "Rs.635,000", "unit"),
    "Signia Motion 5Nx": ("Rs.135,000", "Rs.485,000", "Rs.710,000", "unit"),
    "Signia Motion 7Nx": ("Rs.285,000", "Rs.595,000", "Rs.840,000", "unit"),
}
PURE = {
    "Signia Pure 312 1X": ("Rs.85,000", "Rs.385,000", "Rs.545,000", "unit"),
    "Signia Pure 312 3X": ("Rs.145,000", "Rs.435,000", "Rs.685,000", "unit"),
    "Signia Pure 312 5X": ("Rs.135,000", "Rs.535,000", "Rs.760,000", "unit"),
    "Signia Pure 312 7X": ("Rs.285,000", "Rs.645,000", "Rs.890,000", "unit"),
}
INSIO = {
    "Signia Prompt CIC": ("Rs.35,000", "Rs.118,000", "Rs.150,000", "unit"),
    "Signia Intuis 3 CIC": ("Rs.65,000", "Rs.310,000", "Rs.330,000", "unit"),
    "Signia Insio 1Nx": ("Rs.85,000", "Rs.385,000", "Rs.545,000", "unit"),
    "Signia Insio 3Nx": ("Rs.145,000", "Rs.435,000", "Rs.685,000", "unit"),
    "Signia Insio 5Nx": ("Rs.135,000", "Rs.535,000", "Rs.760,000", "unit"),
    "Signia Insio 7Nx": ("Rs.285,000", "Rs.645,000", "Rs.890,000", "unit"),
}
SILK = {
    "Signia Prompt Click CIC": ("Rs.35,000", "Rs.118,000", "Rs.150,000", "unit"),
    "Signia Intuis 3 Click CIC": ("Rs.65,000", "Rs.310,000", "Rs.330,000", "unit"),
    "Signia Silk 1X": ("Rs.85,000", "Rs.385,000", "Rs.545,000", "unit"),
    "Signia Silk 3X": ("Rs.145,000", "Rs.435,000", "Rs.685,000", "unit"),
    "Signia Silk 5X": ("Rs.135,000", "Rs.535,000", "Rs.760,000", "unit"),
    "Signia Silk 7X": ("Rs.285,000", "Rs.645,000", "Rs.890,000", "unit"),
}
RECHARGEABLE = {
    "Signia Orion 50 C&G": ("Rs.120,000", "Rs.350,000", "Rs.510,000", "pair"),
    "Signia Orion 75 C&G": ("Rs.150,000", "Rs.450,000", "Rs.610,000", "pair"),
    "Signia Orion 100 C&G": ("Rs.180,000", "Rs.650,000", "Rs.810,000", "pair"),
    "Signia Motion C&G Series": (
        "Rs.120,000-280,000",
        "Rs.590,000-790,000",
        "Rs.810,000-1,510,000",
        "pair",
    ),
    "Signia Pure C&G Series": (
        "Rs.120,000-280,000",
        "Rs.590,000-790,000",
        "Rs.845,000-1,955,000",
        "pair",
    ),
}
ALL_PRICES = BTE | PURE | INSIO | SILK | RECHARGEABLE


def norm(value: str) -> str:
    return " ".join(value.split())


def fail(errors: list[str], message: str) -> None:
    errors.append(message)


def table_rows(path: Path) -> dict[str, tuple[str, str, str, str]]:
    soup = BeautifulSoup(path.read_text(encoding="utf-8"), "html.parser")
    rows: dict[str, tuple[str, str, str, str]] = {}
    for row in soup.select("table.price-table tbody tr"):
        cells = row.find_all("td")
        if len(cells) != 5:
            continue
        model = norm(cells[0].get_text(" ", strip=True))
        rows[model] = (
            norm(cells[2].get_text(" ", strip=True)),
            norm(cells[3].get_text(" ", strip=True)),
            norm(cells[4].get_text(" ", strip=True)),
            "pair" if "/pair" in cells[2].get_text(" ", strip=True) else "unit",
        )
    return rows


def validate() -> list[str]:
    errors: list[str] = []
    products = sorted((ROOT / "products").glob("*.html"))
    targets = [ROOT / p for p in ARTICLE_PATHS + LEGACY_PRICE_PATHS] + products + [ROOT / "blog.html", ROOT / "products.html"]

    for path in targets:
        rel = path.relative_to(ROOT).as_posix()
        text = path.read_text(encoding="utf-8")
        soup = BeautifulSoup(text, "html.parser")
        if not soup.title or not soup.title.get_text(strip=True):
            fail(errors, f"{rel}: missing title")
        description = soup.find("meta", attrs={"name": "description"})
        if not description or not description.get("content"):
            fail(errors, f"{rel}: missing meta description")
        if not soup.find("link", rel="canonical"):
            fail(errors, f"{rel}: missing canonical")
        for script in soup.find_all("script", attrs={"type": "application/ld+json"}):
            try:
                json.loads(script.string or script.get_text())
            except Exception as exc:  # pragma: no cover - diagnostic path
                fail(errors, f"{rel}: invalid JSON-LD: {exc}")
        for tag in ("div", "main", "section", "table"):
            opens = len(re.findall(fr"<{tag}(?:\s|>)", text, re.I))
            closes = len(re.findall(fr"</{tag}>", text, re.I))
            if opens != closes:
                fail(errors, f"{rel}: {tag} balance {opens} != {closes}")
        for anchor in soup.find_all("a", href=True):
            href = anchor["href"].split("#", 1)[0].split("?", 1)[0]
            if not href or re.match(r"^(?:https?:|mailto:|tel:|javascript:)", href):
                continue
            if not (path.parent / href).resolve().exists():
                fail(errors, f"{rel}: broken href {anchor['href']}")

    for rel in ARTICLE_PATHS:
        path = ROOT / rel
        soup = BeautifulSoup(path.read_text(encoding="utf-8"), "html.parser")
        schemas = [
            json.loads(script.string or script.get_text())
            for script in soup.find_all("script", attrs={"type": "application/ld+json"})
        ]
        schema_types = {schema.get("@type") for schema in schemas}
        if schema_types != {"Article", "BreadcrumbList", "FAQPage"}:
            fail(errors, f"{rel}: unexpected schema types {schema_types}")
        faq = next(schema for schema in schemas if schema.get("@type") == "FAQPage")
        schema_questions = [entity["name"] for entity in faq["mainEntity"]]
        visible_questions = [
            heading.get_text(" ", strip=True)
            for heading in soup.select("main h3")
            if heading.find_parent("div", style=lambda value: value and "border-left:4px" in value)
        ]
        if schema_questions != visible_questions:
            fail(errors, f"{rel}: visible FAQ does not match FAQPage schema")
        title = soup.title.get_text(strip=True)
        description = soup.find("meta", attrs={"name": "description"})["content"]
        if len(title) > 65:
            fail(errors, f"{rel}: title is {len(title)} characters")
        if not 100 <= len(description) <= 165:
            fail(errors, f"{rel}: description is {len(description)} characters")

    table_contracts = {
        "blog/signia-motion-bte-price-pakistan.html": BTE,
        "blog/signia-pure-312-x-price-pakistan.html": PURE,
        "blog/signia-insio-cic-price-pakistan.html": INSIO,
        "blog/signia-silk-x-price-pakistan.html": SILK,
        "blog/signia-rechargeable-price-pakistan.html": RECHARGEABLE,
        "blog/hearing-aid-price-pakistan-2026.html": ALL_PRICES,
    }
    for rel, contract in table_contracts.items():
        actual = table_rows(ROOT / rel)
        if set(actual) != set(contract):
            fail(errors, f"{rel}: table models differ: missing={set(contract)-set(actual)}, extra={set(actual)-set(contract)}")
            continue
        for model, expected in contract.items():
            actual_prices = actual[model]
            for index, price in enumerate(expected[:3]):
                if price not in actual_prices[index]:
                    fail(errors, f"{rel}: {model} price mismatch {actual_prices} != {expected}")
            if actual_prices[3] != expected[3]:
                fail(errors, f"{rel}: {model} basis mismatch {actual_prices[3]} != {expected[3]}")

    for path in products:
        text = path.read_text(encoding="utf-8")
        soup = BeautifulSoup(text, "html.parser")
        match = re.search(r"The current catalog prices for [^\"<]+? are ([^\"<]+?) Prices were synchronized", text)
        if not match:
            fail(errors, f"{path.name}: direct three-price FAQ answer missing")
            continue
        answer = match.group(1)
        visible_prices = [norm(element.get_text(" ", strip=True)) for element in soup.select(".price-card .price-amount")]
        if len(visible_prices) != 3:
            fail(errors, f"{path.name}: expected three visible price cards, found {len(visible_prices)}")
        for price in visible_prices:
            if price not in answer:
                fail(errors, f"{path.name}: FAQ answer omits visible price {price}")
        if "Expected Lifespan" in text or "Authentic Signia" in text:
            fail(errors, f"{path.name}: unsupported lifespan/authenticity card claim remains")
        for unsupported in (
            '"@type": "AggregateOffer"',
            "https://schema.org/InStock",
            '<span class="spec-label">Manufacturer</span>',
            "authorized Siemens Signia dealer",
            "full warranty support",
            "Get authentic Signia",
        ):
            if unsupported in text:
                fail(errors, f"{path.name}: unsupported product claim/schema remains: {unsupported}")

    products_index = (ROOT / "products.html").read_text(encoding="utf-8")
    if '"@type": "AggregateOffer"' in products_index or '"@type": "Product"' in products_index:
        fail(errors, "products.html: category-level Product/AggregateOffer schema remains")

    stale_checks = {
        "blog/signia-prompt-review.html": [r"4[- ]channel", r"genuine Signia quality"],
        "blog/signia-intuis-3-review.html": [r"Intuis 3[^\r\n<]{0,80}(?:is|with|offers?)?\s*8[- ]channels?"],
        "blog/hearing-aid-price-rawalpindi.html": [r"Signia Fun SP", r"Rs\. ?25,000-30,000"],
    }
    for rel, patterns in stale_checks.items():
        text = (ROOT / rel).read_text(encoding="utf-8")
        for pattern in patterns:
            if re.search(pattern, text, re.I):
                fail(errors, f"{rel}: stale claim matches {pattern}")

    for path in ROOT.rglob("*.html"):
        text = path.read_text(encoding="utf-8", errors="ignore")
        if re.search(r"Pure 312 (?:1|3|5|7)Nx|Pure 312 (?:1|3|5|7)X/Nx", text, re.I):
            fail(errors, f"{path.relative_to(ROOT).as_posix()}: forbidden Pure X/Nx mixed name")
        for marker in ("â", "Ã", "ðŸ", "&#226;"):
            if marker in text:
                fail(errors, f"{path.relative_to(ROOT).as_posix()}: mojibake marker remains: {marker}")

    sitemap = ET.parse(ROOT / "sitemap.xml")
    namespace = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    locations = [element.text for element in sitemap.findall(".//s:loc", namespace)]
    html_files = sorted(ROOT.rglob("*.html"))
    expected_locations = set()
    for path in html_files:
        soup = BeautifulSoup(path.read_text(encoding="utf-8"), "html.parser")
        robots_meta = soup.find("meta", attrs={"name": "robots"})
        if robots_meta and "noindex" in robots_meta.get("content", "").lower():
            continue
        relative = path.relative_to(ROOT).as_posix()
        expected_locations.add(f"{SITE}/" + ("" if relative == "index.html" else relative))
    if len(locations) != len(set(locations)):
        fail(errors, "sitemap.xml: duplicate URLs")
    if set(locations) != expected_locations:
        fail(errors, f"sitemap.xml: parity failure; missing={expected_locations-set(locations)}, extra={set(locations)-expected_locations}")

    robots = (ROOT / "robots.txt").read_text(encoding="utf-8")
    if "User-agent: OAI-SearchBot\nAllow: /" not in robots.replace("\r\n", "\n"):
        fail(errors, "robots.txt: OAI-SearchBot is not explicitly allowed")

    return errors


if __name__ == "__main__":
    problems = validate()
    html_count = len(list(ROOT.rglob("*.html")))
    sitemap_count = len(ET.parse(ROOT / "sitemap.xml").findall(".//{http://www.sitemaps.org/schemas/sitemap/0.9}loc"))
    print(f"Validated {len(ARTICLE_PATHS)} pricing articles, 26 product pages, {html_count} HTML files, and {sitemap_count} sitemap URLs.")
    if problems:
        print("\n".join(f"ERROR: {problem}" for problem in problems))
        sys.exit(1)
    print("Pricing SEO validation passed.")
