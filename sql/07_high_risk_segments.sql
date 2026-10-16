-- ============================================================================
-- Business Question 6: Which customer segments have the highest risk?
-- Purpose: Portfolio risk evaluation by customer segment, combining credit scores,
-- AML risk indices, delinquency incidence, and non-performing loan exposure.
-- ============================================================================

SELECT 
    m.customer_segment,
    COUNT(m.customer_key) AS total_customers_in_segment,
    
    -- Credit Risk Metrics
    ROUND(CAST(AVG(m.credit_score) AS NUMERIC), 1) AS avg_credit_score,
    SUM(CASE WHEN m.credit_score < 600 THEN 1 ELSE 0 END) AS subprime_customer_count,
    ROUND(CAST(100.0 * SUM(CASE WHEN m.credit_score < 600 THEN 1 ELSE 0 END) / COUNT(m.customer_key) AS NUMERIC), 2) AS subprime_customer_pct,
    
    -- Loan Delinquency & NPL Exposure
    SUM(CASE WHEN m.has_overdue_loan = 1 THEN 1 ELSE 0 END) AS delinquent_customers_count,
    ROUND(CAST(100.0 * SUM(CASE WHEN m.has_overdue_loan = 1 THEN 1 ELSE 0 END) / COUNT(m.customer_key) AS NUMERIC), 2) AS delinquency_rate_pct,
    ROUND(CAST(SUM(m.total_overdue_amount) AS NUMERIC), 2) AS total_segment_overdue_amount,
    
    -- Financial Balances
    ROUND(CAST(SUM(m.total_deposit_balance) AS NUMERIC), 2) AS total_segment_deposits,
    ROUND(CAST(SUM(m.total_loan_outstanding) AS NUMERIC), 2) AS total_segment_loans,
    
    -- AML & Regulatory Risk Metrics
    ROUND(CAST(AVG(m.aml_risk_score) AS NUMERIC), 2) AS avg_aml_risk_score,
    SUM(CASE WHEN m.risk_tier IN ('HIGH', 'CRITICAL') THEN 1 ELSE 0 END) AS high_aml_risk_customers_count,
    
    -- Composite Risk Index
    ROUND(CAST(AVG(m.composite_risk_score) AS NUMERIC), 2) AS avg_composite_risk_score,
    
    -- Segment Risk Rating
    CASE 
        WHEN AVG(m.composite_risk_score) >= 45 OR (100.0 * SUM(CASE WHEN m.has_overdue_loan = 1 THEN 1 ELSE 0 END) / COUNT(m.customer_key)) > 15 THEN 'HIGH RISK PORTFOLIO'
        WHEN AVG(m.composite_risk_score) >= 30 OR (100.0 * SUM(CASE WHEN m.has_overdue_loan = 1 THEN 1 ELSE 0 END) / COUNT(m.customer_key)) > 8 THEN 'MODERATE RISK PORTFOLIO'
        ELSE 'LOW RISK / STABLE PORTFOLIO'
    END AS segment_risk_classification
FROM c360_customer_mart m
GROUP BY m.customer_segment
ORDER BY avg_composite_risk_score DESC, total_segment_overdue_amount DESC;
