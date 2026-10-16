-- ============================================================================
-- Business Question 4: What is the monthly transaction volume?
-- Purpose: Track monthly payment throughput, debit vs credit velocity,
-- channel adoption (Digital vs Branch/ATM), and average ticket size.
-- ============================================================================

SELECT 
    d.year,
    d.month,
    d.month_name,
    COUNT(t.fact_txn_key) AS total_transaction_count,
    ROUND(CAST(SUM(t.amount) AS NUMERIC), 2) AS total_transaction_volume,
    ROUND(CAST(AVG(t.amount) AS NUMERIC), 2) AS average_ticket_size,
    
    -- Volume breakdown by transaction type
    ROUND(CAST(SUM(CASE WHEN t.transaction_type IN ('DEBIT', 'ATM_WITHDRAWAL', 'POS') THEN t.amount ELSE 0 END) AS NUMERIC), 2) AS total_debit_volume,
    ROUND(CAST(SUM(CASE WHEN t.transaction_type IN ('CREDIT', 'WIRE') THEN t.amount ELSE 0 END) AS NUMERIC), 2) AS total_credit_volume,
    
    -- Channel volume distribution
    ROUND(CAST(SUM(CASE WHEN ch.channel_type = 'DIGITAL' THEN t.amount ELSE 0 END) AS NUMERIC), 2) AS digital_channel_volume,
    ROUND(CAST(SUM(CASE WHEN ch.channel_type = 'PHYSICAL' THEN t.amount ELSE 0 END) AS NUMERIC), 2) AS physical_channel_volume,
    
    -- Digital adoption percentage
    ROUND(CAST(100.0 * SUM(CASE WHEN ch.channel_type = 'DIGITAL' THEN 1 ELSE 0 END) / COUNT(t.fact_txn_key) AS NUMERIC), 2) AS digital_txn_share_pct,
    
    -- Suspected Fraud Volume
    SUM(CASE WHEN t.is_fraud_flag = 1 THEN 1 ELSE 0 END) AS flagged_fraud_count,
    ROUND(CAST(SUM(CASE WHEN t.is_fraud_flag = 1 THEN t.amount ELSE 0 END) AS NUMERIC), 2) AS flagged_fraud_volume
FROM fact_transactions t
JOIN dim_date d ON t.date_key = d.date_key
JOIN dim_channel ch ON t.channel_key = ch.channel_key
GROUP BY d.year, d.month, d.month_name
ORDER BY d.year ASC, d.month ASC;
