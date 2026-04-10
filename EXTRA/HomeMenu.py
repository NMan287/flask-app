from flask import render_template,  Blueprint

home_bp = Blueprint('home', __name__, template_folder='templates')

# loads the main home page
@home_bp.route('/Home')
def home():
    return render_template("Home/HomeMenu.html")

# loads calculator page
@home_bp.route("/Calculator")
def calculator_page():
    return render_template('Calculator/calculator.html') 

#loads forum page
@home_bp.route("/Forum")
def forum_page():
    return render_template('Forum/forum.html')

# loads questions page
@home_bp.route("/Questions")
def questions_page():
    return render_template('Questions/questions.html')

# loads settings page
@home_bp.route("/Settings")
def settings_page():
    return render_template('User Management/Settings.html')

# loads login page
@home_bp.route('/login')
def login():
    return render_template('Account/login.html')

# loads register page
@home_bp.route('/register')
def register():
    return render_template('Account/register.html') 

# loads question test page
@home_bp.route("/QuestionTest")
def question_test():
    return render_template("Questions/QuestionsTest.html") 

# loads questions the user done
@home_bp.route("/MyQuestions")
def my_questions():
    return render_template("Questions/MyQuestions.html")
