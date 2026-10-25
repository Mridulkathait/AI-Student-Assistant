
import re
import random
import streamlit as st
from collections import Counter

st.set_page_config(
    page_title="AI Student Assistant",
    page_icon="📚",
    layout="wide"
)

# ---------- Text Processing ----------

STOP_WORDS = {
    "the", "is", "are", "a", "an", "and", "or", "of", "to",
    "in", "on", "for", "with", "by", "as", "it", "this",
    "that", "was", "were", "be", "from", "at", "which",
    "we", "they", "their", "can", "has", "have", "its"
}


def split_sentences(text):
    return [
        s.strip() for s in re.split(r"(?<=[.!?])\s+", text)
        if len(s.strip().split()) >= 4
    ]


def summarise(text, number=3):
    sentences = split_sentences(text)

    if not sentences:
        return "Please enter a few complete sentences."

    words = re.findall(r"\b[a-zA-Z]+\b", text.lower())
    words = [w for w in words if w not in STOP_WORDS]
    frequencies = Counter(words)

    scored = []
    for index, sentence in enumerate(sentences):
        sentence_words = re.findall(r"\b[a-zA-Z]+\b", sentence.lower())
        score = sum(
            frequencies[w] for w in sentence_words
            if w not in STOP_WORDS
        )
        scored.append((score, index, sentence))

    selected = sorted(
        sorted(scored, reverse=True)[:min(number, len(scored))],
        key=lambda item: item[1]
    )

    return " ".join(item[2] for item in selected)


def generate_quiz(text, number=5):
    sentences = split_sentences(text)
    questions = []

    for sentence in sentences:
        words = re.findall(r"\b[A-Za-z]{5,}\b", sentence)
        candidates = [w for w in words if w.lower() not in STOP_WORDS]

        if candidates:
            answer = max(candidates, key=len)
            question = re.sub(
                r"\b" + re.escape(answer) + r"\b",
                "________",
                sentence,
                count=1,
                flags=re.IGNORECASE
            )
            questions.append((question, answer))

    random.shuffle(questions)
    return questions[:number]


# ---------- User Interface ----------

st.title("📚 AI Student Assistant")
st.write(
    "A Python-based study tool for summarising notes, "
    "creating practice quizzes and finding relevant information."
)

st.info(
    "This prototype uses extractive summarisation and "
    "keyword matching. It does not yet use a trained AI model."
)

with st.sidebar:
    st.header("About the Project")
    st.write("**Language:** Python")
    st.write("**Interface:** Streamlit")
    st.write("**Method:** Basic NLP and text processing")
    st.write("**Purpose:** Support student learning")

tab1, tab2, tab3 = st.tabs([
    "📝 Summariser",
    "🧠 Quiz Generator",
    "🔎 Ask Your Notes"
])

with tab1:
    st.subheader("Summarise Your Notes")
    notes = st.text_area(
        "Paste your study notes here",
        height=220,
        key="summary_notes",
        placeholder="Paste a paragraph about your subject..."
    )
    sentence_count = st.slider(
        "Approximate number of summary sentences",
        1, 8, 3
    )

    if st.button("Generate Summary"):
        if notes.strip():
            st.write(summarise(notes, sentence_count))
        else:
            st.warning("Please enter your notes first.")

with tab2:
    st.subheader("Create a Practice Quiz")
    quiz_notes = st.text_area(
        "Paste notes for the quiz",
        height=180,
        key="quiz_notes"
    )
    quiz_count = st.slider("Number of questions", 1, 10, 5)

    if st.button("Generate Quiz"):
        if quiz_notes.strip():
            questions = generate_quiz(quiz_notes, quiz_count)

            if not questions:
                st.warning(
                    "Enter a few complete sentences with "
                    "descriptive words."
                )
            else:
                st.session_state.quiz = questions
                st.session_state.quiz_answers = {}

    if "quiz" in st.session_state:
        for i, (question, answer) in enumerate(
            st.session_state.quiz
        ):
            st.markdown(f"**Q{i + 1}. {question}**")
            st.session_state.quiz_answers[i] = st.text_input(
                "Your answer",
                key=f"answer_{i}"
            )

        if st.button("Check Answers"):
            score = 0
            for i, (_, correct) in enumerate(
                st.session_state.quiz
            ):
                user_answer = st.session_state.quiz_answers.get(
                    i, ""
                ).strip()
                if user_answer.lower() == correct.lower():
                    score += 1
                st.write(
                    f"Q{i + 1}: Correct answer — **{correct}**"
                )

            st.success(
                f"Your score: {score}/{len(st.session_state.quiz)}"
            )

with tab3:
    st.subheader("Search Your Study Notes")
    search_notes = st.text_area(
        "Paste notes to search",
        height=150,
        key="search_notes"
    )
    question = st.text_input(
        "Enter a question or keyword",
        placeholder="What is machine learning?"
    )

    if st.button("Find Relevant Information"):
        if search_notes.strip() and question.strip():
            query_words = {
                w.lower() for w in re.findall(
                    r"\b[a-zA-Z]+\b", question
                ) if w.lower() not in STOP_WORDS
            }

            matches = []
            for sentence in split_sentences(search_notes):
                sentence_words = {
                    w.lower() for w in re.findall(
                        r"\b[a-zA-Z]+\b", sentence
                    )
                }
                overlap = query_words & sentence_words
                if overlap:
                    matches.append((len(overlap), sentence))

            matches.sort(key=lambda item: item[0], reverse=True)

            if matches:
                st.write("**Relevant passages from your notes:**")
                for _, sentence in matches[:3]:
                    st.write("• " + sentence)
            else:
                st.warning(
                    "No matching passage found. Try different "
                    "keywords or add more relevant notes."
                )
        else:
            st.warning("Enter both notes and a question.")

st.divider()
st.caption(
    "Student project prototype | Outputs should be checked "
    "against the original study material."
)
