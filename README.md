Prompt Workshop

A Python script that compares vague prompts with well-engineered prompts across three tasks and shows the responses side by side in the terminal.

Prompt Engineering Techniques

Each "good" prompt uses at least two of these three techniques:

Technique	What it does
Role / framing	Tells the model who it is and who it's talking to
Few-shot examples	Shows the model an example of the answer you want
Constraints / format	Sets the length, structure, or output format

The Three Tasks

Task	Goal	Techniques in the good prompt
1. Code explanation	Explain what st.session_state does in Streamlit	Role + format
2. Data formatting	Turn a plain-English task list into a JSON array with title, priority, and status	Few-shot + format
3. System prompt design	A "Course Study Assistant" that uses only the provided context, admits when it doesn't know, stays under 150 words, and cites its source document	Role + format + example

How It Works

get_response() calls the OpenAI API if an OPENAI_API_KEY is set. If not, it uses a mock function.
mock_response() gives the prompt one point for each technique it finds (score 0–3) and returns a vague, decent, or well-engineered answer for that task.
show_side_by_side() prints the bad and good responses in two columns.

How to Run

No packages are needed to run with the mock:

python prompt_workshop.py

To use the real OpenAI API instead:

python -m pip install -r requirements.txt
$env:OPENAI_API_KEY="your-key-here"
python prompt_workshop.py

(The $env: line is for PowerShell. On Mac/Linux, use export OPENAI_API_KEY="your-key-here".)

Example Output:

BAD PROMPT RESPONSE                                | GOOD PROMPT RESPONSE
---------------------------------------------------+---------------------------------------------------
[MOCK — Vague prompt detected]                     | [MOCK — Well-engineered prompt]
Here is a list of your tasks:                      | [
1. API documentation                               |   {"title": "Finish the API documentation",
2. Groceries                                       | "priority": "high", "status": "pending"},
3. Pytest suite                                    |   {"title": "Buy groceries", "priority": "low",

Key Takeaway

Same task, dramatically different results. The prompt IS the product.