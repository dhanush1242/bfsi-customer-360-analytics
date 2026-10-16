from typing import Dict, List, Any
import datetime

class DataLineageTracker:
    @staticmethod
    def get_lineage_graph() -> Dict[str, Any]:
        """
        Returns full Directed Acyclic Graph (DAG) for BFSI Customer 360 Data Lineage:
        Source DBs -> Ingestion/DQ -> EDW Star Schema -> Serving Mart -> Consumers
        """
        nodes = [
            # Layer 1: Operational Systems
            {"id": "src_customers", "label": "Core Banking: Customers", "layer": "Operational Sources", "type": "source", "records": "1,200"},
            {"id": "src_accounts", "label": "Deposit System: Accounts", "layer": "Operational Sources", "type": "source", "records": "1,666"},
            {"id": "src_loans", "label": "Loan Management System", "layer": "Operational Sources", "type": "source", "records": "650"},
            {"id": "src_credit_cards", "label": "Card Processor: Credit Cards", "layer": "Operational Sources", "type": "source", "records": "900"},
            {"id": "src_transactions", "label": "Payments Engine: Txns", "layer": "Operational Sources", "type": "source", "records": "25,000"},
            {"id": "src_kyc", "label": "Compliance: KYC & Sanctions", "layer": "Operational Sources", "type": "source", "records": "1,200"},
            {"id": "src_interactions", "label": "Omnichannel CRM: Interactions", "layer": "Operational Sources", "type": "source", "records": "4,000"},
            
            # Layer 2: Quality & Transformation Processing
            {"id": "dq_engine", "label": "Data Quality Validator (14 Rules)", "layer": "Data Quality Layer", "type": "processing", "status": "Active"},
            {"id": "etl_transformer", "label": "Dimensional Transformer & Keys", "layer": "ETL Pipeline", "type": "processing", "status": "Active"},
            
            # Layer 3: Star Schema Dimensions
            {"id": "dim_customer", "label": "dim_customer (SCD Conformed)", "layer": "EDW Star Schema", "type": "dimension"},
            {"id": "dim_date", "label": "dim_date (Enterprise Calendar)", "layer": "EDW Star Schema", "type": "dimension"},
            {"id": "dim_product", "label": "dim_product (Banking Catalog)", "layer": "EDW Star Schema", "type": "dimension"},
            {"id": "dim_branch", "label": "dim_branch (Geographic Network)", "layer": "EDW Star Schema", "type": "dimension"},
            {"id": "dim_channel", "label": "dim_channel (Omnichannel)", "layer": "EDW Star Schema", "type": "dimension"},
            
            # Layer 4: Star Schema Fact Tables
            {"id": "fact_transactions", "label": "fact_transactions", "layer": "EDW Star Schema", "type": "fact"},
            {"id": "fact_daily_account_snapshot", "label": "fact_daily_account_snapshot", "layer": "EDW Star Schema", "type": "fact"},
            {"id": "fact_loan_performance", "label": "fact_loan_performance", "layer": "EDW Star Schema", "type": "fact"},
            {"id": "fact_customer_interactions", "label": "fact_customer_interactions", "layer": "EDW Star Schema", "type": "fact"},
            
            # Layer 5: Customer 360 Mart
            {"id": "c360_customer_mart", "label": "c360_customer_mart (Consolidated)", "layer": "Data Mart Layer", "type": "mart"},
            
            # Layer 6: Consumption & Serving
            {"id": "api_c360", "label": "FastAPI Customer 360 REST API", "layer": "Serving & BI Layer", "type": "consumer"},
            {"id": "dashboard_bi", "label": "Customer 360 Executive Portal", "layer": "Serving & BI Layer", "type": "consumer"},
            {"id": "power_bi", "label": "Power BI Semantic Model", "layer": "Serving & BI Layer", "type": "consumer"}
        ]

        edges = [
            # Operational to DQ
            {"from": "src_customers", "to": "dq_engine"},
            {"from": "src_accounts", "to": "dq_engine"},
            {"from": "src_loans", "to": "dq_engine"},
            {"from": "src_credit_cards", "to": "dq_engine"},
            {"from": "src_transactions", "to": "dq_engine"},
            {"from": "src_kyc", "to": "dq_engine"},
            {"from": "src_interactions", "to": "dq_engine"},
            
            # DQ to ETL
            {"from": "dq_engine", "to": "etl_transformer"},
            
            # ETL to Dimensions
            {"from": "etl_transformer", "to": "dim_customer"},
            {"from": "etl_transformer", "to": "dim_date"},
            {"from": "etl_transformer", "to": "dim_product"},
            {"from": "etl_transformer", "to": "dim_branch"},
            {"from": "etl_transformer", "to": "dim_channel"},
            
            # ETL & Dimensions to Fact Tables
            {"from": "dim_customer", "to": "fact_transactions"},
            {"from": "dim_date", "to": "fact_transactions"},
            {"from": "dim_product", "to": "fact_transactions"},
            {"from": "dim_channel", "to": "fact_transactions"},
            {"from": "dim_branch", "to": "fact_transactions"},
            
            {"from": "dim_customer", "to": "fact_daily_account_snapshot"},
            {"from": "dim_date", "to": "fact_daily_account_snapshot"},
            {"from": "dim_product", "to": "fact_daily_account_snapshot"},
            
            {"from": "dim_customer", "to": "fact_loan_performance"},
            {"from": "dim_date", "to": "fact_loan_performance"},
            {"from": "dim_product", "to": "fact_loan_performance"},
            
            {"from": "dim_customer", "to": "fact_customer_interactions"},
            {"from": "dim_date", "to": "fact_customer_interactions"},
            {"from": "dim_channel", "to": "fact_customer_interactions"},
            
            # Facts & Dimensions to C360 Mart
            {"from": "dim_customer", "to": "c360_customer_mart"},
            {"from": "fact_daily_account_snapshot", "to": "c360_customer_mart"},
            {"from": "fact_loan_performance", "to": "c360_customer_mart"},
            {"from": "fact_transactions", "to": "c360_customer_mart"},
            {"from": "fact_customer_interactions", "to": "c360_customer_mart"},
            
            # Mart to Consumers
            {"from": "c360_customer_mart", "to": "api_c360"},
            {"from": "c360_customer_mart", "to": "dashboard_bi"},
            {"from": "c360_customer_mart", "to": "power_bi"}
        ]

        return {
            "last_updated": datetime.datetime.now().isoformat(),
            "nodes": nodes,
            "edges": edges,
            "total_nodes": len(nodes),
            "total_edges": len(edges)
        }
