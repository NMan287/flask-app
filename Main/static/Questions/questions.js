console.log("JS LOADED");
async function generateTest() {

    async function generateTest() {
    console.log("CLICKED");

    const res = await fetch("/questions/create", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ subject: "Maths", topic: "Algebra", exam_board: "AQA", q_num: 5 })
    });

    console.log("Response:", res.status);
}

    const subject = document.getElementById("subjectList").value;
    const topic = document.getElementById("topic").value;
    const examBoard = document.getElementById("board").value;
    const qNum = document.getElementById("qNum").value;

    document.getElementById("generateBtn").disabled = true;
    document.getElementById("generateBtn").innerText = "Generating...";
    console.log("Fetching:", "/questions/create");
    const res = await fetch("/questions/create", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ subject, topic, exam_board: examBoard, q_num: qNum })
    });

    console.log("Response status:", res.status);

    if (!res.ok) {
        const text = await res.text();
        console.error("Server error:", text);
        document.getElementById("generateBtn").innerText = "Generate";
        document.getElementById("generateBtn").disabled = false;
        return;
    }

    const data = await res.json();
    console.log("DATA:", data);

    if (!data.test_id) {
    console.error("No test_id returned:", data);

    alert("Error creating test: " + (data.error || "Unknown error"));
    
    document.getElementById("generateBtn").innerText = "Generate";
    document.getElementById("generateBtn").disabled = false;
    return;
}

window.location.href = `/questions/test/${data.test_id}`;

document.getElementById("generateBtn").addEventListener("click", async function (e) {
    e.preventDefault(); //

    console.log("CLICKED");

    const subject = document.getElementById("subjectList").value;
    const topic = document.getElementById("topic").value;
    const examBoard = document.getElementById("board").value;
    const qNum = document.getElementById("qNum").value;

    console.log("Fetching:", "/questions/create");

    const res = await fetch("/questions/create", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ subject, topic, exam_board: examBoard, q_num: qNum })
    });

    console.log("Response status:", res.status);
});}