from flask import render_template, redirect, url_for, request, flash, session, Blueprint
from EXTRA.tables import user, db

settings_bp = Blueprint('settings', 
                         __name__, 
                         template_folder='../templates') # avoids curcular imports
                                                        # connects database together

@settings_bp.route('/user_change', methods=["GET", "POST"])
def username_change():
    if "user_id" not in session:
        return redirect(url_for('login_reg.login'))
    
    username = request.form.get("username")

    if not username or username.strip() == "":
        flash("Please enter a username")
        return redirect(url_for('forum.settings_page'))

    existing_user = user.query.filter_by(username=username).first()
    if existing_user:
        flash("Username already taken")
        return redirect(url_for('forum.settings_page'))
    
    try:
        current_user = user.query.get(session["user_id"])
        current_user.username = username
        db.session.commit()
        session["username"] = username  # update session too
        flash("Username updated successfully")
    except Exception as e:
        db.session.rollback()
        flash("Something went wrong")
    
    return redirect(url_for('forum.settings_page'))