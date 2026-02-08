import argparse
from core.mind_orchestrator import MindOrchestrator


def main():
    parser = argparse.ArgumentParser(description="Mind CLI")

    sub = parser.add_subparsers(dest="command")

    # mind run blueprint.yaml
    run_cmd = sub.add_parser("run", help="Run a blueprint")
    run_cmd.add_argument("blueprint", help="Path to blueprint YAML")

    # mind design blueprint.yaml
    design_cmd = sub.add_parser("design", help="Run meta-design pipeline")
    design_cmd.add_argument("blueprint", help="Path to blueprint YAML")

    # mind evolve
    sub.add_parser("evolve", help="Trigger evolution step")

    args = parser.parse_args()
    mind = MindOrchestrator()

    if args.command == "run":
        result = mind.run(args.blueprint)
        print(result)

    elif args.command == "design":
        result = mind.act(args.blueprint)
        print(result)

    elif args.command == "evolve":
        evo = mind.evolve()
        print(evo)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
