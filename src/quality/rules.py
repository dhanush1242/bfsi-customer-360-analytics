import datetime
from typing import List, Dict, Any
from sqlalchemy import text
from src.database.connection import SourceSessionLocal, WarehouseSessionLocal

class DataQualityRule:
    def __init__(self, rule_id: str, name: str, table_name: str, rule_type: str, query: str, severity: str = "ERROR", threshold: float = 0.0):
        self.rule_id = rule_id
        self.name = name
        self.table_name = table_name
        self.rule_type = rule_type # COMPLETENESS, VALIDITY, REFERENTIAL_INTEGRITY, ANOMALY
        self.query = query
        self.severity = severity # WARNING, ERROR, CRITICAL
        self.threshold = threshold # Max permissible failed records or percentage

# Standard BFSI DQ Rule Suite
BFSI_DATA_QUALITY_RULES: List[DataQualityRule] = [
    # 1. Completeness Checks
    DataQualityRule(
        rule_id="DQ-COMP-01",
        name="Customer ID Not Null",
        table_name="src_customers",
        rule_type="COMPLETENESS",
        query="SELECT COUNT(*) FROM src_customers WHERE customer_id IS NULL OR customer_id = ''",
        severity="CRITICAL"
    ),
    DataQualityRule(
        rule_id="DQ-COMP-02",
        name="Account Balance Not Null",
        table_name="src_accounts",
        rule_type="COMPLETENESS",
        query="SELECT COUNT(*) FROM src_accounts WHERE current_balance IS NULL",
        severity="CRITICAL"
    ),
    DataQualityRule(
        rule_id="DQ-COMP-03",
        name="Loan Outstanding Balance Not Null",
        table_name="src_loans",
        rule_type="COMPLETENESS",
        query="SELECT COUNT(*) FROM src_loans WHERE outstanding_balance IS NULL",
        severity="CRITICAL"
    ),
    DataQualityRule(
        rule_id="DQ-COMP-04",
        name="Transaction Timestamp & Amount Not Null",
        table_name="src_transactions",
        rule_type="COMPLETENESS",
        query="SELECT COUNT(*) FROM src_transactions WHERE amount IS NULL OR transaction_timestamp IS NULL",
        severity="CRITICAL"
    ),
    
    # 2. Validity & Range Checks
    DataQualityRule(
        rule_id="DQ-VAL-01",
        name="Credit Score Valid Range (300 to 850)",
        table_name="src_customers",
        rule_type="VALIDITY",
        query="SELECT COUNT(*) FROM src_customers WHERE credit_score < 300 OR credit_score > 850",
        severity="ERROR"
    ),
    DataQualityRule(
        rule_id="DQ-VAL-02",
        name="AML Risk Score Range (0.0 to 100.0)",
        table_name="src_kyc",
        rule_type="VALIDITY",
        query="SELECT COUNT(*) FROM src_kyc WHERE aml_risk_score < 0.0 OR aml_risk_score > 100.0",
        severity="ERROR"
    ),
    DataQualityRule(
        rule_id="DQ-VAL-03",
        name="Overdue Days Non-Negative",
        table_name="src_loans",
        rule_type="VALIDITY",
        query="SELECT COUNT(*) FROM src_loans WHERE overdue_days < 0",
        severity="ERROR"
    ),
    DataQualityRule(
        rule_id="DQ-VAL-04",
        name="Transaction Amount Positive",
        table_name="src_transactions",
        rule_type="VALIDITY",
        query="SELECT COUNT(*) FROM src_transactions WHERE amount <= 0",
        severity="ERROR"
    ),
    DataQualityRule(
        rule_id="DQ-VAL-05",
        name="Customer Age Above 18",
        table_name="src_customers",
        rule_type="VALIDITY",
        query="SELECT COUNT(*) FROM src_customers WHERE date_of_birth > DATE('now', '-18 years')",
        severity="WARNING"
    ),
    
    # 3. Referential Integrity Checks
    DataQualityRule(
        rule_id="DQ-REF-01",
        name="Orphan Accounts (No Valid Customer)",
        table_name="src_accounts",
        rule_type="REFERENTIAL_INTEGRITY",
        query="SELECT COUNT(*) FROM src_accounts a LEFT JOIN src_customers c ON a.customer_id = c.customer_id WHERE c.customer_id IS NULL",
        severity="CRITICAL"
    ),
    DataQualityRule(
        rule_id="DQ-REF-02",
        name="Orphan Loans (No Valid Customer)",
        table_name="src_loans",
        rule_type="REFERENTIAL_INTEGRITY",
        query="SELECT COUNT(*) FROM src_loans l LEFT JOIN src_customers c ON l.customer_id = c.customer_id WHERE c.customer_id IS NULL",
        severity="CRITICAL"
    ),
    DataQualityRule(
        rule_id="DQ-REF-03",
        name="Orphan Credit Cards (No Valid Customer)",
        table_name="src_credit_cards",
        rule_type="REFERENTIAL_INTEGRITY",
        query="SELECT COUNT(*) FROM src_credit_cards cc LEFT JOIN src_customers c ON cc.customer_id = c.customer_id WHERE c.customer_id IS NULL",
        severity="CRITICAL"
    ),
    DataQualityRule(
        rule_id="DQ-REF-04",
        name="Orphan Transactions (No Valid Account)",
        table_name="src_transactions",
        rule_type="REFERENTIAL_INTEGRITY",
        query="SELECT COUNT(*) FROM src_transactions t LEFT JOIN src_accounts a ON t.account_id = a.account_id WHERE a.account_id IS NULL",
        severity="CRITICAL"
    ),
    
    # 4. Anomaly Detection
    DataQualityRule(
        rule_id="DQ-ANOM-01",
        name="Outlier Transaction Volume (> $50,000 Single Ticket)",
        table_name="src_transactions",
        rule_type="ANOMALY",
        query="SELECT COUNT(*) FROM src_transactions WHERE amount > 50000",
        severity="WARNING"
    ),
    DataQualityRule(
        rule_id="DQ-ANOM-02",
        name="High Delinquency Accounts without Flagged Status",
        table_name="src_loans",
        rule_type="ANOMALY",
        query="SELECT COUNT(*) FROM src_loans WHERE overdue_days > 90 AND status NOT IN ('DELINQUENT', 'DEFAULTED')",
        severity="ERROR"
    )
]

def run_data_quality_suite() -> Dict[str, Any]:
    session = SourceSessionLocal()
    results = []
    total_passed = 0
    total_failed = 0
    start_time = datetime.datetime.now()

    try:
        for rule in BFSI_DATA_QUALITY_RULES:
            try:
                res = session.execute(text(rule.query)).scalar()
                failed_count = int(res) if res is not None else 0
                status = "PASSED" if failed_count <= rule.threshold else "FAILED"
                
                if status == "PASSED":
                    total_passed += 1
                else:
                    total_failed += 1

                results.append({
                    "rule_id": rule.rule_id,
                    "name": rule.name,
                    "table_name": rule.table_name,
                    "rule_type": rule.rule_type,
                    "severity": rule.severity,
                    "status": status,
                    "violations_detected": failed_count,
                    "threshold": rule.threshold
                })
            except Exception as e:
                total_failed += 1
                results.append({
                    "rule_id": rule.rule_id,
                    "name": rule.name,
                    "table_name": rule.table_name,
                    "rule_type": rule.rule_type,
                    "severity": rule.severity,
                    "status": "ERROR",
                    "violations_detected": -1,
                    "error_message": str(e)
                })

        duration = (datetime.datetime.now() - start_time).total_seconds()
        pass_rate = round((total_passed / len(BFSI_DATA_QUALITY_RULES)) * 100, 2) if BFSI_DATA_QUALITY_RULES else 100.0

        scorecard = {
            "execution_timestamp": datetime.datetime.now().isoformat(),
            "duration_seconds": round(duration, 3),
            "total_rules": len(BFSI_DATA_QUALITY_RULES),
            "passed_rules": total_passed,
            "failed_rules": total_failed,
            "pass_rate_pct": pass_rate,
            "overall_status": "HEALTHY" if pass_rate >= 90.0 else "UNHEALTHY",
            "rule_details": results
        }
        return scorecard
    finally:
        session.close()
