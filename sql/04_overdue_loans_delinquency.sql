-- ============================================================================
-- Business Question 3: Which customers have overdue loans?
-- Purpose: Monitor delinquency buckets (30, 60, 90+ DPD / NPL), overdue exposure,
-- and loan loss provisioning for credit risk & debt recovery operations.
-- ============================================================================

SELECT 
    c.customer_id,
    c.full_name,
    c.phone,
    c.email,
    c.customer_segment,
    c.credit_score,
    p.product_sub_type AS loan_type,
    lp.loan_id,
    lp.principal_amount,
    lp.outstanding_balance,
    lp.monthly_installment,
    lp.overdue_days,
    lp.overdue_amount,
    lp.delinquency_status,
    lp.is_npl,
    lp.loan_loss_provision,
    -- Aging Delinquency Bucket
    CASE 
        WHEN lp.overdue_days >= 90 THEN '90+ DPD (Default / NPL)'
        WHEN lp.overdue_days >= 60 THEN '60-89 DPD (Substandard)'
        WHEN lp.overdue_days >= 30 THEN '30-59 DPD (Special Mention)'
        WHEN lp.overdue_days > 0  THEN '1-29 DPD (Early Warning)'
        ELSE 'Current / Performing'
    END AS delinquency_aging_bucket,
    -- Recommended Recovery Strategy
    CASE 
        WHEN lp.overdue_days >= 90 THEN 'Legal Notice / Collateral Liquidation'
        WHEN lp.overdue_days >= 60 THEN 'Field Agent Visit & Restructuring Plan'
        WHEN lp.overdue_days >= 30 THEN 'Intensive Tele-Calling & SMS Followup'
        WHEN lp.overdue_days > 0  THEN 'Automated Grace Period Reminder'
        ELSE 'Standard Service'
    END AS recovery_workflow
FROM fact_loan_performance lp
JOIN dim_customer c ON lp.customer_key = c.customer_key
JOIN dim_product p ON lp.product_key = p.product_key
WHERE lp.overdue_days > 0 OR lp.overdue_amount > 0
ORDER BY lp.overdue_days DESC, lp.overdue_amount DESC;
