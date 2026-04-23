"""Accessibility & ARIA signal.

Checks WCAG 2.1 signals that correlate with Page Experience:
- Images without alt text
- Form inputs without labels
- Missing lang attribute on <html>
- Skip-link presence
- ARIA roles on interactive elements
- Focusable elements without accessible names
"""
from __future__ import annotations

from bs4 import BeautifulSoup

from ..report import Effort, Evidence, Finding, Severity, SignalResult
from ..scoring import score_from_findings


def check(ctx) -> SignalResult:
    findings: list[Finding] = []
    data: dict = {"per_page": []}

    total_images = 0
    images_missing_alt = 0
    total_inputs = 0
    inputs_missing_label = 0
    skip_link_found = False
    lang_found = False
    interactive_missing_name = 0
    total_interactive = 0

    for p in ctx.pages:
        if not p.html or p.status >= 400:
            continue
        soup = BeautifulSoup(p.html, "lxml")

        # lang attribute
        html_tag = soup.find("html")
        page_lang = html_tag.get("lang") if html_tag else None
        if page_lang:
            lang_found = True
        else:
            findings.append(Finding(
                id="accessibility.lang.missing",
                severity=Severity.P2,
                title=f"Missing lang attribute on <html> at {p.final_url}",
                evidence=Evidence(url=p.final_url),
                recommendation="Add lang='en' (or appropriate) to <html> for screen readers and language targeting.",
                effort=Effort.S,
                google_algo_ref="Accessibility / Page Experience",
            ))

        # Skip link
        skip = soup.find("a", href="#main") or soup.find("a", href="#content") or soup.find("a", class_=lambda c: c and "skip" in c.lower())
        if skip:
            skip_link_found = True

        # Images without alt
        images = soup.find_all("img")
        page_missing_alt = 0
        for img in images:
            total_images += 1
            alt = img.get("alt")
            if alt is None or (isinstance(alt, str) and not alt.strip() and not img.get("role") == "presentation"):
                images_missing_alt += 1
                page_missing_alt += 1

        if page_missing_alt > 0:
            findings.append(Finding(
                id="accessibility.img.missing_alt",
                severity=Severity.P2,
                title=f"{page_missing_alt} image(s) without alt text on {p.final_url}",
                evidence=Evidence(url=p.final_url, value=page_missing_alt),
                recommendation="Add descriptive alt text to all informative images. Use alt='' for decorative images.",
                effort=Effort.S,
                google_algo_ref="Accessibility / Image SEO",
            ))

        # Form inputs without labels
        inputs = soup.find_all(["input", "textarea", "select"])
        page_missing_label = 0
        for inp in inputs:
            total_inputs += 1
            inp_id = inp.get("id")
            aria_label = inp.get("aria-label")
            aria_labelledby = inp.get("aria-labelledby")
            placeholder = inp.get("placeholder")
            has_label = False
            if inp_id:
                has_label = bool(soup.find("label", attrs={"for": inp_id}))
            if not has_label and not aria_label and not aria_labelledby and not placeholder:
                inputs_missing_label += 1
                page_missing_label += 1

        if page_missing_label > 0:
            findings.append(Finding(
                id="accessibility.input.missing_label",
                severity=Severity.P3,
                title=f"{page_missing_label} form input(s) without label on {p.final_url}",
                evidence=Evidence(url=p.final_url, value=page_missing_label),
                recommendation="Add <label for='id'> or aria-label to every form input.",
                effort=Effort.S,
                google_algo_ref="Accessibility / WCAG 2.1",
            ))

        # Interactive elements without accessible name
        interactive = soup.find_all(["button", "a", "*[role='button']"])
        page_missing_name = 0
        for el in interactive:
            total_interactive += 1
            text = el.get_text(strip=True)
            aria = el.get("aria-label") or el.get("aria-labelledby")
            title = el.get("title")
            if not text and not aria and not title:
                interactive_missing_name += 1
                page_missing_name += 1

        if page_missing_name > 0:
            findings.append(Finding(
                id="accessibility.interactive.missing_name",
                severity=Severity.P2,
                title=f"{page_missing_name} interactive element(s) without accessible name on {p.final_url}",
                evidence=Evidence(url=p.final_url, value=page_missing_name),
                recommendation="Add visible text, aria-label, or title to buttons and links.",
                effort=Effort.S,
                google_algo_ref="Accessibility / WCAG 2.1",
            ))

        data["per_page"].append({
            "url": p.final_url,
            "lang": page_lang,
            "images": len(images),
            "images_missing_alt": page_missing_alt,
            "inputs": len(inputs),
            "inputs_missing_label": page_missing_label,
            "interactive_missing_name": page_missing_name,
        })

    if not skip_link_found:
        findings.append(Finding(
            id="accessibility.skip_link.missing",
            severity=Severity.P3,
            title="No skip-to-content link found on any page",
            evidence=Evidence(url=ctx.base_url),
            recommendation="Add a 'Skip to main content' link as the first focusable element for keyboard navigation.",
            effort=Effort.S,
            google_algo_ref="Accessibility / WCAG 2.4.1",
        ))

    data.update({
        "total_images": total_images,
        "images_missing_alt": images_missing_alt,
        "total_inputs": total_inputs,
        "inputs_missing_label": inputs_missing_label,
        "skip_link_found": skip_link_found,
        "lang_found": lang_found,
        "interactive_missing_name": interactive_missing_name,
        "total_interactive": total_interactive,
    })

    score = score_from_findings(100, findings)
    return SignalResult(name="accessibility", score=score, findings=findings, data=data)
