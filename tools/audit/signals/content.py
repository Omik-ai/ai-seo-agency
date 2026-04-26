"""Content quality signal — word count, readability, thin/duplicate."""
from __future__ import annotations

import re
from collections import Counter

from bs4 import BeautifulSoup

from ..report import Effort, Evidence, Finding, Severity, SignalResult
from ..scoring import score_from_findings


def _extract_main_text(soup: BeautifulSoup) -> str:
    # Prefer <article> > <main>, else the largest text-dense div
    for tag in ("article", "main"):
        el = soup.find(tag)
        if el and len(el.get_text(strip=True)) > 200:
            return el.get_text(" ", strip=True)
    # Fallback: strip nav/header/footer
    for t in ("nav", "header", "footer", "aside", "script", "style"):
        for el in soup.find_all(t):
            el.decompose()
    return soup.get_text(" ", strip=True)


VOWELS = "aeiouy"


def _syllables(word: str) -> int:
    w = re.sub(r"[^a-z]", "", word.lower())
    if not w:
        return 0
    count = 0
    prev_vowel = False
    for ch in w:
        is_v = ch in VOWELS
        if is_v and not prev_vowel:
            count += 1
        prev_vowel = is_v
    if w.endswith("e") and count > 1:
        count -= 1
    return max(1, count)


def flesch_reading_ease(text: str) -> float | None:
    sentences = re.split(r"[.!?]+", text)
    sentences = [s for s in sentences if s.strip()]
    words = re.findall(r"[A-Za-z']+", text)
    if not sentences or not words:
        return None
    sylls = sum(_syllables(w) for w in words)
    # Flesch Reading Ease: 206.835 - 1.015*(words/sentences) - 84.6*(syllables/words)
    return round(206.835 - 1.015 * (len(words) / len(sentences)) - 84.6 * (sylls / len(words)), 1)


STOPWORDS = {
    "the", "a", "an", "is", "are", "was", "were", "be", "been", "being",
    "have", "has", "had", "do", "does", "did", "will", "would", "could",
    "should", "may", "might", "must", "shall", "can", "need", "dare",
    "ought", "used", "to", "of", "in", "for", "on", "with", "at", "by",
    "from", "as", "into", "through", "during", "before", "after", "above",
    "below", "between", "under", "again", "further", "then", "once", "here",
    "there", "when", "where", "why", "how", "all", "each", "few", "more",
    "most", "other", "some", "such", "no", "nor", "not", "only", "own",
    "same", "so", "than", "too", "very", "just", "and", "but", "if", "or",
    "because", "until", "while", "this", "that", "these", "those", "i",
    "me", "my", "myself", "we", "our", "you", "your", "he", "him", "his",
    "she", "her", "it", "its", "they", "them", "their", "what", "which",
    "who", "whom", "whose", "s", "t", "don", "didn", "doesn", "wasn",
    "weren", "won", "wouldn", "couldn", "shouldn", "isn", "aren", "hasn",
    "haven", "hadn", "does", "did", "will", "would", "could", "should",
}


def _keyword_density(text: str) -> dict[str, float]:
    words = re.findall(r"[A-Za-z']+", text.lower())
    filtered = [w for w in words if w not in STOPWORDS and len(w) > 2]
    if not filtered:
        return {}
    counts = Counter(filtered)
    total = len(filtered)
    return {word: round(count / total * 100, 2) for word, count in counts.most_common(10)}


def _extract_entities(text: str) -> dict[str, list[str]]:
    """Extract named entities. Uses spaCy if available, falls back to regex heuristics."""
    # Try spaCy first (cached at module level to avoid reloads)
    _nlp = getattr(_extract_entities, "_nlp", None)
    if _nlp is None:
        try:
            import spacy
            _nlp = spacy.load("en_core_web_sm")
            _extract_entities._nlp = _nlp
        except Exception:
            _extract_entities._nlp = False
    if _nlp:
        try:
            doc = _nlp(text[:50000])  # cap to avoid memory issues
            entities: dict[str, list[str]] = {}
            for ent in doc.ents:
                entities.setdefault(ent.label_, []).append(ent.text)
            for k in entities:
                entities[k] = list(dict.fromkeys(entities[k]))[:20]
            return entities
        except Exception:
            pass

    # Fallback regex NER (improved)
    entities: dict[str, list[str]] = {}
    # Organizations
    orgs = re.findall(
        r"([A-Z][A-Za-z0-9&\s]+(?:Inc\.?|LLC|Ltd\.?|Corp\.?|Company|Co\.?|Group|Studio|Agency|Labs|AI|Tech|Software|Platform|App))",
        text,
    )
    if orgs:
        entities["ORG"] = list(dict.fromkeys(orgs))[:10]
    # Persons: Capitalized Word Capitalized Word
    persons = re.findall(r"([A-Z][a-z]+\s[A-Z][a-z]+)", text)
    if persons:
        stop = {"The", "For", "And", "With", "From", "This", "That", "Each", "More", "Most", "Some", "Such", "Only", "Same", "Very", "Just", "But", "Not", "Nor", "Can", "Will", "Would", "Could", "Should", "May", "Might", "Must", "Shall", "Need", "Dare", "Ought", "Used", "Have", "Has", "Had", "Do", "Does", "Did", "Be", "Been", "Being", "Was", "Were", "Are", "Is", "Am"}
        filtered = [p for p in persons if p.split()[0] not in stop and p.split()[1] not in stop]
        entities["PERSON"] = list(dict.fromkeys(filtered))[:10]
    # Money / amounts
    money = re.findall(r"\$[\d,]+(?:\.\d{2})?(?:\s*(?:million|billion|thousand|M|B|K))?", text, re.I)
    if money:
        entities["MONEY"] = list(dict.fromkeys(money))[:10]
    # Dates (simple)
    dates = re.findall(r"\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2}(?:,\s+\d{4})?\b", text)
    if dates:
        entities["DATE"] = list(dict.fromkeys(dates))[:10]
    # Percentages
    percents = re.findall(r"\b\d{1,3}(?:\.\d+)?%", text)
    if percents:
        entities["PERCENT"] = list(dict.fromkeys(percents))[:10]
    return entities


def check(ctx) -> SignalResult:
    findings: list[Finding] = []
    data: dict = {"per_page": []}

    titles: list[tuple[str, str]] = []  # (url, title)
    descs: list[tuple[str, str]] = []

    for p in ctx.pages:
        if not p.html or p.status >= 400:
            continue
        soup = BeautifulSoup(p.html, "lxml")
        title_el = soup.find("title")
        title = title_el.get_text(strip=True) if title_el else ""
        desc_el = soup.find("meta", attrs={"name": "description"})
        desc = (desc_el.get("content", "") if desc_el else "").strip()
        text = _extract_main_text(soup)
        word_count = len(re.findall(r"[A-Za-z']+", text))
        flesch = flesch_reading_ease(text) if word_count > 50 else None

        titles.append((p.final_url, title))
        descs.append((p.final_url, desc))

        density = _keyword_density(text)
        entities = _extract_entities(text)

        page_data = {
            "url": p.final_url,
            "title": title,
            "title_len": len(title),
            "meta_desc": desc,
            "meta_desc_len": len(desc),
            "word_count": word_count,
            "flesch": flesch,
            "keyword_density": density,
            "entities": entities,
        }
        data["per_page"].append(page_data)

        # Keyword stuffing detection
        for word, pct in density.items():
            if pct > 5.0:
                findings.append(Finding(
                    id="content.keyword.stuffing",
                    severity=Severity.P1,
                    title=f"Possible keyword stuffing ('{word}' {pct}%) on {p.final_url}",
                    evidence=Evidence(url=p.final_url, value={word: pct}),
                    recommendation="Reduce keyword density to <3%. Use synonyms and natural language.",
                    effort=Effort.M,
                    google_algo_ref="SpamBrain / Keyword Stuffing",
                ))
                break  # one stuffing finding per page is enough

        # Title checks
        if not title:
            findings.append(Finding(
                id="content.title.missing",
                severity=Severity.P0,
                title=f"Missing <title> on {p.final_url}",
                evidence=Evidence(url=p.final_url),
                recommendation="Every page must have a unique <title> of 30–60 characters.",
                effort=Effort.S,
                google_algo_ref="Core on-page signal",
            ))
        else:
            if len(title) < 30:
                findings.append(Finding(
                    id="content.title.short",
                    severity=Severity.P2,
                    title=f"Title too short ({len(title)} chars) on {p.final_url}",
                    evidence=Evidence(url=p.final_url, value=title),
                    recommendation="Expand title to 30–60 chars. Include primary keyword + brand.",
                    effort=Effort.S,
                ))
            elif len(title) > 70:
                findings.append(Finding(
                    id="content.title.long",
                    severity=Severity.P2,
                    title=f"Title truncated risk ({len(title)} chars) on {p.final_url}",
                    evidence=Evidence(url=p.final_url, value=title),
                    recommendation="Trim title to ≤60 chars so it isn't truncated in SERPs.",
                    effort=Effort.S,
                ))

        # Meta description
        if not desc:
            findings.append(Finding(
                id="content.meta_desc.missing",
                severity=Severity.P2,
                title=f"Missing meta description on {p.final_url}",
                evidence=Evidence(url=p.final_url),
                recommendation="Add a 70–160 char meta description. Not a ranking factor, but boosts CTR.",
                effort=Effort.S,
            ))
        elif len(desc) < 70:
            findings.append(Finding(
                id="content.meta_desc.short",
                severity=Severity.P3,
                title=f"Meta description short ({len(desc)} chars) on {p.final_url}",
                evidence=Evidence(url=p.final_url, value=desc),
                recommendation="Expand to 70–160 chars for best SERP snippet coverage.",
                effort=Effort.S,
            ))
        elif len(desc) > 170:
            findings.append(Finding(
                id="content.meta_desc.long",
                severity=Severity.P3,
                title=f"Meta description long ({len(desc)} chars) on {p.final_url}",
                evidence=Evidence(url=p.final_url),
                recommendation="Trim to ≤160 chars to avoid SERP truncation.",
                effort=Effort.S,
            ))

        # Thin content — apply only to clearly content pages (path length > 1)
        if word_count < 300 and len(p.final_url.rstrip("/").split("/")) > 3:
            findings.append(Finding(
                id="content.thin",
                severity=Severity.P1,
                title=f"Thin content ({word_count} words) on {p.final_url}",
                evidence=Evidence(url=p.final_url, value=word_count),
                recommendation="Expand to 600+ words with unique value; Helpful Content system penalizes thin pages.",
                effort=Effort.L,
                google_algo_ref="Helpful Content",
            ))
        elif word_count < 600 and len(p.final_url.rstrip("/").split("/")) > 3:
            findings.append(Finding(
                id="content.borderline",
                severity=Severity.P3,
                title=f"Borderline content length ({word_count} words) on {p.final_url}",
                evidence=Evidence(url=p.final_url, value=word_count),
                recommendation="Consider expanding for topical depth. Not every page needs 600+ words, but content hubs do.",
                effort=Effort.M,
            ))

        # Readability
        if flesch is not None and flesch < 30:
            findings.append(Finding(
                id="content.readability.hard",
                severity=Severity.P3,
                title=f"Very hard to read (Flesch {flesch}) on {p.final_url}",
                evidence=Evidence(url=p.final_url, value=flesch),
                recommendation="Shorten sentences and use simpler words. Flesch 60–70 is the target for web content.",
                effort=Effort.M,
            ))

    # Duplicate titles / meta
    title_counts = Counter([t for _, t in titles if t])
    for (url, t) in titles:
        if t and title_counts[t] > 1:
            findings.append(Finding(
                id="content.title.duplicate",
                severity=Severity.P1,
                title=f"Duplicate title on {url}",
                evidence=Evidence(url=url, value=t),
                recommendation=f"Title '{t}' is used on {title_counts[t]} pages. Make each unique.",
                effort=Effort.S,
                google_algo_ref="Duplicate content",
            ))
    desc_counts = Counter([d for _, d in descs if d])
    for (url, d) in descs:
        if d and desc_counts[d] > 1:
            findings.append(Finding(
                id="content.meta_desc.duplicate",
                severity=Severity.P2,
                title=f"Duplicate meta description on {url}",
                evidence=Evidence(url=url, value=d[:120]),
                recommendation="Make meta descriptions unique per page for better SERP CTR.",
                effort=Effort.S,
            ))

    # De-dup findings (one per id+url)
    seen = set()
    unique_findings: list = []
    for f in findings:
        key = (f.id, f.evidence.url)
        if key in seen:
            continue
        seen.add(key)
        unique_findings.append(f)

    score = score_from_findings(100, unique_findings)
    return SignalResult(name="content", score=score, findings=unique_findings, data=data)
