import os
from flask import render_template, request, url_for, redirect, session, jsonify
from sqlalchemy import desc as sql_desc
from werkzeug.utils import secure_filename

from rddserver import app, bcrypt, db
from rddserver.models import User, Issue, issues_schema


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        if username and password:
            user = User.query.filter_by(username=username).first()
            if user and bcrypt.check_password_hash(user.password, password):
                session['username'] = user.username
                session['name'] = user.name
                session['role'] = user.role
                return redirect(url_for('admin'))
        return render_template('login.html', error="Incorrect username or password!")

    return render_template('login.html')


@app.route('/admin')
def admin():
    if 'username' in session:
        if session.get('role') == User.ROLE_INSPECTOR:
            issues = Issue.query.order_by(sql_desc(Issue.date))
            return render_template('admin.html', issues=issues)
        elif session.get('role') == User.ROLE_MAINTAINER:
            return render_template('maintainer.html')

    return redirect(url_for('login', error="You must login first!"))


@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('role', None)
    return redirect(url_for('login'))


@app.route('/issue', methods=['POST'])
def add_issue():
    return jsonify(request.json)
    name = request.json['name']
    mobile = request.json['mobile']
    details = request.json['details']
    latitude = request.json['latitude']
    longitude = request.json['longitude']
    photo = request.files['photo']

    filename = secure_filename(photo.filename)
    photo.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

    new_issue = Issue(name=name,
                      mobile=mobile,
                      details=details,
                      latitude=latitude,
                      longitude=longitude,
                      photo=filename)
    db.session.add(new_issue)

    db.session.commit()
    return issue_schema.jsonify(new_issue)


@app.route('/issue/<mobile>', methods=['GET'])
def get_issues_by_number(mobile):
    issues = Issue.query.filter_by(mobile=mobile).all()
    result = issues_schema.dump(issues)

    return jsonify(result)
