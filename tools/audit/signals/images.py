"""Image optimization signal.

Checks image SEO health:
- Alt text presence and quality
- Descriptive file names
- Image dimensions (width/height attributes)
- Lazy loading
- File format (WebP/AVIF preference)
- Responsive images (srcset)
- Excessive image count (page bloat)
"""
from __future__ import annotations

import re
from urllib.parse import urlparse

from bs4 import BeautifulSoup

from ..report import Effort, Evidence, Finding, Severity, SignalResult
from ..scoring import score_from_findings


def check(ctx) -> SignalResult:
    findings: list[Finding] = []
    data: dict = {}

    pages_checked = 0
    total_images = 0
    missing_alt = 0
    empty_alt = 0
    generic_alt = 0
    missing_width_height = 0
    not_lazy_loaded = 0
    non_modern_format = 0
    no_srcset = 0
    bad_filename = 0
    oversized_pages = 0

    GENERIC_ALT = {"image", "img", "photo", "picture", "pic", "screenshot", "logo", "icon", "banner"}

    for p in ctx.pages:
        if not p.html or p.status >= 400:
            continue
        soup = BeautifulSoup(p.html, "lxml")
        imgs = soup.find_all("img")
        if not imgs:
            continue

        pages_checked += 1
        page_img_count = len(imgs)
        total_images += page_img_count
        page_missing_alt = 0
        page_empty_alt = 0
        page_generic_alt = 0
        page_missing_dims = 0
        page_not_lazy = 0
        page_non_modern = 0
        page_no_srcset = 0
        page_bad_fname = 0

        for img in imgs:
            src = (img.get("src") or img.get("data-src") or "").strip()
            alt = (img.get("alt") or "").strip()
            width = img.get("width")
            height = img.get("height")
            loading = img.get("loading", "")
            srcset = img.get("srcset", "")

            # Alt text
            if alt == "":
                missing_alt += 1
                page_missing_alt += 1
            elif alt.lower() in GENERIC_ALT:
                generic_alt += 1
                page_generic_alt += 1
            elif len(alt) < 5:
                empty_alt += 1
                page_empty_alt += 1

            # Dimensions
            if not width or not height:
                missing_width_height += 1
                page_missing_dims += 1

            # Lazy loading
            if loading != "lazy":
                not_lazy_loaded += 1
                page_not_lazy += 1

            # Modern format
            fname = src.split("?")[0].split("/")[-1].lower()
            if fname and not fname.endswith((".webp", ".avif")):
                non_modern_format += 1
                page_non_modern += 1

            # Descriptive filename
            if fname:
                name_part = fname.rsplit(".", 1)[0] if "." in fname else fname
                if re.match(r"^img[_-]?\d+$", name_part, re.I) or re.match(r"^image[_-]?\d+$", name_part, re.I) or re.match(r"^\d+$", name_part):
                    bad_filename += 1
                    page_bad_fname += 1

            # Responsive
            if not srcset:
                no_srcset += 1
                page_no_srcset += 1

        # Page-level findings (cap at 1 per page per issue)
        if page_missing_alt > 0:
            findings.append(Finding(
                id="images.alt.missing",
                severity=Severity.P2,
                title=f"{page_missing_alt} image(s) missing alt text on {p.final_url}",
                evidence=Evidence(url=p.final_url, value=page_missing_alt),
                recommendation="Add descriptive alt text to every image. Blank alt is only acceptable for decorative images (use alt='').",
                effort=Effort.S,
                google_algo_ref="Image search / Accessibility",
            ))
        if page_generic_alt > 0:
            findings.append(Finding(
                id="images.alt.generic",
                severity=Severity.P3,
                title=f"{page_generic_alt} image(s) with generic alt text on {p.final_url}",
                evidence=Evidence(url=p.final_url, value=page_generic_alt),
                recommendation="Replace generic alt ('image', 'photo') with descriptive text that describes the image content.",
                effort=Effort.S,
                google_algo_ref="Image search / Accessibility",
            ))
        if page_missing_dims > 0:
            findings.append(Finding(
                id="images.dimensions.missing",
                severity=Severity.P2,
                title=f"{page_missing_dims} image(s) missing width/height on {p.final_url}",
                evidence=Evidence(url=p.final_url, value=page_missing_dims),
                recommendation="Add width and height attributes to all images to prevent CLS (Cumulative Layout Shift).",
                effort=Effort.S,
                google_algo_ref="Core Web Vitals / CLS",
            ))
        if page_not_lazy > 5:
            findings.append(Finding(
                id="images.lazy.missing",
                severity=Severity.P2,
                title=f"{page_not_lazy} image(s) not lazy-loaded on {p.final_url}",
                evidence=Evidence(url=p.final_url, value=page_not_lazy),
                recommendation="Add loading='lazy' to below-the-fold images. Reduces LCP and improves page speed.",
                effort=Effort.S,
                google_algo_ref="Core Web Vitals / LCP",
            ))
        if page_non_modern > 5:
            findings.append(Finding(
                id="images.format.legacy",
                severity=Severity.P3,
                title=f"{page_non_modern} image(s) using legacy format (not WebP/AVIF) on {p.final_url}",
                evidence=Evidence(url=p.final_url, value=page_non_modern),
                recommendation="Convert images to WebP or AVIF. Modern formats are 25-50% smaller than JPEG/PNG.",
                effort=Effort.M,
                google_algo_ref="Page speed / Image optimization",
            ))
        if page_bad_fname > 0:
            findings.append(Finding(
                id="images.filename.nondescriptive",
                severity=Severity.P3,
                title=f"{page_bad_fname} image(s) with non-descriptive filename on {p.final_url}",
                evidence=Evidence(url=p.final_url, value=page_bad_fname),
                recommendation="Use keyword-relevant filenames (e.g., 'on-page-seo-checklist.webp' not 'IMG_1234.jpg').",
                effort=Effort.S,
                google_algo_ref="Image search / SEO",
            ))
        if page_img_count > 30:
            oversized_pages += 1
            findings.append(Finding(
                id="images.count.excessive",
                severity=Severity.P3,
                title=f"{page_img_count} images on {p.final_url} — excessive count",
                evidence=Evidence(url=p.final_url, value=page_img_count),
                recommendation="Pages with >30 images hurt LCP and mobile UX. Consider pagination or lazy-loading galleries.",
                effort=Effort.M,
                google_algo_ref="Core Web Vitals / Mobile UX",
            ))

    data.update({
        "pages_checked": pages_checked,
        "total_images": total_images,
        "missing_alt": missing_alt,
        "empty_alt": empty_alt,
        "generic_alt": generic_alt,
        "missing_width_height": missing_width_height,
        "not_lazy_loaded": not_lazy_loaded,
        "non_modern_format": non_modern_format,
        "no_srcset": no_srcset,
        "bad_filename": bad_filename,
        "oversized_pages": oversized_pages,
    })

    if pages_checked > 0 and total_images == 0:
        findings.append(Finding(
            id="images.none",
            severity=Severity.P3,
            title="No images found across checked pages",
            evidence=Evidence(url=ctx.base_url),
            recommendation="Add relevant images, diagrams, or infographics. Visual content improves engagement and image search visibility.",
            effort=Effort.M,
            google_algo_ref="Image search / Engagement",
        ))

    score = score_from_findings(100, findings)
    return SignalResult(name="images", score=score, findings=findings, data=data)
