# Enterprise BFSI Customer 360 - Power BI Implementation Guide

This guide details how to connect Power BI Desktop to the Customer 360 Data Warehouse, configure the Star Schema relationships, and import the certified BFSI DAX measures library.

---

## 1. Connecting Power BI to the Data Warehouse

### Option A: PostgreSQL Warehouse (Docker / Production)
1. In Power BI Desktop, click **Get Data** &rarr; **PostgreSQL database**.
2. **Server**: `localhost:5432` (or your cloud server hostname).
3. **Database**: `bfsi_enterprise_dw`.
4. **Data Connectivity mode**:
   - **DirectQuery**: For real-time updates and low-latency drill-down.
   - **Import**: Recommended for complex DAX aggregations and offline caching.
5. Select the following Star Schema tables:
   - `dim_customer`
   - `dim_date`
   - `dim_product`
   - `dim_channel`
   - `dim_branch`
   - `fact_transactions`
   - `fact_daily_account_snapshot`
   - `fact_loan_performance`
   - `fact_customer_interactions`
   - `c360_customer_mart`

### Option B: REST API Direct Connector (Web / JSON)
1. Click **Get Data** &rarr; **Web**.
2. URL: `http://localhost:8000/api/c360/customers?limit=500`
3. Expand JSON records into tabular format.

---

## 2. Dimensional Model Relationships (Star Schema)

In Power BI **Model View**, establish the following 1-to-Many (`1:*`), Single-Direction relationships:

| From Table (Dimension 1) | Dimension Key | To Table (Fact *) | Foreign Key | Cross Filter Direction |
|---|---|---|---|---|
| `dim_customer` | `customer_key` | `fact_transactions` | `customer_key` | Single |
| `dim_customer` | `customer_key` | `fact_daily_account_snapshot` | `customer_key` | Single |
| `dim_customer` | `customer_key` | `fact_loan_performance` | `customer_key` | Single |
| `dim_customer` | `customer_key` | `fact_customer_interactions` | `customer_key` | Single |
| `dim_customer` | `customer_key` | `c360_customer_mart` | `customer_key` | Single |
| `dim_date` | `date_key` | `fact_transactions` | `date_key` | Single |
| `dim_date` | `date_key` | `fact_daily_account_snapshot` | `date_key` | Single |
| `dim_date` | `date_key` | `fact_loan_performance` | `date_key` | Single |
| `dim_product` | `product_key` | `fact_transactions` | `product_key` | Single |
| `dim_channel` | `channel_key` | `fact_transactions` | `channel_key` | Single |

---

## 3. Certified BFSI DAX Measures Library

Create a dedicated measure table called `_BFSI Measures` in Power BI and paste the following DAX calculations:

### 1. Cross-Sell Penetration Ratio
```dax
Cross-Sell Ratio % = 
DIVIDE(
    CALCULATE(
        COUNTROWS(c360_customer_mart),
        c360_customer_mart[has_multiple_products] = TRUE()
    ),
    COUNTROWS(c360_customer_mart),
    0
) * 100
```

### 2. Total Assets Under Management (AUM)
```dax
Total AUM = 
SUM(c360_customer_mart[total_deposit_balance]) + 
SUM(c360_customer_mart[total_loan_outstanding])
```

### 3. Non-Performing Loan (NPL) Ratio %
```dax
NPL Ratio % = 
DIVIDE(
    CALCULATE(
        SUM(fact_loan_performance[outstanding_balance]),
        fact_loan_performance[is_npl] = TRUE()
    ),
    SUM(fact_loan_performance[outstanding_balance]),
    0
) * 100
```

### 4. Overdue Delinquency Rate
```dax
Delinquency Rate % = 
DIVIDE(
    CALCULATE(
        COUNTROWS(c360_customer_mart),
        c360_customer_mart[has_overdue_loan] = TRUE()
    ),
    COUNTROWS(c360_customer_mart),
    0
) * 100
```

### 5. Average Customer Lifetime Value (LTV)
```dax
Avg LTV Score = 
AVERAGE(c360_customer_mart[ltv_score])
```

### 6. Net Credit Card Utilization %
```dax
Card Utilization % = 
DIVIDE(
    SUM(c360_customer_mart[total_credit_outstanding]),
    SUM(c360_customer_mart[total_credit_limit]),
    0
) * 100
```

### 7. At-Risk Churn Rate %
```dax
Churn Risk Rate % = 
DIVIDE(
    CALCULATE(
        COUNTROWS(c360_customer_mart),
        c360_customer_mart[engagement_status] = "DECLINING" || 
        c360_customer_mart[engagement_status] = "DORMANT"
    ),
    COUNTROWS(c360_customer_mart),
    0
) * 100
```
