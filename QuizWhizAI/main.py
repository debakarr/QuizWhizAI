import json

import openai
import streamlit as st
from get_quiz import get_quiz_from_topic

# Input box to enter the topic of the quiz
topic = st.sidebar.text_input(
    "To change topic just enter in below. From next new quiz question the topic entered here will be used.",
    value="devops",
)

api_key = st.sidebar.text_input("OpenAI API key", type="password").strip()

# Initialize session state variables if they don't exist yet
if "current_question" not in st.session_state:
    st.session_state.answers = {}
    st.session_state.current_question = 0
    st.session_state.questions = []
    st.session_state.right_answers = 0
    st.session_state.wrong_answers = 0


# Define a function to display the current question and options
def display_question():
    # Handle first case
    if len(st.session_state.questions) == 0:
        try:
            first_question = get_quiz_from_topic(topic, api_key)
        except openai.error.AuthenticationError:
            st.error(
                "Please enter a valid OpenAI API key in the left sidebar to proceed. "
                "To know how to obtain the key checkout readme for this project here: https://github.com/Dibakarroy1997/QuizWhizAI/blob/main/README.md"
            )
            return
        st.session_state.questions.append(first_question)

    # Disable the submit button if the user has already answered this question
    submit_button_disabled = st.session_state.current_question in st.session_state.answers

    # Get the current question from the questions list
    question = st.session_state.questions[st.session_state.current_question]

    # Display the question prompt
    st.write(f"{st.session_state.current_question + 1}. {question['question']}")

    # Use an empty placeholder to display the radio button options
    options = st.empty()

    # Display the radio button options and wait for the user to select an answer
    user_answer = options.radio("Your answer:", question["options"], key=st.session_state.current_question)

    # Display the submit button and disable it if necessary
    submit_button = st.button("Submit", disabled=submit_button_disabled)

    # If the user has already answered this question, display their previous answer
    if st.session_state.current_question in st.session_state.answers:
        index = st.session_state.answers[st.session_state.current_question]
        options.radio(
            "Your answer:",
            question["options"],
            key=float(st.session_state.current_question),
            index=index,
        )

    # If the user clicks the submit button, check their answer and show the explanation
    if submit_button:
        # Record the user's answer in the session state
        st.session_state.answers[st.session_state.current_question] = question["options"].index(user_answer)

        # Check if the user's answer is correct and update the score
        if user_answer == question["answer"]:
            st.write("Correct!")
            st.session_state.right_answers += 1
        else:
            st.write(f"Sorry, the correct answer was {question['answer']}.")
            st.session_state.wrong_answers += 1

        # Show an expander with the explanation of the correct answer
        with st.expander("Explanation"):
            st.write(question["explanation"])

    # Display the current score
    st.write(f"Right answers: {st.session_state.right_answers}")
    st.write(f"Wrong answers: {st.session_state.wrong_answers}")


# Define a function to go to the next question
def next_question():
    # Move to the next question in the questions list
    st.session_state.current_question += 1

    # If we've reached the end of the questions list, get a new question
    if st.session_state.current_question > len(st.session_state.questions) - 1:
        try:
            next_question = get_quiz_from_topic(topic, api_key)
        except openai.error.AuthenticationError:
            st.session_state.current_question -= 1
            return
        st.session_state.questions.append(next_question)


# Define a function to go to the previous question
def prev_question():
    # Move to the previous question in the questions list
    if st.session_state.current_question > 0:
        st.session_state.current_question -= 1
        st.session_state.explanation = None


# Create a 3-column layout for the Prev/Next buttons and the question display
col1, col2, col3 = st.columns([1, 6, 1])

# Add a Prev button to the left column that goes to the previous question
with col1:
    if col1.button("Prev"):
        prev_question()

# Add a Next button to the right column that goes to the next question
with col3:
    if col3.button("Next"):
        next_question()

# Display the actual quiz question
with col2:
    display_question()

# Add download buttons to sidebar which download current questions
download_button = st.sidebar.download_button(
    "Download Quiz Data",
    data=json.dumps(st.session_state.questions, indent=4),
    file_name="quiz_session.json",
    mime="application/json",
)
