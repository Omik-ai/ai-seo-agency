# Skill: Generative Engine Optimization (GEO)

**Invokable by**: geo-optimization, seo-strategist, content-strategist, technical-seo
**Trigger**: LLM citation optimization, entity building, brand mention strategy

## Entity Graph Building Checklist

### sameAs Network
- [ ] Wikipedia page (or Wikidata entry)
- [ ] Crunchbase profile
- [ ] LinkedIn Company Page
- [ ] X/Twitter profile
- [ ] GitHub organization (if tech)
- [ ] Google Business Profile (if local)
- [ ] Apple App Store / Google Play (if app)
- [ ] Product Hunt (if product)
- [ ] G2 / Capterra (if SaaS)
- [ ] Trustpilot / Reviews.io (if reviews matter)
- [ ] Industry-specific directories
- [ ] Authoritative news mentions (for citation)

### Organization Schema (homepage)
```json
{
  "@context": "https://schema.org",
  "@type": "Organization",
  "name": "Brand Name",
  "url": "https://brand.com",
  "logo": "https://brand.com/logo.png",
  "sameAs": [
    "https://twitter.com/brand",
    "https://linkedin.com/company/brand",
    "https://github.com/brand",
    "https://crunchbase.com/organization/brand"
  ],
  "contactPoint": {
    "@type": "ContactPoint",
    "contactType": "customer support",
    "email": "support@brand.com"
  }
}
```

### Person Schema (for key authors/experts)
```json
{
  "@context": "https://schema.org",
  "@type": "Person",
  "name": "Author Name",
  "url": "https://brand.com/author/name",
  "sameAs": [
    "https://twitter.com/author",
    "https://linkedin.com/in/author",
    "https://github.com/author"
  ],
  "jobTitle": "Role",
  "worksFor": {
    "@type": "Organization",
    "name": "Brand Name"
  }
}
```

## Citation-Worthy Content Frameworks

### The Definitive Guide
- 3,000+ words, single URL authority on a topic
- Clear H2/H3 hierarchy with direct answers
- Data tables, original research, or proprietary insights
- Updated quarterly with `dateModified`

### The Comparison Matrix
- Side-by-side feature comparison (use `<table>`)
- Own the "X vs Y" query in LLM training data
- Include your product/service naturally

### The Original Research
- Survey data, benchmark reports, industry stats
- Cited by journalists and bloggers (feeds LLMs)
- Publish as PDF + interactive web page

### The FAQ Hub
- 50+ questions with concise 40-60 word answers
- FAQPage schema on every question cluster
- Target the queries LLMs answer most

## Knowledge Graph Submission Protocol

1. **Wikidata** — Create item if notable; add "official website" and "Twitter handle"
2. **Google Knowledge Panel** — Claim via Search Console; suggest edits
3. **Bing Entity** — Submit via Bing Webmaster Tools
4. **Apple Maps / Siri** — Submit via Apple Business Register
5. **Amazon Alexa** — Ensure Wikipedia + authoritative sources mention you

## Community Seeding Targets

### Reddit
- Relevant subreddits (not promotional)
- Answer questions with deep expertise
- Link to definitive guides only when genuinely helpful
- Build karma and account age before any self-promotion

### Quora
- Answer questions in your domain
- Use real name (builds author entity)
- Link to in-depth content on your site
- Space: 3-5 answers/week

### StackExchange / StackOverflow
- Technical domains only
- High-quality answers get cited in LLM training
- Include links to documentation or deep dives

### Hacker News
- Launch major content pieces
- Engage authentically in comments
- No marketing speak

## LLM-Readable Content Structure

### Passage Extraction Friendly
- Each H2/H3 should be answerable in 1-2 sentences immediately following
- Use bold for key takeaways
- Numbered lists for step-by-step processes
- Tables for comparisons

### Definitive Statements
- Start sections with direct definitions: "[Topic] is..."
- Avoid hedging language: "might", "could", "some say"
- Use "In 202X, [source] found that..." for data-backed claims

### Source Density
- Every claim should have a source link
- Link to .edu, .gov, and peer-reviewed papers when possible
- Cite your own original research prominently

## Monitoring

### Manual LLM Citation Check (monthly)
Run these queries on ChatGPT, Perplexity, Claude, Gemini:
- "What is [brand]?"
- "Best [category] tools"
- "[brand] vs [competitor]"
- "How to [problem your product solves]"

Document:
- Is brand mentioned?
- Is brand URL cited?
- Is competitor cited instead?
- What content is referenced?

### Entity Search Operators
- `site:wikipedia.org "Brand Name"`
- `site:crunchbase.com "Brand Name"`
- `site:reddit.com "Brand Name"`
- `site:news.ycombinator.com "Brand Name"`

## GEO Score Card

| Element | Weight | Score (1-5) | Weighted |
|---------|--------|-------------|----------|
| sameAs completeness | 20% | | |
| Knowledge Graph presence | 20% | | |
| Citation-worthy content | 20% | | |
| Community presence | 15% | | |
| Author entity authority | 15% | | |
| LLM citation rate | 10% | | |
| **Total** | **100%** | | **X/5** |
