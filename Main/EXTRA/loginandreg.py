from flask import render_template, redirect, url_for, request, flash, session, Blueprint
import bcrypt
from EXTRA.tables import user, db

login_reg_bp = Blueprint('login_reg', 
                         __name__, 
                         template_folder='../templates') # avoids curcular imports
                                                        # connects database together


@login_reg_bp.route('/userLogin', methods=["GET", "POST"])
def user_login():
    if request.method == "POST":
        user_email = request.form.get("email") 
        user_pass = request.form.get("password")
        found_user = user.query.filter_by(user_email=user_email).first() 
        if found_user:
            if bcrypt.checkpw(user_pass.encode('utf-8'), found_user.user_pass.encode('utf-8')):
                session['user_id'] = found_user.user_id
                return redirect(url_for("home.home"))
            else:
                flash("Incorrect password") 
                return redirect(url_for('login_reg.user_login'))
        else:
            flash("User not found")
            return redirect(url_for('login_reg.user_login'))
    return render_template("Account/login.html") 


@login_reg_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login_reg.login'))


@login_reg_bp.route('/resetPass')
def forgot_pass():
    return render_template("Account/passresetTemplate.html") # not functional yet

@login_reg_bp.route('/')
def login():
    return render_template('Account/login.html')

@login_reg_bp.route('/register')
def register():
    return render_template('Account/register.html')


@login_reg_bp.route('/add', methods=["POST"])
def add_user():
    user_email = request.form.get("email")
    username = request.form.get("username")
    user_pass = request.form.get("password")
    confirm_pass = request.form.get("confirm_pass")  
    confirm_email = request.form.get("confirm_email")

    user_email = user_email.strip().lower()
    confirm_email = confirm_email.strip().lower()
    if user_email != confirm_email:
        flash("Emails do not match")
        return redirect(url_for("login_reg.register"))
    elif user_pass != confirm_pass: 
        flash("Passwords do not match")
        return redirect(url_for("login_reg.register"))

    hash_pass = bcrypt.hashpw(user_pass.encode('utf-8'), bcrypt.gensalt()) # pass hashed with salt (extra chars)
    if user_email and username and user_pass:
        existing_user = user.query.filter_by(username=username).first()
        existing_email = user.query.filter_by(user_email=user_email).first()
        if existing_user:
            flash("Username Already taken")
            return redirect(url_for('login_reg.register'))
        elif existing_email:
            flash("Email already Registered")
            return redirect(url_for("login_reg.register"))
        else:
            new_user = user(user_email=user_email, username=username, user_pass=hash_pass.decode('utf-8'))
            try:
                db.session.add(new_user)
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                print("db error:", e)
                flash("Something went wrong, please try again")
                return redirect(url_for("login_reg.register"))
        return redirect(url_for("login_reg.user_login"))
    else:
        return redirect(url_for("login_reg.register"))