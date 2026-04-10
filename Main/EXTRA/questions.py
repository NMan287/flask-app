from flask import Blueprint, request, jsonify, render_template, session
from EXTRA.tables import db, test, test_question
import g4f
import json
import re

questions_bp = Blueprint('questions', __name__)

@questions_bp.route("/")
def questions_page():
    return render_template("Questions/questions.html")

@questions_bp.route("/test/<int:test_id>")
def test_page(test_id):
    return render_template("Questions/QuestionsTest.html", test_id=test_id)

@questions_bp.route("/create", methods=["POST"])
def create_test():
    data = request.get_json()
    user_id = session.get("user_id")
    subject = data.get("subject")
    topic = data.get("topic")
    exam_board = data.get("exam_board")
    q_num = data.get("q_num", 5) # gets the information from the inputs
    try:
        response = g4f.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "user", "content":
                    f"Generate {q_num} {exam_board} {subject} exam questions on the topic: {topic}. "
                    f"Reply with ONLY a numbered list. Each question on its own line starting with '1.', '2.', etc. "
                    f"No headers, no markdown, no extra text before or after the list."
                } # tells ai model to generate questions based on information given
            ]
        )
        if not isinstance(response, str):
            response = "".join(response)

        if not response or response.strip() == "":
            return jsonify({"error": "AI returned empty response"}), 500

        # split response into individual lines
        lines = response.strip().split('\n')
        questions_list = []

        for i, line in enumerate(lines):  # adds a counter as the key
            stripped = line.strip()
            if not stripped:
                continue

            # allows format to be: 1. question"
            if re.match(r'^\d+[\.\)]', stripped):
                cleaned = re.sub(r'^\d+[\.\)]\s*', '', stripped)
                cleaned = re.sub(r'\*+', '', cleaned).strip()
                if cleaned and len(cleaned) > 5:
                    questions_list.append(cleaned)

            # makes sure question not presented in other ways
            elif re.match(r'^[#*]*\s*Question\s*\d+', stripped, re.IGNORECASE):
                fragment = ""
                for next_line in lines[i + 1:]:
                    next_line = next_line.strip()
                    if not next_line or next_line == '---':
                        if fragment:
                            break
                        continue
                    if re.match(r'^[#*]*\s*Question\s*\d+', next_line, re.IGNORECASE):
                        break
                    if any(phrase in next_line.lower() for phrase in ["if you want", "do you want", "let me know"]):
                        break
                    next_line = re.sub(r'\*+', '', next_line).strip()
                    fragment += " " + next_line
                cleaned = fragment.strip()
                if cleaned and len(cleaned) > 5:
                    questions_list.append(cleaned)

        if not questions_list:
            return jsonify({"error": "Could not extract questions from ai response"})

        # trim to requested number of questions
        questions_list = questions_list[:int(q_num)]

        new_test = test(
            user_id=user_id,
            q_num=q_num,
            topic=topic,
            subject=subject,
            exam_board=exam_board
        )
        db.session.add(new_test)
        db.session.flush()

        # adds each question to database
        for q_text in questions_list:
            new_q = test_question(
                user_id=user_id,
                test_id=new_test.test_id,
                topic=topic,
                subject=subject,
                question_text=q_text,
                user_answer=None,
                ai_answer=None,
                is_correct=None
            )
            db.session.add(new_q)

        db.session.commit()
        return jsonify({"test_id": new_test.test_id, "questions": questions_list})

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)})


@questions_bp.route("/get/<int:test_id>")
def get_questions(test_id):
    questions = test_question.query.filter_by(test_id=test_id).all()

    question_list = []
    for q in questions:
        question_list.append({
            "question_id": q.question_id,
            "question_text": q.question_text,
            "user_answer": q.user_answer,
            "ai_answer": q.ai_answer,
            "is_correct": q.is_correct
        })
    return jsonify({"questions": question_list})


@questions_bp.route("/check", methods=["POST"])
def check_answer():
    data = request.get_json()
    question_id = data.get("question_id")
    user_answer = data.get("user_answer")

    q = db.session.get(test_question, question_id)
    if not q:
        return jsonify({"error": "Question not found"})

    try:
        response = g4f.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "user", "content":
                    f"You are a teacher marking a student's answer. "
                    f"Question: {q.question_text}\n"
                    f"Student's answer: {user_answer}\n\n"
                    f"Reply ONLY with a JSON object in this exact format, no extra text: "
                    f"{{\"result\": \"correct\", \"feedback\": \"Well done! ...\", \"correct_answer\": \"...\"}} "
                    f"or {{\"result\": \"incorrect\", \"feedback\": \"Not quite...\", \"correct_answer\": \"...\"}} "
                    f"Be encouraging. Always include the full correct working in correct_answer."
                }
            ]
        )

        if not isinstance(response, str):
            response = "".join(response)


        if not response or response.strip() == "":
            return jsonify({
                "result": "error",
                "feedback": "AI returned no response. Please try again.",
                "correct_answer": ""
            })

        clean = response.strip()
        # strip markdown code fences if ai wrapped response in them
        if clean.startswith("```"):
            clean = clean.split("```")[1]
            if clean.startswith("json"):
                clean = clean[4:]
            clean = clean.strip()

        try:
            parsed = json.loads(clean)
        except json.JSONDecodeError: # falls back if error occurs
            is_correct = any(word in clean.lower() for word in ["correct", "well done", "great", "right"])
            parsed = {
                "result": "correct" if is_correct else "incorrect",
                "feedback": clean[:500],
                "correct_answer": ""
            }

        q.user_answer = user_answer
        q.ai_answer = parsed.get("correct_answer")
        q.is_correct = parsed.get("result") == "correct"
        db.session.commit()

        return jsonify(parsed)

    except Exception as e:
        db.session.rollback()
        return jsonify({
            "result": "error",
            "feedback": "Could not mark answer: " + str(e),
            "correct_answer": ""
        })


@questions_bp.route("/results/<int:test_id>")
def get_results(test_id):
    questions = test_question.query.filter_by(test_id=test_id).all()
    total = len(questions)
    correct = sum(1 for q in questions if q.is_correct)

    question_list = []
    for q in questions:
        question_list.append({
            "question_text": q.question_text,
            "user_answer": q.user_answer,
            "ai_answer": q.ai_answer,
            "is_correct": q.is_correct
        })

    return jsonify({
        "total": total,
        "correct": correct,
        "score": f"{correct}/{total}",
        "questions": question_list
    })

@questions_bp.route("/my-questions")
def my_questions_page():
    return render_template("Questions/myQuestions.html")

@questions_bp.route("/history")
def get_history():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "Not logged in"}), 401

    tests = test.query.filter_by(user_id=user_id).all()
    result = []

    for t in tests:
        questions = test_question.query.filter_by(test_id=t.test_id).all()

        # calculate score for this test
        answered = [q for q in questions if q.is_correct is not None]
        correct = sum(1 for q in answered if q.is_correct)
        total = len(answered)

        # get improvement suggestion if user got any wrong
        wrong = [q for q in answered if not q.is_correct]
        improvement = get_improvement(t.subject, wrong) if wrong else ""

        result.append({
            "test_id": t.test_id,
            "subject": t.subject,
            "topic": t.topic,
            "exam_board": t.exam_board,
            "score": f"{correct}/{total}" if total > 0 else "Not attempted",
            "correct": correct,
            "total": total,
            "improvement": improvement
        })

    return jsonify({"tests": result})

def get_improvement(subject, question_wrong):
    wrong_texts = "\n".join([f"- {q.question_text}" for q in question_wrong])
    try:
        response = g4f.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "user", "content":
                    f"A student got these {subject} questions wrong:\n{wrong_texts}\n"
                    f"In 1-2 sentences, what specific areas should they focus on to improve? "
                    f"Reply with plain text only, no markdown, no bullet points."
                }
            ]
        )
        if not isinstance(response, str):
            response = "".join(response)
        return response.strip()[:300] if response else "Review the questions you got wrong and practice similar problems."
    except Exception as e:
        print("AI error:", e)
        return "Review the questions you got wrong and practice similar problems."