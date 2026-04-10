function renderAnswer(text) {
    // Extract LaTeX blocks and replace with placeholders
    const latexBlocks = [];
    
    // Protect display math \[...\]
    text = text.replace(/\\\[[\s\S]*?\\\]/g, match => {
        latexBlocks.push(match);
        return `%%LATEX${latexBlocks.length - 1}%%`;
    });
    
    // Protect inline math \(...\)
    text = text.replace(/\\\([\s\S]*?\\\)/g, match => {
        latexBlocks.push(match);
        return `%%LATEX${latexBlocks.length - 1}%%`;
    });

    // Now run marked
    let html = marked.parse(text);

    // Restore LaTeX blocks
    latexBlocks.forEach((latex, i) => {
        html = html.replace(`%%LATEX${i}%%`, latex);
    });

    return html;
}

async function send_question(question) {
    var res = await fetch("/ask", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question })
    });

    var data = await res.json();
    const answer = data.answer;

    const graphMatch = answer.match(/<<GRAPH>>(.*?)<<GRAPH>>/s);
    if (graphMatch) {
        try {
            const jsonString = graphMatch[1].replace(/'/g, '"');
            const graphData = JSON.parse(jsonString);
            document.getElementById("aiChat").innerHTML += `
                <p><b>You:</b> ${question}</p>
                <p><b>Bot:</b> Here is the graph:</p>
            `;
            plotGraph(graphData.equation, graphData.xMin, graphData.xMax);
        } catch (e) {
            console.error("Graph parse error:", e);
        }
    } else {
        document.getElementById("aiChat").innerHTML += `
            <p><b>You:</b> ${question}</p>
            <div><b>Bot:</b> ${renderAnswer(answer)}</div>
        `;
        MathJax.typesetPromise();
    }
}
function plotGraph(equation, xMin, xMax) {
    const canvas = document.getElementById("graphCanvas");
    canvas.style.display = "block";

    const labels = [];
    const dataPoints = [];

    for (let x = xMin; x <= xMax; x += 0.1) {
        const xRounded = Math.round(x * 10) / 10;
        labels.push(xRounded);
        try {
            const y = math.evaluate(equation.replace(/\^/g, '**'), { x: xRounded });
            dataPoints.push({ x: xRounded, y });
        } catch {
            dataPoints.push({ x: xRounded, y: null });
        }
    }

    // Destroy previous chart if one exists
    if (window.currentChart) window.currentChart.destroy();

    window.currentChart = new Chart(canvas, {
        type: 'line',
        data: {
            datasets: [{
                label: `y = ${equation}`,
                data: dataPoints,
                borderColor: 'rgb(75, 192, 192)',
                borderWidth: 2,
                pointRadius: 0,
                tension: 0.1
            }]
        },
        options: {
            parsing: false,
            scales: {
                x: {
                    type: 'linear',
                    title: { display: true, text: 'x' }
                },
                y: {
                    title: { display: true, text: 'y' }
                }
            }
        }
    });
}

document.addEventListener("DOMContentLoaded", function() {
    const question = sessionStorage.getItem("question");
    const image = sessionStorage.getItem("image");
    console.log("Question:", question);
    if (question) {
        document.getElementById("displayedQ").innerText = question;
        send_question(question);
        sessionStorage.removeItem("question");
    }
    if (image) {
        console.log("got image")
        var img = document.getElementById("displayImg");
            img.style.display = "block";
            img.style.maxWidth = "600px";
            img.style.maxHeight = "300px";
            img.style.objectFit = "contain"; 
            img.style.margin = "0 auto";
        ocr(image)
        sessionStorage.removeItem("image");

        
    }
});

document.getElementById("inpBox").addEventListener("keypress", function(event) {
    if (event.key == "Enter") {
        event.preventDefault();
        const followUp = document.getElementById("inpBox").value.trim();
        if (followUp.length > 0) {
            send_question(followUp);
            document.getElementById("inpBox").value = ""; 
        }
    }
});

async function ocr(img){
    const { createWorker } = Tesseract;
    const worker = await createWorker('eng');
    console.log("Function Starting")

    const {data: {text}} = await worker.recognize(img)
    console.log("Image translated")
    console.log(text)
    await worker.terminate()
    send_question(text)
}

async function send_followup(follow_up) {
    var res = await fetch("/followup", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ follow_up })
    });

    var data = await res.json();
    document.getElementById("aiChat").innerHTML += `
        <p><b>You:</b> ${follow_up}</p>
        <div><b>Bot:</b> ${renderAnswer(data.answer)}</div>
    `;
    MathJax.typesetPromise();
}