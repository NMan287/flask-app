from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class user(db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    user_email = db.Column(db.String(50), nullable=False, unique=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    user_pass = db.Column(db.String(200), nullable=False) # password is hashed

class question_asked(db.Model):
    question_id = db.Column(db.Integer, primary_key=True) 
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=True) 
    quest_text = db.Column(db.String(500), nullable=True)
    ai_answer = db.Column(db.String(500), nullable=True)
    quest_image = db.Column(db.String(1000), nullable=True) # use ocr library to add to database

class user_posts(db.Model):
    post_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=True) 
    post_contents = db.Column(db.String(500), nullable=True)
    post_image = db.Column(db.String(1000), nullable=True)
    subject = db.Column(db.String(100))
    user = db.relationship('user', backref='posts', foreign_keys=[user_id])  # 'user' not 'Users'

class user_comments(db.Model):
    comment_id = db.Column(db.Integer, primary_key = True)
    comment_title = db.Column(db.String)
    post_id = db.Column(db.Integer, db.ForeignKey('user_posts.post_id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)  # also add the ForeignKey here
    body = db.Column(db.Text, nullable=False)
    user = db.relationship('user', backref='comments', foreign_keys=[user_id])  # 'user' not 'Users'

class test(db.Model):
    test_id = db.Column(db.Integer, primary_key = True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=True)
    q_num = db.Column(db.Integer)
    topic = db.Column(db.String(100))
    subject = db.Column(db.String(100))
    exam_board = db.Column(db.String(100))


class test_question(db.Model):
    question_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))
    test_id = db.Column(db.Integer, db.ForeignKey('test.test_id'))
    topic = db.Column(db.String(100))
    subject = db.Column(db.String(100))
    question_text = db.Column(db.String(1000))
    user_answer = db.Column(db.String(1000))
    ai_answer = db.Column(db.String(1000))
    is_correct = db.Column(db.Boolean)

