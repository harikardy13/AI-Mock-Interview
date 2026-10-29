import os
import json

from flask import Flask, render_template, request
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key) if api_key else None


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/start-interview", methods=["POST"])
def start_interview():
    if client is None:
        return "API key not found. Check your .env file.", 500

    role = request.form.get("role", "Software Developer")
    experience = request.form.get("experience", "Fresher")
    difficulty = request.form.get("difficulty", "Easy")

    prompt = f"""
    Generate exactly five interview questions for this candidate.

    Job role: {role}
    Experience level: {experience}
    Difficulty: {difficulty}

    Return a JSON object with a "questions" array containing
    exactly five relevant interview questions.
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an experienced technical interviewer. "
                        "Generate clear and relevant interview questions."
                    ),
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            response_format={"type": "json_object"},
        )

        result = json.loads(response.choices[0].message.content)
        questions = result.get("questions", [])

        if (
            not isinstance(questions, list)
            or len(questions) != 5
            or not all(
                isinstance(question, str) and question.strip()
                for question in questions
            )
        ):
            raise ValueError("Invalid question response from AI.")

        return render_template(
            "interview.html",
            questions=questions,
            role=role,
            experience=experience,
            difficulty=difficulty,
        )

    except Exception as e:
        app.logger.exception("Failed to generate interview questions.")
        return f"Error: {type(e).__name__}: {str(e)}", 502
    


if __name__ == "__main__":
    app.run(debug=True)