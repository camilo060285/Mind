import argparse
from core.meta_orchestrator import MetaOrchestrator

def main():
    parser = argparse.ArgumentParser(description="Mind meta-system runner")
    parser.add_argument(
        "blueprint",
        help="Path to blueprint YAML file (e.g., blueprints/meta_system.yaml)",
    )
    args = parser.parse_args()

    orchestrator = MetaOrchestrator()
    result = orchestrator.run_blueprint(args.blueprint)

    print("=== META PIPELINE RESULT ===")
    print(result)

if __name__ == "__main__":
    main()
