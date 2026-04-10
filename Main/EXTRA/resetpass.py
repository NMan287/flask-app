from flask import Blueprint, render_template, request, jsonify
from EXTRA.loginandreg import user
from EXTRA.tables import db, user
from datetime import datetime, timedelta
import secrets
import requests
import bcrypt

reset_pass_bp = Blueprint('resetPassword', __name__)

EMAILJS_SERVICE_ID = 'service_057n18v'
EMAILJS_TEMPLATE_ID = 'template_uqtdtxs' 
EMAILJS_PUBLIC_KEY = 'PD2xvFXZY13lUJ41H'
EMAILJS_PRIVATE_KEY = 'SElFMZmlvV-8dAolwarV6'
# all above needed for emailJS to work

class password_reset(db.Model):
    reset_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    token = db.Column(db.String(100), unique=True, nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    used = db.Column(db.Boolean, default=False)

@reset_pass_bp.route('/api/auth/forgot-password', methods=['POST'])
def forgot_password():
    data = request.get_json() # grabs json data sent with request
    email = data.get('email')

    user = user.query.filter_by(userEmail=email).first()

    if not user:
        return jsonify({'message': 'An email has been sent'})

    token = secrets.token_urlsafe(32)
    expires_at = datetime.utcnow() + timedelta(hours=1)

    reset_token = password_reset(
        user_id = user.user_id,
        token = token,
        expires_at = expires_at
    )
    db.session.add(reset_token)
    db.session.commit()

    reset_link = 'http://localhost:5000/reset-password?token=' + token

    print('sending email to:', user.userEmail)
    print('found user:', user)


    response = requests.post('https://api.emailjs.com/api/v1.0/email/send', json={
        'service_id': EMAILJS_SERVICE_ID,
        'template_id': EMAILJS_TEMPLATE_ID,
        'user_id': EMAILJS_PUBLIC_KEY,
        'accessToken': EMAILJS_PRIVATE_KEY,
        'template_params': {
            'email': user.userEmail,
            'link': reset_link,
        }
    }) # sends post to emailjs to send an email

    return jsonify({'message': 'An email has been sent'})


@reset_pass_bp.route('/api/auth/reset-password', methods=['POST'])
def reset_password():
    data = request.get_json()
    token = data.get('token')
    new_password = data.get('password')

    reset_token = password_reset.query.filter_by(token=token, used=False).first() #for acessing the site to reset pass

    if not reset_token or reset_token.expires_at < datetime.utcnow():
        return jsonify({'error': 'Session expired'})

    user = user.query.get(reset_token.user_id)

    # hash for security
    hashed = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
    user.user_pass = hashed.decode('utf-8')

    reset_token.used = True
    db.session.commit()

    return jsonify({'message': 'Password reset successfully'})

@reset_pass_bp.route('/reset-password')
def reset_password_page():
    return render_template('Account/resetPass.html')