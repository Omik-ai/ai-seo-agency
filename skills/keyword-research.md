# Skill: Keyword Research

**Invokable by**: keyword-research, content-strategist, seo-strategist, competitive-intel
**Trigger**: Any task requiring keyword discovery or analysis

## Methodology

### Step 1: Seed Keyword Generation
Start with the topic/business and expand:
- Direct product/service terms
- Problem/pain point terms
- Solution/benefit terms
- Industry jargon and terminology
- Question modifiers (how, what, why, when, where, best, vs)
- Long-tail variations
- Geo-modifiers (if local)

### Step 2: Keyword Expansion Techniques
- **Google Autocomplete**: Type seed → capture suggestions
- **People Also Ask**: Extract PAA questions from SERPs
- **Related Searches**: Bottom of SERP suggestions
- **Competitor Keywords**: What competitors rank for
- **Topic Modeling**: Semantically related terms
- **Forum Mining**: Reddit, Quora, niche forums for natural language
- **Alphabet Soup**: seed + a, seed + b, seed + c...

### Step 3: Data Enrichment
For each keyword, gather:
| Data Point | Source |
|-----------|--------|
| Search Volume | Keyword tools |
| Keyword Difficulty | Ahrefs/SEMrush |
| CPC | Google Keyword Planner |
| Search Intent | SERP analysis |
| SERP Features | SERP analysis |
| Current Ranking | GSC / rank tracker |
| Trend | Google Trends |

### Step 4: Intent Classification
| Signal | Intent | Priority for E-com | Priority for SaaS |
|--------|--------|-------------------|-------------------|
| how to, guide, what is | Informational | Medium | High |
| best, review, vs | Commercial Investigation | High | High |
| buy, price, discount | Transactional | Highest | Medium |
| [brand name] | Navigational | Low | Low |

### Step 5: Clustering
Group keywords by:
1. **Topical relevance** (same subject matter)
2. **Search intent** (same user need)
3. **SERP overlap** (same pages ranking for multiple keywords)

Each cluster = one content piece or page.

### Step 6: Prioritization Formula
```
Priority Score = (Volume × Intent_Value) / (Difficulty × Competition)

Where:
- Volume = monthly search volume (normalized 0-1)
- Intent_Value = informational(0.3), commercial(0.7), transactional(1.0)
- Difficulty = keyword difficulty (normalized 0-1)
- Competition = number of strong competitors in top 10
```

### Step 7: Keyword-to-Page Mapping
- Map each keyword cluster to existing page OR flag for new content
- Identify cannibalization (multiple pages targeting same cluster)
- Assign primary and secondary keywords per page

## Output Template

```markdown
| # | Keyword | Volume | KD | Intent | CPC | Cluster | Page | Priority |
|---|---------|--------|-----|--------|-----|---------|------|----------|
| 1 | | | | | | | | |
```

## Quality Checklist
- [ ] Minimum 50 keywords per topic area
- [ ] All keywords have volume and difficulty data
- [ ] Intent classified for every keyword
- [ ] Keywords grouped into clusters
- [ ] Clusters mapped to pages (existing or new)
- [ ] No keyword cannibalization issues
- [ ] Quick wins identified (position 4-20 keywords)
- [ ] Long-tail opportunities included
