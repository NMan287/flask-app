document.addEventListener("DOMContentLoaded", async function() {
    const res = await fetch(`/questions/get/${testId}`);
    const data = await res.json();
    renderQuestions(data.questions);
    document.getElementById("submitBtn").style.display = "block";
});

function renderQuestions(questions) {
    const container = document.getElementById("questions");
    container.innerHTML = "";
    questions.forEach((q, i) => {
        container.innerHTML += `
            <div class="questionCard" id="card${i}">
                <p class="questionText"><b>Q${i+1}:</b> ${q.question_text}</p>
                <textarea id="answer${i}" placeholder="Type your answer here..."></textarea>
                <div id="feedback${i}" class="feedback" style="display:none;"></div>
            </div>
        `;
    });
    MathJax.typesetPromise();
}

async function submitAll() {
    const submitBtn = document.getElementById("submitBtn");
    submitBtn.disabled = true;
    submitBtn.innerText = "Marking...";

    const res = await fetch(`/questions/get/${testId}`);
    const data = await res.json();
    const dbQuestions = data.questions;

    const promises = dbQuestions.map(async (q, i) => {
        const userAnswer = document.getElementById(`answer${i}`).value.trim();

        if (!userAnswer) {
            showFeedback(i, "skipped", "No answer provided.", "");
            return;
        }

        const checkRes = await fetch("/questions/check", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                question_id: q.question_id,
                user_answer: userAnswer
            })
        });

        const result = await checkRes.json();
        showFeedback(i, result.result, result.feedback, result.correct_answer);
    });

    await Promise.all(promises);

    const scoreRes = await fetch(`/questions/results/${testId}`);
    const scoreData = await scoreRes.json();
    document.getElementById("score").innerText = `Score: ${scoreData.score}`;
    document.getElementById("score").style.display = "block";

    submitBtn.innerText = "Submitted";
}

function showFeedback(i, result, feedback, correctAnswer) {
    const el = document.getElementById(`feedback${i}`);
    const answer = document.getElementById(`answer${i}`);
    el.style.display = "block";

    if (result === "correct") {
        el.className = "feedback correct";
        el.innerHTML = ` ${feedback}`;
    } else if (result === "incorrect") {
        el.className = "feedback incorrect";
        el.innerHTML = `${feedback}<br><b>Correct answer:</b> ${correctAnswer}`;
    } else {
        el.className = "feedback skipped";
        el.innerHTML = ` ${feedback}`;
    }
}