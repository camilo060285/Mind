from core.meta_orchestrator import MetaOrchestrator

if __name__ == "__main__":
    orchestrator = MetaOrchestrator()
    result = orchestrator.run_blueprint("blueprints/meta_system.yaml")
    print("=== META PIPELINE RESULT ===")
    print(result)
