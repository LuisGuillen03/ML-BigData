# Iowa Liquor Sales - Exploratory Data Analysis

**Dataset:** `bigquery-public-data.iowa_liquor_sales.sales`  
**Analysis Date:** December 3, 2025

---

## Dataset Overview

### Meta Information
| Metric | Value |
|--------|-------|
| **Total Records** | 32,816,143 |
| **Date Range** | 2012-01-03 to 2025-10-31 |
| **Time Span** | ~13.8 years |

### Cardinalities
| Dimension | Unique Values |
|-----------|---------------|
| **Stores** | 3,337 |
| **Cities** | 504 |
| **Items** | 15,183 |
| **Categories** | 185 |

---

## Data Quality

### Sale Dollars Distribution
| Percentile | Value ($) |
|------------|-----------|
| **P50 (Median)** | $78.66 |
| **P90** | $269.88 |
| **P99** | $1,185.60 |

### Missing Values
| Field | Null Count |
|-------|------------|
| **sale_dollars** | 10 |
| **category** | 16,974 |
| **city** | 84,575 |

**Data Quality:** 99.96% complete (only 0.04% missing values)

---

## Top 10 Categories by Sales

| Rank | Category ID | Total Sales ($) | Transactions |
|------|-------------|-----------------|--------------|
| 1 | 1012100.0 | $495,078,200 | 2,778,490 |
| 2 | 1031100.0 | $441,329,100 | 2,988,622 |
| 3 | 1011200.0 | $288,427,900 | 1,859,256 |
| 4 | 1081600.0 | $219,643,200 | 1,360,017 |
| 5 | 1062400.0 | $169,326,700 | 861,360 |
| 6 | 1022200.0 | $152,794,300 | 668,286 |
| 7 | 1031080.0 | $145,760,500 | 1,265,930 |
| 8 | 1022100.0 | $143,383,100 | 849,580 |
| 9 | 1011400.0 | $119,534,300 | 538,956 |
| 10 | 1011100.0 | $117,536,600 | 1,213,606 |

**Total Top 10 Sales:** $2.29 billion (approximately)

---

## Sample Data

```
         date  store_number   city  category  item_number  sale_dollars  bottles_sold
0  2018-02-26          4986  FLOYD   1031080        10624         20.04             3
1  2018-02-26          4986  FLOYD   1011200        15856        100.44             2
2  2018-02-26          4986  FLOYD   1062400        29997         78.00            12
3  2018-02-26          4986  FLOYD   1062400        35917         75.12            12
4  2018-02-26          4986  FLOYD   1062400        36307         72.96            12
```

---

## Key Insights

1. **Large Scale Dataset:** 32.8M records spanning 13+ years
2. **High Cardinality:** 15K+ unique items across 185 categories
3. **Geographic Coverage:** 504 cities with 3,337 stores
4. **Data Quality:** Excellent (99.96% complete)
5. **Sales Distribution:** 
   - Median transaction: $78.66
   - 90th percentile: $269.88
   - Top 10 categories account for significant volume

---

## Suitability for ML

✅ **Large volume:** 32M+ records ideal for distributed processing  
✅ **Temporal data:** 13+ years for time-series analysis  
✅ **Rich features:** Store, city, category, item dimensions  
✅ **Clean data:** Minimal missing values  
✅ **Regression target:** sale_dollars (continuous variable)

**Recommended Model:** Linear Regression to predict sale_dollars based on:
- bottles_sold
- volume_sold_liters
- temporal features (day_of_week, quarter, is_weekend)
- derived features (price_per_bottle, volume_per_bottle)
