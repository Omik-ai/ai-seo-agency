# Skill: AI Overviews Optimization (AIO)

**Invokable by**: aio-optimization, on-page-seo, content-strategist, technical-seo
**Trigger**: AI Overview citation optimization, PAA targeting, extractive answer formatting

## AI Overview Signals Checklist

### FAQPage Schema
- [ ] FAQ section present on pages answering common questions
- [ ] FAQPage JSON-LD with `mainEntity` array
- [ ] Each Q has a concise A (50-150 words ideal)
- [ ] FAQ content visible in DOM (not schema-only)
- [ ] FAQ answers are direct and unambiguous

### HowTo Schema
- [ ] How-to content has HowTo JSON-LD
- [ ] `name`, `step` array, `totalTime` included
- [ ] Each step has `name` and `text`
- [ ] Step images included where helpful
- [ ] How-to URLs use /how-to/ or how- in path

### Question-Style Headings
- [ ] H2s phrased as questions on informational pages
- [ ] H3s expand on H2 with sub-questions
- [ ] Questions match real search queries (check Search Console)
- [ ] One clear answer follows each question heading

### Passage Fitness
- [ ] Direct answers placed immediately after question headings
- [ ] Answers are 40-60 words for paragraph snippets
- [ ] Answers start with the keyword ("[Keyword] is...")
- [ ] No fluff before the answer
- [ ] Each passage is self-contained (makes sense out of context)

### TL;DR / Summary Blocks
- [ ] Every article has a 2-3 sentence TL;DR near the top
- [ ] TL;DR is wrapped in a `<div class="summary">` or `<blockquote>`
- [ ] TL;DR answers the primary query of the page
- [ ] TL;DR is distinct from the introduction

### PAA (People Also Ask) Coverage
- [ ] Target PAA questions mapped to existing content
- [ ] Each mapped question has a dedicated H2 + answer
- [ ] New PAA questions are tracked monthly
- [ ] Unanswered PAA questions become content briefs

## Extractive Answer Formats

### Paragraph Snippet
```html
<h2>What is [Topic]?</h2>
<p>[Topic] is [direct definition in 40-60 words]. It [key characteristic] and is used for [primary use case].</p>
```

### List Snippet
```html
<h2>How to [Achieve Result]</h2>
<ol>
  <li><strong>Step 1:</strong> [Action]</li>
  <li><strong>Step 2:</strong> [Action]</li>
  <li><strong>Step 3:</strong> [Action]</li>
</ol>
```

### Table Snippet
```html
<h2>[Topic] Comparison</h2>
<table>
  <thead>
    <tr><th>Feature</th><th>Option A</th><th>Option B</th></tr>
  </thead>
  <tbody>
    <tr><td>Price</td><td>$X</td><td>$Y</td></tr>
  </tbody>
</table>
```

## PAA Mining Workflow

1. Search target keyword in Google
2. Expand all PAA questions (click each to reveal more)
3. Document:
   - Question text
   - Answer format (paragraph/list/table)
   - Source URL (if shown)
   - Related follow-up questions
4. Map each question to existing page or new content brief

## AI Overview Monitoring

### Manual Check (weekly for priority keywords)
- Search target query in incognito
- Document if AI Overview appears
- Note cited sources (are we included?)
- Note answer format
- Screenshot for trend tracking

### Competitive Tracking
| Query | AI Overview? | We Cited? | Competitor Cited? | Format |
|-------|-------------|-----------|-------------------|--------|
|       |             |           |                   |        |

## AIO Score Card

| Element | Weight | Score (1-5) | Weighted |
|---------|--------|-------------|----------|
| FAQPage schema | 15% | | |
| HowTo schema | 10% | | |
| Question headings | 15% | | |
| Passage fitness | 20% | | |
| TL;DR presence | 10% | | |
| PAA coverage | 15% | | |
| AI Overview citations | 15% | | |
| **Total** | **100%** | | **X/5** |
