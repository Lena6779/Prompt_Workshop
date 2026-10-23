import os
import textwrap  # wraps long lines so the side-by-side columns line up

# --- Mock responses for each task (vague, decent, well-engineered) ---
# Format: MOCK_ANSWERS[task number][quality level] -> response text
MOCK_ANSWERS = {
    1: {
        "vague": "Session state is a way to store information during a session. "
        "It is used in many web frameworks and can help with keeping "
        "track of data.",
        "decent": "In Streamlit, st.session_state lets you store values that stay "
        "the same while a user interacts with the app.",
        "good": "- st.session_state stores values between reruns of a Streamlit app.\n"
        "- Streamlit reruns the whole script after every interaction, so "
        "regular variables get reset.\n"
        "- Session state keeps things like counters, user input, and "
        "login status.\n\n"
        "Example:\n"
        'if "count" not in st.session_state:\n'
        "    st.session_state.count = 0\n"
        'if st.button("Click me"):\n'
        "    st.session_state.count += 1\n"
        "st.write(st.session_state.count)",
    },
    2: {
        "vague": "Here is a list of your tasks:\n"
        "1. API documentation\n"
        "2. Groceries\n"
        "3. Pytest suite",
        "decent": '{"tasks": ["API documentation", "Groceries", "Pytest suite"]}',
        "good": "[\n"
        '  {"title": "Finish the API documentation", "priority": "high", "status": "pending"},\n'
        '  {"title": "Buy groceries", "priority": "low", "status": "pending"},\n'
        '  {"title": "Finish the pytest suite", "priority": "medium", "status": "done"}\n'
        "]",
    },
    3: {
        "vague": "A PersistentClient is a type of database client. Databases store "
        "information so it can be used later. There are many kinds of "
        "databases, and each one handles storage differently.",
        "decent": "A PersistentClient in ChromaDB saves your data so it is not lost "
        "when the program ends.",
        "good": "A PersistentClient saves ChromaDB collections to disk, so the data "
        "is still available after the program stops.\n\n"
        "Source: week5_chromadb.md",
    },
}


# --- Mock response function (scoring from the Guided Example) ---
def mock_response(prompt, task):
    """Simulates how prompt quality affects response quality."""
    prompt_lower = prompt.lower()

    # Detect if the prompt has framing
    has_role = any(word in prompt_lower for word in ["you are", "act as", "your role"])
    # Detect if the prompt has constraints
    has_constraints = any(
        word in prompt_lower
        for word in [
            "under 100",
            "in 3 sentences",
            "as a table",
            "as json",
            "format",
            "bullet",
        ]
    )
    # Detect if the prompt has examples
    has_examples = "input:" in prompt_lower or "example:" in prompt_lower

    # True counts as 1 and False as 0, so the score is 0-3
    quality_score = sum([has_role, has_constraints, has_examples])

    if quality_score == 0:
        return "[MOCK — Vague prompt detected]\n" + MOCK_ANSWERS[task]["vague"]
    elif quality_score == 1:
        return "[MOCK — Decent prompt]\n" + MOCK_ANSWERS[task]["decent"]
    else:
        return "[MOCK — Well-engineered prompt]\n" + MOCK_ANSWERS[task]["good"]


def get_response(prompt, task, system_prompt=None):
    """Try real API, fall back to mock.
    Added system_prompt so Task 3 can send a system message."""
    api_key = os.environ.get("OPENAI_API_KEY")
    if api_key:
        import openai

        client = openai.OpenAI(api_key=api_key)
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        response = client.chat.completions.create(
            model="gpt-3.5-turbo", messages=messages, max_tokens=300
        )
        return response.choices[0].message.content
    else:
        # The mock only takes one string, so combine the system and user prompts
        full_prompt = (system_prompt + "\n" + prompt) if system_prompt else prompt
        return mock_response(full_prompt, task)


# --- Helper: show two responses side by side ---
def show_side_by_side(bad_text, good_text, width=50):
    """Print the bad and good responses in two columns."""
    bad_lines = []
    for line in bad_text.splitlines():
        # Wrap long lines; 'or [""]' keeps blank lines from disappearing
        bad_lines.extend(textwrap.wrap(line, width) or [""])
    good_lines = []
    for line in good_text.splitlines():
        good_lines.extend(textwrap.wrap(line, width) or [""])
    # Make both columns the same length
    total = max(len(bad_lines), len(good_lines))
    bad_lines += [""] * (total - len(bad_lines))
    good_lines += [""] * (total - len(good_lines))

    print(f"{'BAD PROMPT RESPONSE':<{width}} | GOOD PROMPT RESPONSE")
    print("-" * width + "-+-" + "-" * width)
    # Pair up lines from each column and pad the left side so the | lines up correctly
    for bad_line, good_line in zip(bad_lines, good_lines):
        print(f"{bad_line:<{width}} | {good_line}")
    print()


# --- Task 1: Code explanation ---
print("=" * 60)
print("TASK 1: Code Explanation (st.session_state)")
print("=" * 60)

bad_prompt_1 = "What is session_state?"

# Techniques: role + constraints/format
good_prompt_1 = (
    "You are a patient programming instructor teaching career changers "
    "who know Python but are new to Streamlit. "
    "Explain what st.session_state does in Streamlit and why it is needed, "
    "since Streamlit reruns the whole script on every interaction. "
    "Format your answer as 3 bullet points followed by a short code example "
    "of a button that counts clicks. Keep it under 100 words."
)

print(f"\nBad prompt: '{bad_prompt_1}'")
print(f"Good prompt: '{good_prompt_1[:80]}...'\n")
show_side_by_side(get_response(bad_prompt_1, 1), get_response(good_prompt_1, 1))


# --- Task 2: Data formatting ---
print("=" * 60)
print("TASK 2: Data Formatting (tasks to JSON)")
print("=" * 60)

task_list = (
    "Finish the API documentation today, it's urgent. "
    "Buy groceries sometime this week. "
    "I already finished the pytest suite."
)

bad_prompt_2 = f"Turn these into a list: {task_list}"

# Techniques: few-shot examples + constraints/format
# {{ }} prints a literal { } inside an f-string
good_prompt_2 = f"""Convert the tasks below into a JSON array. Return the output as JSON only.
Each object must have exactly these fields: "title", "priority" (high/medium/low), "status" (pending/done).

Input: "Pay the electric bill tomorrow, very important. I already walked the dog."
Output: [{{"title": "Pay the electric bill", "priority": "high", "status": "pending"}}, {{"title": "Walk the dog", "priority": "low", "status": "done"}}]

Input: "{task_list}"
Output:"""

print(f"\nBad prompt: '{bad_prompt_2[:80]}...'")
print(f"Good prompt:\n{good_prompt_2}\n")
show_side_by_side(get_response(bad_prompt_2, 2), get_response(good_prompt_2, 2))


# --- Task 3: System prompt design ---
print("=" * 60)
print("TASK 3: System Prompt Design (Course Study Assistant)")
print("=" * 60)

bad_system_prompt = "Answer questions about the course."

# Techniques: role + constraints/format + example
# Covers all 4 requirements: context only, admit when unsure,
# under 150 words, include the source document
good_system_prompt = """You are a Course Study Assistant for students in an AI engineering course.
Follow these rules:
1. Answer using ONLY the provided context from the course notes. Do not use outside knowledge.
2. If the context does not contain the answer, say "I don't know based on the course notes."
3. Keep every answer under 150 words.
4. Format: end every answer with "Source: <document name>".

Example:
Context: [streamlit_basics.md] st.columns() splits the page into side-by-side columns.
Question: How do I put things side by side in Streamlit?
Answer: Use st.columns() to split the page into columns, then place widgets in each one.
Source: streamlit_basics.md"""

# Same question for both, so the only difference is the system prompt
user_question = """Context:
[week5_chromadb.md] A PersistentClient stores collections on disk, so data survives after the program stops.
[week4_streamlit.md] st.session_state keeps values between reruns.

Question: What does a PersistentClient do in ChromaDB?"""

print(f"\nBad system prompt: '{bad_system_prompt}'")
print(f"Good system prompt:\n{good_system_prompt}\n")
print(f"User question (same for both):\n{user_question}\n")
show_side_by_side(
    get_response(user_question, 3, system_prompt=bad_system_prompt),
    get_response(user_question, 3, system_prompt=good_system_prompt),
)

print("=" * 60)
print("KEY TAKEAWAY: Same task, dramatically different results.")
print("The prompt IS the product.")
print("=" * 60)
