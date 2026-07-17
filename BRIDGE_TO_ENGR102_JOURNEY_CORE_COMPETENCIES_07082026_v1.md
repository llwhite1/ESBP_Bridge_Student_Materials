# Your Bridge-to-ENGR 102 Journey

Version: 07082026 v1 draft for student-facing review
Course: ENGR 102 Summer Bridge Python Seminar

## Why this bridge exists

This bridge is not trying to make you memorize every Python feature before the semester begins. The bigger goal is to help you enter ENGR 102 with the habits that make engineering computation feel manageable:

- keep track of what the code actually stores;
- separate visible output from program state;
- test decisions with evidence, not guesses;
- trace repeated processes carefully;
- explain your reasoning in a way another engineer can inspect.

In the regular ENGR 102 semester, you will keep seeing new tools and larger problems. The bridge gives you a smaller, guided version of the same journey: read the situation, identify the evidence, write or inspect Python, test what happened, and explain what your result supports.

---

## The story arc

### 1. Evidence first: what did the code actually show?

Bridge days: Day 1

Core question:

> What can I prove from what I see?

You begin with visible output because output is the easiest kind of evidence to inspect. But visible output is not the same thing as memory. A printed value can show a displayed candidate, but that does not mean the program stored it as the current value.

ENGR 102 competency this supports:

- Trace visible output carefully.
- Explain what a program proves and what it does not prove.
- Use code evidence instead of guessing from intention.

Semester success move:

When a problem asks “what prints?” or “what does this code show?”, do not jump to what the code was supposed to do. Read the actual statements in order and write down the evidence.

---

### 2. State and assignment: what is stored right now?

Bridge days: Day 2

Core question:

> What value does this name currently hold, and what assignment changed it?

Variables help Python remember values, but a variable is not a formula that keeps updating automatically. A name holds its current recorded value after the most recent assignment. If another value is only displayed or stored in a different name, it is not the current value for the record-holding name.

ENGR 102 competency this supports:

- Collect, store, and manipulate data with variables and expressions.
- Trace program state.
- Explain the difference between displayed evidence, a stored candidate value, and the current recorded value.

Semester success move:

When code uses variables, build a small state table. Each time assignment happens, update the value. Do not rewrite history unless the code assigns a new value.

---

### 3. Type-aware calculation: what kind of value am I using?

Bridge days: Day 3

Core question:

> Before I trust this value, what type of value is it?

The same visible characters can behave differently depending on type. `"80"` and `80` do not always mean the same thing to Python. ENGR 102 problems often require you to read input, convert values, calculate with them, and explain the result.

ENGR 102 competency this supports:

- Use variables, expressions, and type-aware calculations.
- Interpret input and output correctly.
- Avoid treating all displayed values as ready-to-calculate numbers.

Semester success move:

Before doing math, ask: is this value already numeric, or is it text that must be converted? Before making a decision, ask: is the comparison using the kind of value I think it is using?

---

### 4. Decisions and boundaries: which branch should the code select?

Bridge days: Days 4–8

Core question:

> What condition selects the branch, and what evidence supports that decision?

Engineering decisions often depend on thresholds: safe/unsafe, pass/fail, ready/hold, within/outside a boundary. Python uses comparisons, Boolean logic, and conditionals to make these decisions explicit.

ENGR 102 competency this supports:

- Use comparisons, Boolean logic, boundary cases, and test cases.
- Use conditionals to implement simple decision procedures.
- Debug expected-versus-actual behavior when the code takes the incorrect branch.

Semester success move:

For each decision, name the condition, test the boundary case, and write down the branch the code should select. If the actual branch is different, do not just change code randomly; compare expected evidence to actual evidence.

---

### 5. Repeated processes: how does the state change over time?

Bridge days: Days 10–14

Core question:

> What repeats, what changes each time, and when does the process stop?

Loops are where many students lose track of state. A loop is not just “doing something many times.” It is a repeated process with changing evidence: counters, accumulators, branch decisions, stopping conditions, and sometimes skipped or early-ended steps.

ENGR 102 competency this supports:

- Use loops in computer programs.
- Trace loop state across repeated steps.
- Decompose a repeated process into update rules, stopping rules, and evidence checks.

Semester success move:

When you see a loop, do not try to hold everything in your head. Make a trace table. Track the loop variable, the changing state, and the condition that controls whether the loop continues.

---

### 6. Lists and indexed data: how do I work with a collection?

Bridge days: Days 15–16

Core question:

> Am I reading a value, changing a value, or using an index to locate a value?

Many ENGR 102 problems involve batches of data: measurements, readings, charges, scores, or test cases. Lists let Python store multiple values together. The key habit is to know whether you are reading an element, using an index, or changing a stored element.

ENGR 102 competency this supports:

- Collect, create, store, and manipulate data in larger structures such as lists.
- Use loops with lists.
- Explain list state before and after mutation.

Semester success move:

For list problems, separate three things: the list, the index, and the element value. If code changes the list, show the before-and-after state.

---

### 7. Synthesis: can I plan, trace, test, debug, explain, and ask for support?

Bridge days: Days 18–19

Core question:

> Can I use evidence to move from confusion to a defensible next step?

By the end of the bridge, the main target is not one isolated Python trick. The target is a full engineering-computation habit: plan the task, trace the code, test a boundary, debug a mismatch, explain what the evidence supports, and choose a support plan when you get stuck.

ENGR 102 competency this supports:

- Decompose a complicated task into manageable pieces.
- Use Python-readable evidence to reason about measurements, thresholds, and repeated processes.
- Communicate computational work through readable code, output, trace tables, tests, and written explanations.

Semester success move:

When a semester assignment feels large, do not start by asking “What is the whole answer?” Start with: What are the inputs? What are the outputs? What state changes? What conditions matter? What test would convince me the answer is working?

---

## The bridge competencies in one view

| Bridge habit | What it means | Where it appears in the bridge | Why it matters in ENGR 102 |
|---|---|---|---|
| Evidence before answer | Use visible output, traces, and tests to support claims | Day 1 and all later days | ENGR 102 expects you to justify what your code does, not only submit code |
| State tracking | Know what value each variable currently stores | Day 2 and all trace/debug work | Most programming errors come from losing track of updates |
| Type awareness | Know whether a value is text, number, Boolean, or list data | Day 3 and later calculations | Input, calculations, comparisons, and plots all depend on type |
| Boundary decisions | Test the exact edge between branch outcomes | Days 4–8 | Engineering decisions often depend on thresholds and constraints |
| Debugging with evidence | Compare expected behavior to actual behavior | Day 8 and all later repair work | Debugging is a normal engineering practice, not a sign of failure |
| Loop tracing | Track repeated updates over time | Days 10–14 | Semester problems often require repeated calculations or repeated checks |
| List reasoning | Read, index, and update collections of data | Days 15–16 | Engineering data usually arrives in batches, not one value at a time |
| Decomposition | Break a large task into smaller inspectable steps | Days 18–19 | Larger assignments require planning, not one-step guessing |
| Communication and support | Explain evidence and choose a next support plan | Every day, especially Days 18–19 | ENGR 102 success includes explaining, documenting, and asking productive questions |

---

## What successful bridge work looks like

A strong bridge student does not always get the answer instantly. A strong bridge student can slow down and produce evidence.

By the end of the bridge, you should be able to say:

- I can tell the difference between what Python displayed and what Python stored.
- I can update a state table when assignment changes a value.
- I can check type before trusting a calculation.
- I can identify a decision condition and test the boundary case.
- I can trace a loop without trying to remember every step in my head.
- I can explain how a list changes when code mutates it.
- I can use expected-versus-actual evidence to debug.
- I can write a short explanation of what my code proves.
- I can choose a support plan when I know what evidence I am missing.

That is the bridge-to-ENGR 102 journey: from “I hope this code works” to “I can show what this code does, why it does it, and what evidence I need next.”
