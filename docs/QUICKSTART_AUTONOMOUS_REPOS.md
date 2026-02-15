# Autonomous Repository Generation - Quick Start

## TL;DR - Create a System in 30 Seconds

```python
from mind.system_generator import SystemGenerator

# Initialize generator
gen = SystemGenerator()

# Create a system
system = gen.create(
    name="My Analytics Engine",
    goal="Process and analyze metrics",
    features=["data_collection", "analysis", "alerts"],
    tools=["pandas", "mongodb"],
)

# View results
print(system.get_output_summary())
```

That's it! A complete, independent Git repository was created at:
```
~/.mind_systems/my_analytics_engine_abc12345/
```

---

## What Just Happened?

✅ Created independent Git repository  
✅ Generated complete system structure  
✅ Created README with user guide  
✅ Set up main + dev branches  
✅ Added system to Mind's registry  
✅ Generated all system files  

---

## Access Your System

```bash
# Navigate to system
cd ~/.mind_systems/my_analytics_engine_abc12345

# Review documentation
cat README.md

# Check metadata
cat system.metadata.json

# See current branch
git branch

# View commit history
git log --oneline
```

---

## Development Workflow

```bash
# Create feature branch
git checkout -b feature/my-feature

# Make changes
# ... edit agents, blueprints, etc ...

# Commit changes
git add .
git commit -m "Add my feature"

# Test and merge to dev
git checkout dev
git merge feature/my-feature

# When stable, merge to main
git checkout main
git merge dev
```

---

## Query Systems from Mind

```python
from mind.system_generator import SystemGenerator, SystemRegistry

gen = SystemGenerator()

# Get all systems
all_systems = gen.registry.list_systems()
print(f"Total systems: {len(all_systems)}")

# Find system by name
system = gen.registry.get_system_by_name("my_analytics_engine")
print(f"Repository: {system['repository']['path']}")

# Get statistics
stats = gen.registry.get_registry_summary()
print(f"Active: {stats['active']}, Archived: {stats['archived']}")
```

---

## Command-Line (CLI)

### Create with prompts
```bash
mind systems create
# Interactive prompts guide you through creation
```

### List all systems
```bash
mind systems list

# Or with format option
mind systems list --format json
```

### Get system details
```bash
mind systems info system_id_here
```

### Show statistics
```bash
mind systems stats
```

### Archive a system
```bash
mind systems archive system_id_here
```

---

## System Types

Specify what kind of system you're creating:

```python
system = gen.create(
    name="My System",
    goal="System purpose",
    features=["f1", "f2"],
    tools=[],
    system_type="agent-cluster",  # Choose one:
    # "agent-cluster"    - Multi-agent coordination
    # "subsystem"         - Specialized subsystem
    # "service"           - Microservice
    # "pipeline"          - Data/ML pipeline
    # "monitor"           - Monitoring system
    # "orchestrator"      - Orchestration layer
)
```

---

## Generated System Contents

```
my_analytics_engine_abc12345/
├── README.md                    ← Start here!
├── system.metadata.json         ← System info
├── requirements.txt             ← Dependencies
├── cli.py                       ← Entry point
├── agents/                      ← Put your agents here
├── models/                      ← Data schemas
├── blueprints/                  ← Workflows (YAML)
├── core/                        ← Orchestration logic
├── tests/                       ← Test suite
├── config/                      ← Configuration
├── data/                        ← Runtime data
└── .git/                        ← Full Git history
```

---

## Set Up Development Environment

```bash
cd ~/.mind_systems/my_analytics_engine_abc12345

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the system
python cli.py
```

---

## Key Features

### Independent Repository
- Fully independent Git repo
- Complete version control
- Can be deployed anywhere
- No automatic sync with Mind

### Comprehensive Metadata
- System ID and creation time
- Mind version at creation
- Full specification
- List of dependencies

### Dual Branch Model
- **main**: Stable, production-ready
- **dev**: Active development

### Self-Documenting
- Professional README
- System metadata JSON
- Code comments and docstrings
- Architecture documentation

---

## System Metadata

Each system includes `system.metadata.json`:

```json
{
  "system": {
    "id": "abc12345",
    "name": "my_analytics_engine",
    "type": "subsystem"
  },
  "generation": {
    "mind_version": "0.1.0",
    "generated_at": "2026-02-15T10:30:00"
  },
  "specification": {
    "name": "My Analytics Engine",
    "goal": "Process and analyze metrics",
    "features": ["data_collection", "analysis", "alerts"],
    "tools": ["pandas", "mongodb"]
  },
  "repository": {
    "path": "/home/user/.mind_systems/...",
    "branches": ["main", "dev"]
  }
}
```

---

## Practical Examples

### Example 1: Data Pipeline

```python
system = gen.create(
    name="ETL Pipeline",
    goal="Extract, transform, load data",
    features=["extraction", "validation", "loading"],
    tools=["pandas", "postgres"],
    system_type="pipeline",
)
```

### Example 2: Monitor System

```python
system = gen.create(
    name="System Monitor",
    goal="Monitor and alert on metrics",
    features=["metrics_collection", "alerting", "dashboard"],
    tools=["prometheus", "grafana"],
    system_type="monitor",
)
```

### Example 3: Multi-Agent System

```python
system = gen.create(
    name="Research Agents",
    goal="Coordinate research agents",
    features=["search", "analysis", "synthesis"],
    tools=["langchain", "openai"],
    system_type="agent-cluster",
)
```

---

## Customizing Your System

### Add New Agent

1. Create `agents/my_agent.py`
2. Implement your agent logic
3. Register in `core/orchestrator.py`
4. Add tests in `tests/test_my_agent.py`
5. Commit changes: `git add . && git commit -m "Add my agent"`

### Update Blueprints

1. Edit YAML files in `blueprints/`
2. Define your workflows
3. Test with agents
4. Commit changes

### Modify Configuration

1. Update `config/settings.yaml`
2. Add new parameters as needed
3. Load in your code
4. Commit changes

---

## Common Questions

### Q: Where is my system stored?
**A**: `~/.mind_systems/system_name_id/`

### Q: Is it separate from Mind?
**A**: Yes! Completely independent with its own Git repo.

### Q: Can I deploy it separately?
**A**: Yes! Copy the directory anywhere and it works.

### Q: Can I fork it?
**A**: Yes! Full Git history available.

### Q: How do I know what Mind knows about it?
**A**: Check `~/.mind/system_registry/systems.json`

### Q: Can I delete a system?
**A**: Yes! Both repo and registry entry can be deleted independently.

---

## Troubleshooting

### System doesn't appear in registry

```python
from mind.system_generator import SystemRegistry
registry = SystemRegistry()
registry._load_registry()
systems = registry.list_systems()
```

### Git errors

```bash
cd ~/.mind_systems/my_system_id
git status
git log
git branch -a
```

### Missing dependencies

```bash
cd ~/.mind_systems/my_system_id
pip install -r requirements.txt
```

---

## File Locations

- **System repositories**: `~/.mind_systems/`
- **Registry**: `~/.mind/system_registry/systems.json`
- **Mind home**: `~/.mind/`

---

## Next Steps

1. **Review** the generated README.md in your system
2. **Explore** the generated structure
3. **Customize** agents and blueprints
4. **Add** your business logic
5. **Test** thoroughly
6. **Deploy** when ready

---

## Documentation

For more detailed information, see:

- **User Guide**: [AUTONOMOUS_REPOSITORY_GENERATION.md](AUTONOMOUS_REPOSITORY_GENERATION.md)
- **Architecture**: [ARCHITECTURE_AUTONOMOUS_REPOS.md](ARCHITECTURE_AUTONOMOUS_REPOS.md)
- **Implementation**: [IMPLEMENTATION_AUTONOMOUS_REPOS.md](IMPLEMENTATION_AUTONOMOUS_REPOS.md)
- **Examples**: `examples/system_generation_example.py`

---

## Support

Having issues? Check:

1. System README.md
2. system.metadata.json
3. This quick start guide
4. Full documentation in docs/

---

**Happy system generation! 🚀**
