# Mind System - Simple Practical Examples

These are real examples you can try RIGHT NOW. Copy and paste them!

---

## Simplest Example: Ask Mind a Question

**What it does:** You ask Mind a question, and it answers.

```python
from mind.cognition import init_llm

# Start mind with the fast AI
mind = init_llm(model="phi")

# Ask a simple question
question = "What is the capital of France?"
answer = mind.generate(question)
print(answer)
```

**Result:** You get an answer back

**Time:** 2-3 seconds

---

## Example 2: Understand What You Want

**What it does:** You describe a project, Mind figures out what type it is

```python
from mind.cognition import init_llm

mind = init_llm(model="phi")

# Describe what you want
task_description = "Create an animated chart showing how temperature changes throughout the day"

# Let Mind understand it
task_info = mind.parse_task(task_description)

print("Task Type:", task_info["task_type"])
print("Goal:", task_info["goal"])
print("Steps needed:", task_info["subtasks"])
```

**Result:** Mind breaks down your idea into steps

**Example Output:**
```
Task Type: animation
Goal: Show temperature changes with animation
Steps needed:
  - Get temperature data
  - Create chart
  - Add animation
  - Save as video
```

---

## Example 3: Get a Step-by-Step Plan

**What it does:** Tell Mind a goal, it creates a plan

```python
from mind.cognition import init_llm

mind = init_llm(model="phi")

# Your goal
goal = "Build a website that shows real-time weather"

# Available helpers
available_agents = [
    {"name": "DataCollector", "role": "gathers weather data"},
    {"name": "WebDesigner", "role": "creates website layout"},
    {"name": "Animator", "role": "makes things move smoothly"},
]

# Get the plan
plan = mind.create_plan(goal, available_agents)

print("Plan:")
for step in plan:
    print("  •", step)
```

**Result:** A step-by-step plan for your project

---

## Example 4: Think Through a Problem

**What it does:** Give Mind a problem, it thinks through it

```python
from mind.cognition import init_llm

mind = init_llm(model="qwen")  # Use smart model for this

# Your problem
problem = """
I have a shop. Sales are slow. 
What could be wrong and how do I fix it?
"""

# Let Mind think about it
reasoning = mind.reasoning(problem)

print("Analysis:")
print(reasoning)
```

**Result:** Mind explains possible causes and solutions

---

## Example 5: Practical: Analyze Business Data

**What it does:** You have data, Mind analyzes it

```python
from mind.cognition import init_llm

mind = init_llm(model="qwen")  # Better for analysis

# Your data (as text)
data_description = """
Monthly Sales Last 3 Months:
January: $5,000
February: $4,500
March: $3,200
"""

# Ask Mind to analyze it
prompt = f"""
Analyze this data and tell me:
1. What's happening?
2. Why is this happening?
3. What should we do about it?

Data:
{data_description}
"""

analysis = mind.generate(prompt, n_predict=300)
print(analysis)
```

**Result:** You get an analysis with insights and suggestions

---

## Example 6: Get Creative Ideas

**What it does:** Ask Mind for ideas

```python
from mind.cognition import init_llm

mind = init_llm(model="qwen")

# Your challenge
request = "I want to promote my online shop. Give me 5 creative ideas."

# Get ideas
ideas = mind.generate(request, n_predict=400)

print("Creative Ideas:")
print(ideas)
```

**Result:** 5 creative marketing ideas

---

## Example 7: Real Use Case - Create a Summary

**What it does:** You have text, Mind summarizes it

```python
from mind.cognition import init_llm

mind = init_llm(model="phi")

# Your long text
long_text = """
The Industrial Revolution was a period of human history marked by the 
transition of human economies from agrarian and handicraft economies to 
industrial and machine-based manufacturing. It began in Britain in the 
late 1700s and spread throughout Europe and North America over the next 
century. The revolution was marked by rapid technological advancement, 
the development of factories, and significant social changes...
[imagine this is much longer]
"""

# Ask for a summary
prompt = f"""
Summarize this in just 2-3 sentences:

{long_text}
"""

summary = mind.generate(prompt)
print("Summary:")
print(summary)
```

**Result:** A short, clear summary

---

## Example 8: Practical for Work

**What it does:** You have messy data, Mind helps organize it

```python
from mind.cognition import init_llm

mind = init_llm(model="phi")

# Messy data
messy_data = """
john bought 3 apples for $2.50
sarah got 5 oranges costs: $4.75
Mike purchased 2 bananas $1.80
"""

# Ask Mind to organize it
prompt = f"""
Organize this shopping data in a clear table format:
Name | Item | Quantity | Price

Data:
{messy_data}
"""

organized = mind.generate(prompt)
print(organized)
```

**Result:** Neatly organized data

---

## Example 9: Quick Decision Help

**What it does:** You're unsure, Mind helps you decide

```python
from mind.cognition import init_llm

mind = init_llm(model="qwen")

# Your decision
question = """
I need to choose between:
Option A: Hire 1 person ($30k/year)
Option B: Use software ($200/month)

Which is better for a small business with $5k/month budget?
Give pros and cons for each.
"""

advice = mind.generate(question, n_predict=300)
print(advice)
```

**Result:** Clear comparison and recommendation

---

## Example 10: Project Planning

**What it does:** You have an idea, Mind helps plan it

```python
from mind.cognition import init_llm

mind = init_llm(model="qwen")

# Your project idea
project = "I want to create a newsletter about AI for business"

prompt = f"""
Help me plan this project:
{project}

Tell me:
1. What do I need to do first?
2. What tools should I use?
3. How long will it take?
4. What could go wrong?
5. How do I know if it's successful?
"""

plan = mind.generate(prompt, n_predict=400)
print(plan)
```

**Result:** A complete project plan

---

## How to Run These Examples

### Step 1: Open Terminal
```bash
cd ~/mind
source mind-env/bin/activate
```

### Step 2: Create a File
```bash
nano my_test.py
```

### Step 3: Copy One of the Examples Above

### Step 4: Run It
```bash
python my_test.py
```

### Step 5: Wait for Result
- Phi model: 2-5 seconds
- Qwen model: 10-20 seconds

---

## How to Choose Which Model to Use

### Use **Phi** (Fast) When:
- You need quick answers
- Simple questions
- Time matters
- You have limited CPU time

Example:
```python
mind = init_llm(model="phi")
```

### Use **Qwen** (Smart) When:
- Complex thinking needed
- Deep analysis
- Quality matters more than speed
- Creative tasks

Example:
```python
mind = init_llm(model="qwen")
```

---

## What NOT to Expect (Yet)

These don't work perfectly yet:

❌ Access external websites
❌ Download files from internet
❌ Connect to databases
❌ Update files automatically
❌ Make images/videos (coming later!)

But all of these are coming soon!

---

## Troubleshooting

### Problem: "Module not found"
**Solution:** Make sure you did:
```bash
source mind-env/bin/activate
```

### Problem: "Takes too long"
**Solution:** 
- Use Phi instead of Qwen
- Ask simpler questions
- Check if computer is busy

### Problem: "Answer is weird"
**Solution:**
- Try asking again (results vary)
- Be more specific in your request
- Use Qwen model instead of Phi

### Problem: "Nothing happens"
**Solution:**
- Check the computer isn't frozen
- Try the test first: `python test_llm_setup.py`
- Restart the terminal

---

## Real-World Workflow

### Morning
```python
# Check what happened overnight
mind.generate("Summarize sales from yesterday")

# Plan your day
mind.generate("What should I focus on today?")
```

### During Work
```python
# Analyze data quickly
task = mind.parse_task("Show me slow-selling products")

# Get a plan
plan = mind.create_plan("Improve slow product sales", agents)

# Quick research
mind.reasoning("What are industry best practices for product pricing?")
```

### End of Day
```python
# Create summary report
report = mind.generate("Create a daily summary of sales")

# Plan tomorrow
mind.generate("What should I prepare for tomorrow?")
```

---

## Cost Comparison (Real Numbers)

### Traditional Approach
- Hire analyst: $50/hour
- Analyst works on your request: 4 hours
- Cost: **$200 per analysis**
- Time to get result: **1-2 days**

### With Mind
- 1 minute of your time to describe it
- Mind analyzes: 30 seconds
- Cost: **$0**
- Time to get result: **30 seconds**

**Savings: $200 per analysis + instant results**

---

## Next Steps (What to Try)

1. **Tomorrow morning:**
   ```bash
   cd ~/mind && source mind-env/bin/activate
   python test_llm_setup.py  ← run this first
   ```

2. **This week:**
   - Try Example 1 (ask a question)
   - Try Example 4 (think through problem)
   - Try Example 5 (analyze data)

3. **Next week:**
   - Try Example 9 (decision help)
   - Try Example 10 (project planning)
   - Combine examples for your real work

4. **Going forward:**
   - Use Mind for your daily work
   - Tell us what works well
   - Ask for features you need

---

## The Bottom Line

**You have a smart AI team on your computer right now.**

**Use it for:**
- Getting answers quickly ✓
- Understanding problems ✓
- Planning projects ✓
- Analyzing data ✓
- Making decisions ✓
- Learning new things ✓

**Use these examples as a starting point, then adapt them for your own needs.**

Enjoy! 🚀
