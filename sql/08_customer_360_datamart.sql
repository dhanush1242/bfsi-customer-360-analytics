-- ============================================================================
-- Customer 360 Consolidated Mart Transformation SQL
-- Aggregates data from Star Schema Conformed Dimensions and Fact tables
-- into the single-row-per-customer 360 analytical mart.
-- ============================================================================

CREATE OR REPLACE VIEW view_c360_customer_summary AS
WITH deposit_agg AS (
    SELECT 
        customer_key,
        COUNT(DISTINCT account_id) AS deposit_accounts_count,
        SUM(current_balance) AS total_deposit_balance
    FROM fact_daily_account_snapshot
    WHERE status = 'ACTIVE'
    GROUP BY customer_key
),
loan_agg AS (
    SELECT 
        customer_key,
        COUNT(DISTINCT loan_id) AS active_loans_count,
        SUM(outstanding_balance) AS total_loan_outstanding,
        MAX(overdue_days) AS max_overdue_days,
        SUM(overdue_amount) AS total_overdue_amount,
        MAX(CASE WHEN overdue_days > 0 THEN 1 ELSE 0 END) AS has_overdue_loan
    FROM fact_loan_performance
    WHERE outstanding_balance > 0
    GROUP BY customer_key
),
txn_agg AS (
    SELECT 
        customer_key,
        COUNT(fact_txn_key) AS txn_count_30d,
        SUM(amount) AS txn_volume_30d,
        AVG(amount) AS avg_txn_amount_30d
    FROM fact_transactions
    WHERE created_timestamp >= CURRENT_DATE - INTERVAL '30 days'
    GROUP BY customer_key
),
interaction_agg AS (
    SELECT 
        customer_key,
        COUNT(interaction_fact_key) AS interactions_count_90d,
        AVG(sentiment_score) AS avg_sentiment_score,
        SUM(CASE WHEN is_complaint = 1 AND resolution_status != 'RESOLVED' THEN 1 ELSE 0 END) AS unresolved_complaints_count
    FROM fact_customer_interactions
    GROUP BY customer_key
)
SELECT 
    c.customer_key,
    c.customer_id,
    c.full_name,
    c.email,
    c.phone,
    c.city,
    c.state,
    c.customer_segment,
    c.credit_score,
    c.credit_score_bracket,
    c.kyc_status,
    c.aml_risk_score,
    c.risk_tier,
    
    COALESCE(d.deposit_accounts_count, 0) AS deposit_accounts_count,
    COALESCE(d.total_deposit_balance, 0.0) AS total_deposit_balance,
    
    COALESCE(l.active_loans_count, 0) AS active_loans_count,
    COALESCE(l.total_loan_outstanding, 0.0) AS total_loan_outstanding,
    COALESCE(l.max_overdue_days, 0) AS max_overdue_days,
    COALESCE(l.total_overdue_amount, 0.0) AS total_overdue_amount,
    COALESCE(l.has_overdue_loan, 0) AS has_overdue_loan,
    
    (COALESCE(d.deposit_accounts_count, 0) + COALESCE(l.active_loans_count, 0)) AS total_products_held,
    CASE WHEN (COALESCE(d.deposit_accounts_count, 0) + COALESCE(l.active_loans_count, 0)) > 1 THEN 1 ELSE 0 END AS has_multiple_products,
    
    (COALESCE(d.total_deposit_balance, 0.0) + COALESCE(l.total_loan_outstanding, 0.0)) AS total_relationship_value,
    
    COALESCE(t.txn_count_30d, 0) AS txn_count_30d,
    COALESCE(t.txn_volume_30d, 0.0) AS txn_volume_30d,
    COALESCE(t.avg_txn_amount_30d, 0.0) AS avg_txn_amount_30d,
    
    COALESCE(i.interactions_count_90d, 0) AS interactions_count_90d,
    COALESCE(i.avg_sentiment_score, 0.0) AS avg_sentiment_score,
    COALESCE(i.unresolved_complaints_count, 0) AS unresolved_complaints_count
FROM dim_customer c
LEFT JOIN deposit_agg d ON c.customer_key = d.customer_key
LEFT JOIN loan_agg l ON c.customer_key = l.customer_key
LEFT JOIN txn_agg t ON c.customer_key = t.customer_key
LEFT JOIN interaction_agg i ON c.customer_key = i.customer_key;
