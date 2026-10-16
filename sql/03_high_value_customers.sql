-- ============================================================================
-- Business Question 2: Which customers are high-value?
-- Purpose: Calculate customer Lifetime Value (LTV), total Assets Under Management (AUM),
-- credit utilization, and transaction volume to segment VIP/Private Banking prospects.
-- ============================================================================

SELECT 
    m.customer_id,
    m.full_name,
    m.customer_segment,
    m.credit_score,
    m.total_deposit_balance,
    m.total_loan_outstanding,
    m.total_credit_limit,
    m.total_relationship_value,
    m.txn_volume_30d,
    m.ltv_score,
    m.risk_tier,
    -- Value Tier Classification
    CASE 
        WHEN m.ltv_score >= 85 OR m.total_relationship_value >= 250000 THEN 'Tier 1: Private Wealth'
        WHEN m.ltv_score >= 65 OR m.total_relationship_value >= 100000 THEN 'Tier 2: Premier Affluent'
        WHEN m.ltv_score >= 45 OR m.total_relationship_value >= 40000 THEN 'Tier 3: Emerging Wealth'
        ELSE 'Tier 4: Standard Retail'
    END AS value_classification,
    -- Cross-sell recommendation flag
    CASE 
        WHEN m.total_deposit_balance > 100000 AND m.active_loans_count = 0 THEN 'Prime Mortgage/Investment Lead'
        WHEN m.total_deposit_balance > 50000 AND m.credit_cards_count = 0 THEN 'Premium Card Cross-Sell'
        WHEN m.has_overdue_loan = 1 THEN 'High Value at Risk (Collections Intervention)'
        ELSE 'Relationship Maintenance'
    END AS strategic_action
FROM c360_customer_mart m
WHERE m.is_high_value = 1 OR m.total_relationship_value >= 75000
ORDER BY m.total_relationship_value DESC, m.ltv_score DESC;
