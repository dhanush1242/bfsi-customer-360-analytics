import sys
from src.etl.pipeline import BFSIETLPipeline

def main():
    try:
        BFSIETLPipeline.run()
    except Exception as e:
        print(f"[FATAL] Pipeline failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
