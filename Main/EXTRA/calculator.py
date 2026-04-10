from flask import jsonify, request, render_template, Blueprint

calculator_bp = Blueprint('calculator', __name__, template_folder='templates')

# Stack

stack = []
# stores last 10 calcs

def is_empty():
    return len(stack) == 0

def push(item):
    if len(stack) >= 10:
        stack.pop(0) # removes oldest calculation
    stack.append(item)
    return "ok"

def pop():
    if is_empty():
        return "Empty"
    return stack.pop()

def peek():
    if is_empty():
        return "Empty"
    else:
        return stack[-1]

def show_stack():
    return list(stack)


@calculator_bp.route("/") 
def calculator():
    return render_template("calculator.html")


@calculator_bp.route("/push", methods=["POST"])
def push_route():
    value = request.json["value"]  # pushes calculation
    push(value)
    return jsonify({"stack": show_stack()})


@calculator_bp.route("/get_list")
def get_stack():
    return jsonify(stack)

