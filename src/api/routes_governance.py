from fastapi import APIRouter
from src.quality.validator import DataQualityValidator
from src.lineage.tracker import DataLineageTracker
from src.etl.pipeline import BFSIETLPipeline

router = APIRouter(prefix="/api/governance", tags=["Data Governance & Pipeline"])

@router.get("/quality")
def get_data_quality_report():
    """
    Returns latest Data Quality Rule Suite validation scorecard and test results.
    """
    scorecard = DataQualityValidator.evaluate()
    return scorecard

@router.get("/lineage")
def get_data_lineage():
    """
    Returns full Data Lineage DAG nodes and directed edges.
    """
    return DataLineageTracker.get_lineage_graph()

@router.post("/trigger-pipeline")
def trigger_pipeline_run():
    """
    Trigger immediate execution of BFSI ETL pipeline and return results.
    """
    res = BFSIETLPipeline.run()
    return res
