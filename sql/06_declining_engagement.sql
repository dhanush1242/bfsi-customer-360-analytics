-- ============================================================================
-- Business Question 5: Which customers have declining engagement?
-- Purpose: Early warning churn detection based on interaction frequency drops,
-- negative customer sentiment, pending disputes, and reduced transaction counts.
-- ============================================================================

SELECT 
    m.customer_id,
    m.full_name,
    m.customer_segment,
    m.total_deposit_balance,
    m.total_relationship_value,
    m.txn_count_30d,
    m.txn_volume_30d,
    m.interactions_count_90d,
    m.avg_sentiment_score,
    m.unresolved_complaints_count,
    m.engagement_status,
    -- Churn Risk Factor Scoring
    CASE 
        WHEN m.unresolved_complaints_count > 0 AND m.avg_sentiment_score < -0.3 THEN 'Critical Churn Risk (Complaint + Negative Sentiment)'
        WHEN m.txn_count_30d = 0 AND m.interactions_count_90d = 0 THEN 'Dormancy Risk (Zero Activity in 90 Days)'
        WHEN m.txn_count_30d <= 2 AND m.avg_sentiment_score < 0 THEN 'High Churn Risk (Declining Activity)'
        WHEN m.avg_sentiment_score < -0.2 THEN 'Dissatisfied Customer (Service Intervention Needed)'
        ELSE 'Moderate Retention Risk'
    END AS churn_risk_driver,
    -- Recommended Retention Action
    CASE 
        WHEN m.total_relationship_value > 50000 THEN 'Assign Dedicated Relationship Manager Immediate Outreach'
        WHEN m.unresolved_complaints_count > 0 THEN 'Escalate to Senior Complaints Lead for 24h Resolution'
        ELSE 'Trigger Personalized Re-engagement Email / Promotional Offer'
    END AS retention_action
FROM c360_customer_mart m
WHERE m.engagement_status IN ('DECLINING', 'DORMANT')
   OR m.avg_sentiment_score < -0.1
   OR (m.txn_count_30d <= 1 AND m.total_relationship_value > 10000)
ORDER BY m.total_relationship_value DESC, m.avg_sentiment_score ASC;
