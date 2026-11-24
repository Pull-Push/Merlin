from flask_app import app
from flask import render_template, redirect, request, session, flash
from flask_app.models.user_model import User
from flask_app.controllers import room_controller  # noqa: F401 - registers routes
import bcrypt


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/new/user', methods=['POST'])
def register():
    info = request.form.to_dict()

    if not User.validate(info):
        return redirect('/')

    # Hash the password before saving
    info['password'] = bcrypt.hashpw(
        info['password'].encode('utf-8'), bcrypt.gensalt()
    ).decode('utf-8')

    User.save_user(info)
    flash("Account created! Please log in.", "success")
    return redirect("/dashboard")


@app.route('/login/user', methods=['POST'])
def login():
    info = request.form.to_dict()
    user = User.check_user(info)

    if not user:
        flash("No account found with that email.", "error")
        return render_template('index.html')

    if not bcrypt.checkpw(info['password'].encode('utf-8'), user.password.encode('utf-8')):
        flash("Incorrect password.", "error")
        return render_template('index.html')

    session['user_id'] = user.id
    session['username'] = user.username
    return redirect("/dashboard")
