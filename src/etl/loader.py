from typing import Dict, Any
from src.database.connection import warehouse_engine, WarehouseBase, WarehouseSessionLocal

class DataLoader:
    @staticmethod
    def load_all(transformed_data: Dict[str, Any]):
        print("[ETL:Load] Recreating Data Warehouse schema (Dimensions & Facts)...")
        WarehouseBase.metadata.drop_all(bind=warehouse_engine)
        WarehouseBase.metadata.create_all(bind=warehouse_engine)
        
        session = WarehouseSessionLocal()
        try:
            print(f"[ETL:Load] Loading {len(transformed_data['dim_dates'])} Date dimension rows...")
            session.bulk_save_objects(transformed_data["dim_dates"])
            session.commit()

            print(f"[ETL:Load] Loading {len(transformed_data['dim_products'])} Product dimension rows...")
            session.bulk_save_objects(transformed_data["dim_products"])
            session.commit()

            print(f"[ETL:Load] Loading {len(transformed_data['dim_branches'])} Branch dimension rows...")
            session.bulk_save_objects(transformed_data["dim_branches"])
            session.commit()

            print(f"[ETL:Load] Loading {len(transformed_data['dim_channels'])} Channel dimension rows...")
            session.bulk_save_objects(transformed_data["dim_channels"])
            session.commit()

            print(f"[ETL:Load] Loading {len(transformed_data['dim_customers'])} Customer dimension rows...")
            session.bulk_save_objects(transformed_data["dim_customers"])
            session.commit()

            print(f"[ETL:Load] Loading {len(transformed_data['fact_snapshots'])} Account Snapshot fact rows...")
            session.bulk_save_objects(transformed_data["fact_snapshots"])
            session.commit()

            print(f"[ETL:Load] Loading {len(transformed_data['fact_loans'])} Loan Performance fact rows...")
            session.bulk_save_objects(transformed_data["fact_loans"])
            session.commit()

            print(f"[ETL:Load] Loading {len(transformed_data['fact_txns'])} Transaction fact rows...")
            session.bulk_save_objects(transformed_data["fact_txns"])
            session.commit()

            print(f"[ETL:Load] Loading {len(transformed_data['fact_interactions'])} Customer Interaction fact rows...")
            session.bulk_save_objects(transformed_data["fact_interactions"])
            session.commit()

            print(f"[ETL:Load] Loading {len(transformed_data['c360_records'])} Customer 360 Mart rows...")
            session.bulk_save_objects(transformed_data["c360_records"])
            session.commit()

            print("[ETL:Load] Data Warehouse successfully loaded!")
        except Exception as e:
            session.rollback()
            print(f"[ETL:Load] Failed to load data warehouse: {e}")
            raise e
        finally:
            session.close()
