# ENGR 102 Bridge Quick Glossary

What we mean by output, state, evidence, and checks.

Use this as a quick reference when a workbooklet or notebook asks you to explain what code showed, what Python stored, or what evidence supports your answer.

## The big distinction

Visible output is what you can see after running code. Stored state is what Python will remember and reuse through variable names. Engineers often need both: what appeared on screen and what the program actually stored for the next calculation.

## Terms

| Term | Meaning in this bridge course | Tiny example |
|---|---|---|
| Visible output | Anything the notebook, console, or output area shows after code runs. It may come from `print(...)` or from a final bare expression in a notebook cell. Visible output is useful evidence, but it is not automatically stored. | `speed + 0.2` may display `5.2` without changing `speed`. |
| Console / output area | The part of the coding environment where results, printed lines, errors, or displayed notebook values appear. In this course, when we say “what appears in the console,” we usually mean the visible output area for the code you ran. | A line from `print("ready")` appears there. |
| Printed output | Visible output created by `print(...)`. Printed output is useful for reporting or debugging, but printing a value does not store or update it. | `print(speed)` shows the current value of `speed`. |
| Notebook display | Visible output created when a bare expression is the last line of a notebook cell. It shows a value, but does not change stored state unless there is also an assignment. | Last line `speed + 0.2` displays a value. |
| Stored state | The current values Python has stored in variable names. This is what later code can reuse. | After `speed = 5.0`, `speed` stores `5.0`. |
| Assignment | Code using `=` to store or update a value in a variable name. | `speed = adjusted_speed` updates `speed`. |
| Expression | Code that produces a value. An expression can display or be used inside an assignment, but by itself it may not update state. | `distance / time` produces a speed. |
| Overwrite / update | Assigning a new value to a name that already had a value. The old value is no longer the current stored value for that name. | `flow_lpm = planned_flow_lpm`. |
| Candidate / planned value | A value being considered before it becomes the official current stored value. | `planned_flow_lpm = 17.7`. |
| Current value | The value currently stored in the name the team is using as the record. | `flow_lpm` may stay `16.8` until approved. |
| State history / trace | The step-by-step record of how variable values changed as code cells ran. | After Cell 2, after Cell 3, after Cell 4. |
| Evidence checkpoint | A place where you pause and record what you know: visible output, stored values, type, comparison result, or error message. | “After Cell 2, `speed` is still `5.0`.” |
| Type | The kind of value Python sees: `str`, `int`, `float`, or `bool`. | `"20.0"` is text; `20.0` is a float. |
| Cast / conversion | Turning a value into another type when it is safe to do so. | `float("20.0")` produces `20.0`. |
| Truthiness | Python's quick true/false interpretation of a value. It can be helpful but can also mislead. | `bool("no")` is `True` because the string is not empty. |
| Boundary check | A comparison at or near a limit. Exact-boundary cases are where `<` versus `<=` matters. | `19.6 >= 19.6` is `True`. |
| Boolean combination | Combining separate checks with `and`, `or`, or `not`. | `flow_ok and approval_ok`. |

## Optional evening pre-reading map

Use these as 10–15 minute supports, not as extra graded work.

| Bridge day | Think Python anchor | Video-search topic |
|---|---|---|
| Day 1 | Ch. 1, *Programming as a way of thinking*: <https://allendowney.github.io/ThinkPython/chap01.html> | Python print output vs expression output; Jupyter notebook output |
| Day 2 | Ch. 2, *Variables and Statements*: <https://allendowney.github.io/ThinkPython/chap02.html> | Python variables / expressions / assignment |
| Day 3 | Ch. 2 sections on values/types plus the glossary terms above | Python type casting / strings / booleans |
| Day 4 | Ch. 5, *Conditionals and Recursion*, comparison ideas: <https://allendowney.github.io/ThinkPython/chap05.html> | Python comparison operators |
| Day 5 | Ch. 5 Boolean/conditional ideas plus the glossary terms above | Python logical operators: `and`, `or`, `not` |

## A useful sentence frame

“The code **showed** ____ as visible output, but Python **stored** ____ in `____` after the assignment/checkpoint.”

## When you are unsure

Ask two questions:

1. Did I see it because Python displayed or printed it?
2. Which variable name, if any, now stores it for the next line of code?
