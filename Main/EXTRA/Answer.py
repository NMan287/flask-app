from flask import request, jsonify, render_template, Blueprint, session, redirect, url_for
import g4f
from EXTRA.tables import db, question_asked
import pytesseract
from PIL import Image

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe' # path to the tesseract program

answer_bp = Blueprint('answer', __name__)

ai_personality = {
    'brief': (
        "You are to answer questions and explain them breifly max 4 sentences "
        "Do not use images when explaining even when asked to "
        "Replace the equation and range with the correct values. Use * for multiplication. "
        "Display line by line an explanation and only explain the answer "
        "Do not ask the user any questions or add notes at the end of the explanation"  # briefly explain the answer in as little sentences
    ),
    'detailed': (
        "You are to answer questions and explain in as much detail as possible "
        "Be as detailed as possible but make it understandable for the user to read "
        "Do not use images when explaining even when asked to "
        "Replace the equation and range with the correct values. Use * for multiplication. "
        "Do not ask the user any questions or add notes at the end of the explanation" # explain the answer in as much detail

    ),
    'diagram': (
        "You are to answer questions and explain them both with detail and visually"
        "Try to use images in every question given for clarity and understanding the question"
        "Replace the equation and range with the correct values. Use * for multiplication. "
        "For all non-graph questions: use ASCII diagrams, markdown tables, and LaTeX. "
        "Do not ask the user any questions or add notes at the end of the explanation" # visually explain the answer in as much detail
    ),
}


@answer_bp.route('/settings/personality', methods=['POST'])
def save_personality():
    personality = request.form.get('personality')  # gets option picked from settings
    if personality in ('brief', 'detailed', 'diagram'):
        session['ai_personality'] = personality
    return redirect(url_for('forum.settings_page'))


@answer_bp.route("/addUserQ", methods=["POST"])
def send_question():
    print("Getting Question") # for debugging
    data = request.get_json()
    print("Data Received:", data)
    return jsonify({"message": "Question added successfully"}) # recieves question into backend


@answer_bp.route("/answer")
def answer():
    return render_template("ai_solver/Answer.html")


def save_question(user_id, question, response):
    try:
        question_entry = question_asked(user_id=user_id,
                                        quest_text=question,
                                        ai_answer=response,
                                        quest_image=None)
        db.session.add(question_entry) # add to database
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print("db error:", e)


@answer_bp.route("/ask", methods=["POST"])
def ask():
    data = request.get_json()
    question = data.get("question", "")
    user_id = session.get("user_id")
    personality = session.get('ai_personality', 'detailed')
    system_prompt = ai_personality[personality]

    #send question to ai
    try:
        response = g4f.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": question} # sets ai model to answer the question based of option in settings
            ]
        )

    except Exception as e:
        print(e)
        return jsonify({"answer": "Error: " + str(e)})
    
    save_question(user_id, question, response)
    return jsonify({"answer": response})

