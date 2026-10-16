from src.quality.rules import run_data_quality_suite

class DataQualityValidator:
    @staticmethod
    def evaluate():
        scorecard = run_data_quality_suite()
        return scorecard

    @staticmethod
    def print_summary(scorecard):
        print(f"==================================================")
        print(f"BFSI DATA QUALITY SCORECARD")
        print(f"Status: {scorecard['overall_status']} | Pass Rate: {scorecard['pass_rate_pct']}%")
        print(f"Passed: {scorecard['passed_rules']} / {scorecard['total_rules']} Rules")
        print(f"==================================================")
        for r in scorecard["rule_details"]:
            symbol = "[OK]" if r["status"] == "PASSED" else "[FAIL]"
            print(f"{symbol} [{r['rule_id']}] {r['name']} ({r['table_name']}) - Violations: {r['violations_detected']}")
