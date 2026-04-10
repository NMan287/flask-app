const display = document.getElementById("display");
let justCalculated = false; // tracks if a result was just shown

function append_to_display(input){
    if (justCalculated || display.value === "Input Error" || display.value === "Cannot divide by zero") {
        const operators = ['+', '-', '*', '/'];
        if (!operators.includes(input)) {
            display.value = "";
        } else {
            display.value = ""; // always clear on error, even if they press an operator
        }
        justCalculated = false;
    }
    display.value += input;
}

function clear_display(){
    display.value = "";
    justCalculated = false;
}

function delete_value(){
    display.value = display.value.slice(0, -1);
}

function calculate(){
    const expression = display.value;

    // check for invalid consecutive operators like +*, /+, ** etc
    if (/[+\-*/]{2,}/.test(expression)) {
        display.value = "Input Error";
        justCalculated = false;
        return;
    }

    // check expression doesn't start or end with an operator (except leading minus)
    if (/[+*/]$/.test(expression) || /[+*\/]/.test(expression[0])) {
        display.value = "Input Error";
        justCalculated = false;
        return;
    }

    // check for divide by zero
    if (/\/\s*0(\D|$)/.test(expression)) {
        display.value = "Cannot divide by zero";
        justCalculated = false;
        return;
    }

    try {
        const result = eval(expression);

        if (!isFinite(result)) { // catches any other division by zero edge cases
            display.value = "Cannot divide by zero";
            justCalculated = false;
            return;
        }

        display.value = result;
        justCalculated = true; // mark that a result is now showing

        fetch("/push", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ value: expression + " = " + result })
        });

    } catch (e) {
        display.value = "Input Error";
        justCalculated = false;
    }
}

document.getElementById("history").onclick = async function() { 
    const historyBox = document.getElementById("histCont");
    
    const response = await fetch("/get_list");
    const data = await response.json();

    // clear existing items before re-rendering
    historyBox.innerHTML = "<h1>History</h1>";

    if (data.length === 0) {
        const empty = document.createElement("p");
        empty.innerHTML = "No calculations yet";
        historyBox.appendChild(empty);
        return;
    }

    data.forEach(item => {
        const calc = document.createElement("p");
        calc.innerHTML = item;
        historyBox.appendChild(calc);
    });
}