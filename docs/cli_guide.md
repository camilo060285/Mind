# Mind CLI - Terminal Interface

Use Mind directly from your terminal without writing Python code!

## Installation

### Automatic Installation
```bash
cd ~/mind
pip install -e .
```

This creates the `mind` command globally in your terminal.

### Verify Installation
```bash
mind status
```

You should see:
```
Mind System Status
✓ LLM Provider: LlamaCppProvider(model=phi, threads=2)
✓ Model: phi
✓ Status: Ready
```

---

## Quick Start

### Basic Question
```bash
$ mind ask "What is machine learning?"

Machine learning is a subset of artificial intelligence that enables
systems to learn and improve from experience without being explicitly
programmed...
```

### Get Help with a Problem
```bash
$ mind help "ModuleNotFoundError: No module named 'tensorflow'"

This error occurs when:
1. TensorFlow is not installed
2. Wrong Python environment
3. Virtual environment not activated

Solution:
1. Install: pip install tensorflow
...
```

### Analyze a File
```bash
$ mind analyze sales.csv "Find trends"

Based on the data analysis:

Top selling products:
1. Product A - 1,250 units ($50k revenue)
2. Product B - 890 units ($35k revenue)
...
```

### Create a Plan
```bash
$ mind plan "Build a cartoon generator"

Step-by-step plan:

1. Set up news scraper (Google Finance API)
2. Create LLM agent for story generation
3. Integrate with image generator (DALL-E)
4. Create animation pipeline
5. Set up daily scheduler
...
```

---

## Commands Reference

### `mind ask`
Ask Mind a question

**Usage:**
```bash
mind ask "Your question here"
mind ask "What is quantum computing?" --model qwen
mind ask "Explain machine learning" --verbose
mind ask "How do I sort a list?" --save
```

**Options:**
- `--model` {phi|qwen}: Which model to use (default: phi)
  - `phi`: Fast, lightweight responses
  - `qwen`: Better reasoning, slower
- `--verbose`: Show detailed output
- `--save`: Save result to history

### `mind plan`
Create a step-by-step plan for a task

**Usage:**
```bash
mind plan "Build a website"
mind plan "Create comic system" --json
mind plan "Setup database" --save > plan.txt
```

**Options:**
- `--json`: Output as structured JSON
- `--save`: Save to history

**Example Output:**
```
1. Design database schema
2. Create REST API endpoints
3. Build frontend
4. Deploy to production
```

### `mind analyze`
Analyze files with Mind

**Usage:**
```bash
mind analyze data.csv "Find trends"
mind analyze report.txt "Summarize"
mind analyze code.py "Find bugs" --format json
```

**Options:**
- `--format` {text|json|csv}: Output format (default: text)
- `--save`: Save analysis to history

**Supported Files:**
- CSV files (data analysis)
- Text files (content analysis)
- Code files (review)
- Any text-based file (up to 50KB)

### `mind help`
Get help with problems or errors

**Usage:**
```bash
mind help "I get this error: ..."
mind help "How do I optimize my code?"
mind help "My database query is slow"
```

**Provides:**
1. What's likely causing the problem
2. How to fix it
3. How to prevent it in future

### `mind learn`
Learn from YouTube videos (via transcript)

**Usage:**
```bash
mind learn "https://youtube.com/watch?v=..."
mind learn "https://youtube.com/watch?v=..." --save
```

**Note:** Requires video to have captions/transcripts available

**Output:**
- Video summary
- Key concepts
- Saved to knowledge base (with --save)

### `mind status`
Check Mind system status

**Usage:**
```bash
mind status
```

**Output:**
- LLM Provider info
- Current model
- System status
- Timestamp

### `mind history`
Show recent commands and results

**Usage:**
```bash
mind history
```

**Shows:** Last 10 commands with timestamps

### `mind version`
Show version and system info

**Usage:**
```bash
mind version
```

---

## Advanced Usage

### Pipe Input/Output

```bash
# Analyze output from another command
$ echo "Apple stock up 5%" | mind analyze - "What's happening?"

# Chain commands
$ ls *.txt | xargs -I {} mind analyze {} "Summarize"

# Save result to file
$ mind plan "Build system" > plan.txt

# Use result in another command
$ mind ask "Question" > answer.txt && cat answer.txt
```

### Shell Integration

```bash
# Add to .bashrc or .zshrc for alias
alias ask='mind ask'
alias plan='mind plan'

# Then use:
$ ask "What is Python?"
$ plan "Deploy application"
```

### In Scripts

```bash
#!/bin/bash

# Analyze file before processing
ERROR_SUMMARY=$(mind analyze error.log "Find root cause")
echo "Error Analysis: $ERROR_SUMMARY"

# Create plan for task
PLAN=$(mind plan "Process data files" --json)
echo "Execution Plan:"
echo "$PLAN" | jq .

# Get help if command fails
npm test || mind help "npm test failed"
```

### Automation

```bash
# Daily routine
$ mind ask "What should I focus on today?"

# Problem debugging
$ npm start 2>&1 | tee startup.log
$ mind help "$(tail -20 startup.log)"

# Code review
$ git diff main | mind analyze - "Any issues?"
```

---

## Use Cases

### For Developers

```bash
# Quick help on syntax
$ mind ask "How do I use map() in Python?"

# Debug errors
$ mind help "AttributeError: 'NoneType' object has no attribute..."

# Code review
$ mind analyze mycode.py "Any bugs or improvements?"
```

### For Data Analysts

```bash
# Analyze CSV
$ mind analyze data.csv "What are the key trends?"

# Plan analysis
$ mind plan "Analyze quarterly sales data"

# Quick insights
$ mind ask "How do I calculate regression in pandas?"
```

### For Project Managers

```bash
# Create project plan
$ mind plan "Redesign website platform"

# Get advice
$ mind ask "What's a realistic timeline for this project?"

# Problem solving
$ mind help "Team is behind schedule"
```

### For Content Creators

```bash
# Learn from video
$ mind learn "https://youtube.com/watch?v=..." --save

# Get ideas
$ mind ask "What are trending topics in AI?"

# Plan content
$ mind plan "Create video series about machine learning"
```

---

## Examples by Scenario

### Scenario 1: Daily Standup
```bash
# What to focus on
$ mind ask "Based on current priorities, what should I work on today?"

# Check status
$ mind status

# Review yesterday's work
$ mind analyze work_log.txt "What did I accomplish?"
```

### Scenario 2: Debugging an Issue
```bash
# Analyze error logs
$ mind analyze app.log "Why is production down?"

# Get detailed help
$ mind help "Database connection timeout"

# Create fix plan
$ mind plan "Implement connection pooling"
```

### Scenario 3: Learning Something New
```bash
# Learn from video
$ mind learn "https://youtube.com/watch?v=tutorial"

# Ask follow-up questions
$ mind ask "How do I apply this to my project?"

# Create implementation plan
$ mind plan "Implement what I learned"
```

### Scenario 4: Decision Making
```bash
# Analyze options
$ mind ask "Should we use Python or Go for this backend service?"

# Get pros/cons
$ mind analyze requirements.txt "Based on requirements, what tech stack?"

# Create implementation plan
$ mind plan "Setup development environment"
```

---

## Tips & Tricks

### 1. Save Frequently Used Questions
```bash
# Create aliases in .bashrc
alias ask-python='mind ask --model qwen'
```

### 2. Analyze Large Files
```bash
# Mind truncates at 50KB
# For larger files, use head/tail:
$ head -1000 large_file.txt | mind analyze - "Find issues"
```

### 3. JSON Output for Processing
```bash
# Get structured output
$ mind plan "Task" --json | jq '.steps'

# Process with tools
$ mind ask "List top 5" | grep "^[0-9]"
```

### 4. Redirect to File
```bash
# Save analysis
$ mind analyze data.csv "Trends" > analysis.txt

# Save plan
$ mind plan "Project" > project_plan.md
```

### 5. Chain Commands
```bash
# Multiple analyses
$ FILES=(*.csv); for f in "${FILES[@]}"; do
  echo "=== $f ===" >> report.txt
  mind analyze "$f" "Summary" >> report.txt
done
```

---

## Performance

### Response Times

| Command | Model | Time |
|---------|-------|------|
| ask | phi | 3-5 sec |
| ask | qwen | 10-15 sec |
| plan | phi | 5-10 sec |
| analyze | phi | 10-20 sec |
| help | qwen | 10-15 sec |

**Note:** First run may take longer (model loading)

### Tips for Speed

```bash
# Use phi for quick responses
$ mind ask "Question" --model phi

# Batch operations
$ mind analyze file1.csv "Summary" && mind analyze file2.csv "Summary"

# Save results to avoid re-running
$ mind status --save  # Saves for quick access later
```

---

## Troubleshooting

### Command Not Found
```bash
# Make sure installation completed
$ pip install -e ~/mind

# Verify
$ which mind
# Should show: /usr/local/bin/mind
```

### Mind Not Available
```bash
# Check Mind system
$ mind status

# If fails, check local LLM
$ ls ~/llama.cpp/build/bin/llama-completion

# Check models
$ ls ~/local_llms/models/llm_a/model.gguf
```

### Slow Responses
```bash
# Check system load
$ top

# Use faster model
$ mind ask "..." --model phi

# Reduce input size (for analyze)
$ mind analyze file.txt "..." < (head -500 file.txt)
```

### File Not Found
```bash
# Use absolute path
$ mind analyze /full/path/to/file.csv "..."

# Or use pwd
$ mind analyze "$(pwd)/file.csv" "..."
```

---

## Integration with Other Tools

### Git Integration
```bash
# Analyze git diff
$ git diff main | mind analyze - "Any issues?"

# Get commit message suggestion
$ mind ask "Write a git commit message for: $(git diff --stat)"
```

### CI/CD Integration
```bash
# In GitHub Actions
- run: |
    TEST_RESULT=$(npm test)
    if [ $? -ne 0 ]; then
      mind help "$TEST_RESULT"
    fi
```

### Editor Integration
```bash
# VS Code: Add to tasks.json
{
  "label": "Mind Help",
  "type": "shell",
  "command": "mind",
  "args": ["help", "${input:problem}"]
}
```

---

## Data Storage

### History Location
```
~/.mind/history.json
```

Last 100 commands automatically saved.

### View History
```bash
$ mind history

# Or read directly
$ cat ~/.mind/history.json
```

### Clear History
```bash
$ rm ~/.mind/history.json
```

---

## Environmental Variables

```bash
# Override default model
export MIND_LLM_MODEL=qwen

# Custom paths
export MIND_LLAMA_BIN=/custom/path/llama-completion
export MIND_MODELS_DIR=/custom/path/models
```

---

## Getting Help

```bash
# Show all commands
$ mind --help

# Help on specific command
$ mind ask --help
$ mind plan --help
$ mind analyze --help
```

---

## Next: Advanced Features Coming Soon

- 🔜 Real-time chat mode (`mind chat`)
- 🔜 Custom agents (`mind agent create`)
- 🔜 Integration with cloud LLMs
- 🔜 Results sharing (`mind share`)
- 🔜 Analytics dashboard

---

Enjoy using Mind from your terminal! 🧠
