import time
import datetime
from src.quality.validator import DataQualityValidator
from src.etl.extractor import DataExtractor
from src.etl.transformer import DataTransformer
from src.etl.loader import DataLoader
from src.lineage.tracker import DataLineageTracker

class BFSIETLPipeline:
    @staticmethod
    def run():
        start_time = time.time()
        print("=================================================================")
        print("    STARTING ENTERPRISE BFSI CUSTOMER 360 ETL PIPELINE           ")
        print(f"    Timestamp: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  ")
        print("=================================================================")

        # Step 1: Pre-load Data Quality Checks
        print("\n--- PHASE 1: DATA QUALITY VALIDATION LAYER ---")
        scorecard = DataQualityValidator.evaluate()
        DataQualityValidator.print_summary(scorecard)
        if scorecard["overall_status"] != "HEALTHY":
            print("[WARN] Data quality warnings detected, proceeding with caution...")

        # Step 2: Extract
        print("\n--- PHASE 2: OPERATIONAL SOURCE DATA EXTRACTION ---")
        extracted_data = DataExtractor.extract_all()

        # Step 3: Transform
        print("\n--- PHASE 3: DIMENSIONAL MODELING & C360 TRANSFORMATION ---")
        transformed_data = DataTransformer.transform(extracted_data)

        # Step 4: Load
        print("\n--- PHASE 4: ENTERPRISE DATA WAREHOUSE LOADING ---")
        DataLoader.load_all(transformed_data)

        # Step 5: Data Lineage Refresh
        print("\n--- PHASE 5: DATA LINEAGE & METADATA REGISTRATION ---")
        lineage = DataLineageTracker.get_lineage_graph()
        print(f"[OK] Data Lineage DAG updated: {lineage['total_nodes']} nodes, {lineage['total_edges']} edges mapped.")

        duration = round(time.time() - start_time, 2)
        print("\n=================================================================")
        print(f" [SUCCESS] BFSI CUSTOMER 360 PIPELINE COMPLETED IN {duration}s")
        print(f" Loaded: {len(transformed_data['c360_records'])} Customer 360 profiles")
        print(f" Loaded: {len(transformed_data['fact_txns'])} Fact Transactions")
        print(f" Loaded: {len(transformed_data['fact_loans'])} Fact Loan Records")
        print("=================================================================")

        return {
            "status": "SUCCESS",
            "duration_seconds": duration,
            "quality_scorecard": scorecard,
            "records_processed": {
                "customers": len(transformed_data["c360_records"]),
                "transactions": len(transformed_data["fact_txns"]),
                "loans": len(transformed_data["fact_loans"]),
                "accounts": len(transformed_data["fact_snapshots"])
            }
        }

if __name__ == "__main__":
    BFSIETLPipeline.run()
