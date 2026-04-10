from flask import Flask
from EXTRA.loginandreg import login_reg_bp
from EXTRA.HomeMenu import home_bp
from EXTRA.calculator import calculator_bp
from EXTRA.Answer import answer_bp
from EXTRA.tables import db
from EXTRA.forum import forum_bp
from EXTRA.resetpass import reset_pass_bp
from EXTRA.questions import questions_bp
from EXTRA.settings import settings_bp
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
app = Flask(__name__,
                    template_folder=os.path.join(BASE_DIR, "templates"),
                      static_folder=os.path.join(BASE_DIR, "static")) # locates folders for js and css
app.secret_key = "super_secret_key" # so data cannot be accessed by others
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
app.register_blueprint(home_bp)
app.register_blueprint(login_reg_bp)
app.register_blueprint(answer_bp)
app.register_blueprint(forum_bp)
app.register_blueprint(reset_pass_bp)
app.register_blueprint(calculator_bp)
app.register_blueprint(questions_bp, url_prefix="/questions")
app.register_blueprint(settings_bp)
# all above avoids circular imports
# connects to one system

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)

    # run command
    # python -m EXTRA.main

