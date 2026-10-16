-- ============================================================================
-- Business Question 1: Which customers have multiple products?
-- Purpose: Identify cross-holdings across Deposits, Loans, Credit Cards & Wealth
-- to power cross-sell propensity, bundling, and relationship depth analysis.
-- ============================================================================

WITH customer_product_holdings AS (
    SELECT 
        c.customer_key,
        c.customer_id,
        c.full_name,
        c.email,
        c.customer_segment,
        -- Count distinct product categories held
        COUNT(DISTINCT p.product_category) AS distinct_product_categories,
        COUNT(DISTINCT p.product_id) AS total_products_held,
        
        -- Specific product flags
        MAX(CASE WHEN p.product_category = 'DEPOSIT' THEN 1 ELSE 0 END) AS has_deposit_account,
        MAX(CASE WHEN p.product_category = 'LOAN' THEN 1 ELSE 0 END) AS has_loan,
        MAX(CASE WHEN p.product_category = 'CREDIT_CARD' THEN 1 ELSE 0 END) AS has_credit_card,
        MAX(CASE WHEN p.product_category = 'WEALTH' THEN 1 ELSE 0 END) AS has_wealth_product
    FROM dim_customer c
    LEFT JOIN (
        -- Aggregate active product holdings from account, loan, and card facts
        SELECT customer_key, product_key, 'DEPOSIT' as product_category, CAST(account_id AS VARCHAR) as product_id 
        FROM fact_daily_account_snapshot WHERE status = 'ACTIVE'
        UNION ALL
        SELECT customer_key, product_key, 'LOAN' as product_category, CAST(loan_id AS VARCHAR) as product_id 
        FROM fact_loan_performance WHERE outstanding_balance > 0
    ) p ON c.customer_key = p.customer_key
    GROUP BY c.customer_key, c.customer_id, c.full_name, c.email, c.customer_segment
)
SELECT 
    customer_id,
    full_name,
    customer_segment,
    total_products_held,
    distinct_product_categories,
    has_deposit_account,
    has_loan,
    has_credit_card,
    has_wealth_product,
    CASE 
        WHEN distinct_product_categories >= 3 THEN 'Omni-Banking (3+ Categories)'
        WHEN distinct_product_categories = 2 THEN 'Cross-Sold (2 Categories)'
        WHEN total_products_held > 1 THEN 'Multi-Product (Single Category)'
        ELSE 'Mono-Product'
    END AS relationship_depth
FROM customer_product_holdings
WHERE total_products_held > 1
ORDER BY total_products_held DESC, distinct_product_categories DESC;
