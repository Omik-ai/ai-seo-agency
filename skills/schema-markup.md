# Skill: Schema Markup Implementation

**Invokable by**: technical-seo, on-page-seo, ecommerce-seo, local-seo
**Trigger**: Structured data implementation or audit

## Schema Type Decision Tree

```
What type of page?
├── Homepage → Organization + WebSite + SiteNavigationElement
├── About Page → Organization + Person (if founder/team)
├── Blog Post → Article + BreadcrumbList + FAQ (if applicable)
├── Product Page → Product + Offer + AggregateRating + Review + BreadcrumbList
├── Category Page → CollectionPage + BreadcrumbList + ItemList
├── Service Page → Service + Provider + AreaServed + BreadcrumbList
├── Local Business → LocalBusiness + OpeningHours + GeoCoordinates
├── FAQ Page → FAQPage + BreadcrumbList
├── How-To → HowTo + BreadcrumbList
├── Event → Event + Performer + Location
├── Recipe → Recipe + NutritionInformation
└── Video → VideoObject + BreadcrumbList
```

## Common Schema Templates

### Organization (Homepage)
```json
{
  "@context": "https://schema.org",
  "@type": "Organization",
  "name": "[Business Name]",
  "url": "[Website URL]",
  "logo": "[Logo URL]",
  "description": "[Business description]",
  "foundingDate": "[YYYY]",
  "sameAs": [
    "[Facebook URL]",
    "[Twitter URL]",
    "[LinkedIn URL]"
  ],
  "contactPoint": {
    "@type": "ContactPoint",
    "telephone": "[Phone]",
    "contactType": "customer service"
  }
}
```

### Article (Blog Posts)
```json
{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "[Title]",
  "description": "[Meta description]",
  "image": "[Featured image URL]",
  "author": {
    "@type": "Person",
    "name": "[Author Name]",
    "url": "[Author page URL]"
  },
  "publisher": {
    "@type": "Organization",
    "name": "[Publisher]",
    "logo": {
      "@type": "ImageObject",
      "url": "[Logo URL]"
    }
  },
  "datePublished": "[YYYY-MM-DD]",
  "dateModified": "[YYYY-MM-DD]"
}
```

### Product (E-commerce)
```json
{
  "@context": "https://schema.org",
  "@type": "Product",
  "name": "[Product Name]",
  "image": "[Product Image URL]",
  "description": "[Product description]",
  "sku": "[SKU]",
  "brand": {
    "@type": "Brand",
    "name": "[Brand]"
  },
  "offers": {
    "@type": "Offer",
    "url": "[Product URL]",
    "priceCurrency": "[USD]",
    "price": "[Price]",
    "availability": "https://schema.org/InStock",
    "seller": {
      "@type": "Organization",
      "name": "[Seller]"
    }
  },
  "aggregateRating": {
    "@type": "AggregateRating",
    "ratingValue": "[4.5]",
    "reviewCount": "[100]"
  }
}
```

### LocalBusiness
```json
{
  "@context": "https://schema.org",
  "@type": "LocalBusiness",
  "name": "[Business Name]",
  "image": "[Image URL]",
  "address": {
    "@type": "PostalAddress",
    "streetAddress": "[Street]",
    "addressLocality": "[City]",
    "addressRegion": "[State]",
    "postalCode": "[Zip]",
    "addressCountry": "[US]"
  },
  "geo": {
    "@type": "GeoCoordinates",
    "latitude": "[lat]",
    "longitude": "[lng]"
  },
  "telephone": "[Phone]",
  "openingHoursSpecification": [
    {
      "@type": "OpeningHoursSpecification",
      "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
      "opens": "09:00",
      "closes": "17:00"
    }
  ]
}
```

### FAQPage
```json
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "[Question 1]",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "[Answer 1]"
      }
    },
    {
      "@type": "Question",
      "name": "[Question 2]",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "[Answer 2]"
      }
    }
  ]
}
```

### BreadcrumbList (Universal)
```json
{
  "@context": "https://schema.org",
  "@type": "BreadcrumbList",
  "itemListElement": [
    {
      "@type": "ListItem",
      "position": 1,
      "name": "Home",
      "item": "[Homepage URL]"
    },
    {
      "@type": "ListItem",
      "position": 2,
      "name": "[Category]",
      "item": "[Category URL]"
    },
    {
      "@type": "ListItem",
      "position": 3,
      "name": "[Current Page]"
    }
  ]
}
```

## Validation Checklist
- [ ] Valid JSON-LD syntax (no errors in Schema.org validator)
- [ ] No warnings in Google Rich Results Test
- [ ] All required properties present
- [ ] URLs are absolute (not relative)
- [ ] Dates in ISO 8601 format
- [ ] Images are accessible and appropriate size
- [ ] No misleading or spammy markup
- [ ] Schema matches visible page content
- [ ] Placed in `<head>` via `<script type="application/ld+json">`
