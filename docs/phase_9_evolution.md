"""Phase 9: Evolution Engine - System Self-Improvement and Adaptation."""

# Phase 9: Evolution Engine
# ==========================

"""
The Evolution Engine enables the Mind system to learn from experiences and
automatically improve its performance through hypothesis generation, A/B testing,
and adaptive improvement application.

Key Components:
1. ExperienceLogger: Records system executions with metrics
2. MetricsCollector: Real-time performance monitoring
3. HypothesisGenerator: Generates improvement hypotheses from data
4. ExperimentFramework: A/B testing system for validation
5. AdaptationEngine: Applies validated improvements automatically

Lifecycle:
1. Execute system tasks → log experiences with metrics
2. Analyze experiences → generate improvement hypotheses  
3. Create experiments → test hypotheses with variants
4. Validate results → apply successful improvements
5. Measure impact → iterate for continuous improvement
"""

# Example 1: Logging System Experiences
# =====================================

from mind.evolution import ExperienceLogger, SystemMetrics

# Initialize logger
logger = ExperienceLogger()

# Record a system execution
metrics = SystemMetrics(
    goal="Deploy Mind system",
    execution_time=2.5,  # seconds
    result_success=True,
    agents_used=3,
    decisions_made=5,
    memory_accessed=10,
    memory_stored=3,
    error_count=0,
    quality_score=0.85,
)

exp_id = logger.log_experience(
    metrics, 
    observation="System successfully deployed with good performance"
)
print(f"Logged experience: {exp_id}")


# Example 2: Collecting Runtime Metrics
# ======================================

from mind.evolution import MetricsCollector

collector = MetricsCollector()

# Record metrics during execution
collector.record_metric("latency", 0.45, category="performance")
collector.record_metric("memory_used", 256, category="resource")
collector.increment_counter("api_calls", 5)
collector.increment_counter("cache_hits", 3)

# Finalize and get summary
summary = collector.finalize()
print(f"Total execution time: {summary['total_time']:.2f}s")
print(f"Metrics recorded: {summary['total_time']}")


# Example 3: Analyzing and Generating Hypotheses
# ==============================================

from mind.evolution import HypothesisGenerator

# Initialize with experience logger
gen = HypothesisGenerator(logger)

# Analyze recent experiences and generate improvement ideas
hypotheses = gen.analyze_performance()
print(f"Generated {len(hypotheses)} improvement hypotheses")

# Get top-priority hypotheses
top_hyps = gen.get_top_hypotheses(limit=3)
for hyp in top_hyps:
    print(f"- {hyp.title}")
    print(f"  Expected improvement: +{hyp.expected_improvement*100:.0f}%")
    print(f"  Priority: {hyp.priority}/5")


# Example 4: Running A/B Testing Experiments
# =========================================

from mind.evolution import ExperimentFramework

framework = ExperimentFramework()

# Create an A/B test for a hypothesis
experiment = framework.create_experiment(
    hypothesis_id="hyp_001",
    title="Optimize Decision Making",
    description="Test improved reasoning strategy",
    variant_a_name="Current Strategy",
    variant_a_config={"strategy": "default"},
    variant_b_name="Enhanced Strategy", 
    variant_b_config={"strategy": "enhanced", "context_depth": "full"},
    sample_size=10,
)

print(f"Created experiment: {experiment.id}")

# Record results from running each variant
for i in range(10):
    # Control variant (A) results
    framework.record_result(experiment.id, "A", 0.75 + (i % 3) * 0.05)
    # Treatment variant (B) results
    framework.record_result(experiment.id, "B", 0.82 + (i % 3) * 0.05)

# Check results
experiment = framework.get_experiment(experiment.id)
print(f"Experiment completed. Winner: {experiment.winner}")


# Example 5: Adaptation Engine - Automatic Improvement
# ===================================================

from mind.evolution import AdaptationEngine

# Initialize full evolution system
engine = AdaptationEngine(logger, gen, framework)

# Analyze system and propose improvements
strategy = engine.get_adaptation_strategy()
print(f"Current hypotheses: {len(strategy['current_hypotheses'])}")
print(f"Active experiments: {strategy['active_experiments']}")
print("Recommendations:")
for rec in strategy['recommendations']:
    print(f"  - {rec}")

# Analyze impact of improvements so far
impact = engine.get_impact_analysis()
print(f"\nImprovement Impact:")
print(f"  Success rate delta: {impact['improvements']['success_rate_delta']*100:+.1f}%")
print(f"  Speed improvement: {impact['improvements']['speed_delta_percent']:+.1f}%")


# Example 6: CLI Integration (Phase 7-8-9)
# ========================================

# The interactive shell includes evolution commands:
#
# > mind> analyze
# Generated 3 improvement hypotheses:
# 1. Improve Decision Making (Priority: 5)
#    Expected improvement: 15%
# 2. Optimize Execution Speed (Priority: 4)
#    Expected improvement: 25%
# ...
#
# > mind> list_hyp
# Top 5 hypotheses:
# 1. Improve Decision Making - Priority: 5, Expected: +15%
# ...
#
# > mind> propose_exp hyp_001
# Created experiment: exp_abc123
# Title: Test: Improve Decision Making
#
# > mind> record_result exp_abc123 A 0.85
# Result recorded. Progress: 1/20
#
# > mind> adapt_status
# Adaptation Engine Status:
# Hypotheses generated: 3
# Experiments created: 1
# Improvements applied: 2
#
# > mind> evo_stats
# Evolution Statistics:
# Total experiences: 25
# Success rate: 85.0%
# Avg execution time: 2.15s
# Validated improvements: 3


# Example 7: Custom Hypothesis Generation
# =======================================

# Generate a custom hypothesis
custom_hyp = gen.generate_hypothesis(
    title="Implement Caching Layer",
    description="Add intelligent caching to reduce computation",
    expected_improvement=0.3,
    priority=4,
    required_changes=[
        "Add caching module",
        "Implement cache invalidation",
        "Monitor cache hit rate",
    ],
    affected_components=["orchestrator", "agents"],
    estimated_effort="high",
)

print(f"Created hypothesis: {custom_hyp.id}")

# Validate after running experiment
gen.validate_hypothesis(custom_hyp.id, True)


# Example 8: System Statistics and Monitoring
# ==========================================

# Get comprehensive system statistics
logger_stats = logger.get_statistics()
print(f"Experience Statistics:")
print(f"  Total experiences: {logger_stats['total_experiences']}")
print(f"  Success rate: {logger_stats['successful_rate']*100:.1f}%")
print(f"  Average time: {logger_stats['avg_execution_time']:.2f}s")

hyp_stats = gen.get_statistics()
print(f"\nHypothesis Statistics:")
print(f"  Total hypotheses: {hyp_stats['total_hypotheses']}")
print(f"  Validated: {hyp_stats['validated']}")
print(f"  Successful: {hyp_stats['successful_validations']}")

exp_stats = framework.get_statistics()
print(f"\nExperiment Statistics:")
print(f"  Total experiments: {exp_stats['total_experiments']}")
print(f"  Completed: {exp_stats['completed']}")
print(f"  Active: {exp_stats['active']}")


# Example 9: Data Persistence and Export
# =====================================

# Export experiences for analysis
logger.export("/tmp/experiences.json")
print("Exported experiences to /tmp/experiences.json")

# Export experiment results
framework.export_results("/tmp/experiment_results.json")
print("Exported experiment results")

# Clear old experiences (older than 30 days)
cleared = logger.clear_old_experiences(days=30)
print(f"Cleared {cleared} old experiences")


# Example 10: Integration with Mind Agents
# ======================================

from mind.core.mind_orchestrator import MindOrchestrator

# Initialize orchestrator (which has evolution system)
orchestrator = MindOrchestrator()

# Execute goal as normal
goal = "Deploy system with monitoring"
result = orchestrator.execute(goal)

# Evolution system automatically:
# 1. Logs the execution with metrics
# 2. Analyzes performance against baseline
# 3. Generates improvement hypotheses if needed
# 4. Proposes A/B tests for new ideas
# 5. Applies validated improvements


# Storage Locations
# ================
#
# Experience logs: ~/.mind_experiences/
#   - experiences.jsonl: JSONL log of all experiences
#
# Experiment data: ~/.mind_experiments/
#   - experiments.jsonl: JSONL log of all experiments
#
# Integration with Memory (Phase 8):
#   - Important learnings stored in memory system
#   - Experiences tagged for classification
#   - Memories used as context for hypotheses


# Configuration
# =============
#
# Custom storage paths:
from pathlib import Path
custom_logger = ExperienceLogger(Path("/custom/path/experiences"))
custom_framework = ExperimentFramework(Path("/custom/path/experiments"))
#
# Create full evolution system:
logger = ExperienceLogger()
generator = HypothesisGenerator(logger)
framework = ExperimentFramework()
engine = AdaptationEngine(logger, generator, framework)


# Performance Optimization Tips
# ==============================
#
# 1. Log meaningful metrics (execution_time, quality_score, error_count)
# 2. Set appropriate sample sizes for experiments (10-20 per variant)
# 3. Review hypotheses regularly for validation
# 4. Prioritize high-impact improvements (high expected improvement + low effort)
# 5. Archive old experiences to maintain performance
# 6. Use A/B tests to validate major changes before full rollout
