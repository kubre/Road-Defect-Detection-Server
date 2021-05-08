import os
import uuid
from flask import render_template, request, url_for, redirect, session, jsonify
from sqlalchemy import desc as sql_desc
from werkzeug.utils import secure_filename

from rddserver import app, bcrypt, db
from rddserver.models import User, Issue, issues_schema, issue_schema


def middleware_auth():
    if 'username' not in session:
        return redirect(url_for('login'))


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


@app.route('/admin/', methods=['GET'], defaults={'page': 1})
@app.route('/admin/<int:page>', methods=['GET'])
def admin(page):
    middleware_auth()
    per_page = 6
    if session.get('role') == User.ROLE_INSPECTOR:
        issues = Issue.query.filter_by(status=Issue.STATUS_INSPECTOR).order_by(
            sql_desc(Issue.date)).paginate(page, per_page, error_out=False)
        return render_template('inspector.html', issues=issues)
    elif session.get('role') == User.ROLE_MAINTAINER:
        issues = Issue.query.filter_by(status=Issue.STATUS_MAINTAINER).order_by(
            sql_desc(Issue.date)).paginate(page, per_page, error_out=False)
        return render_template('maintainer.html', issues=issues)


@app.route('/reports-forwarded/', methods=['GET'], defaults={'page': 1})
@app.route('/reports-forwarded/<int:page>', methods=['GET'])
def reports_forwarded(page):
    middleware_auth()
    per_page = 6
    issues = Issue.query.filter_by(status=Issue.STATUS_MAINTAINER).order_by(
        sql_desc(Issue.date)).paginate(page, per_page, error_out=False)

    return render_template('reports.html', issues=issues)


@app.route('/reports-work-started/', methods=['GET'], defaults={'page': 1})
@app.route('/reports-work-started/<int:page>', methods=['GET'])
def reports_wip(page):
    middleware_auth()
    per_page = 6
    issues = Issue.query.filter_by(status=Issue.STATUS_ACCEPTED).order_by(
        sql_desc(Issue.date)).paginate(page, per_page, error_out=False)

    return render_template('reports.html', issues=issues)


@app.route('/reports-declined/', methods=['GET'], defaults={'page': 1})
@app.route('/reports-declined/<int:page>', methods=['GET'])
def reports_declined(page):
    middleware_auth()
    per_page = 6
    issues = Issue.query.filter_by(status=Issue.STATUS_DECLINED).order_by(
        sql_desc(Issue.date)).paginate(page, per_page, error_out=False)

    return render_template('reports.html', issues=issues)


@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('role', None)
    return redirect(url_for('login'))


@app.route('/issue', methods=['POST'])
def add_issue():
    name = request.form['name']
    mobile = request.form['mobile']
    details = request.form['details']
    latitude = request.form['latitude']
    longitude = request.form['longitude']
    photo = request.files['photo']

    filename, ext = secure_filename(photo.filename).rsplit('.', 1)
    rnd = uuid.uuid4().hex
    filename = f"{rnd}.{ext}"
    photo.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

    location = f"{latitude},{longitude}"
    new_issue = Issue(name=name,
                      mobile=mobile,
                      details=details,
                      location=location,
                      photo=filename)
    db.session.add(new_issue)

    db.session.commit()
    return issue_schema.jsonify(new_issue)


@app.route('/issue/<mobile>', methods=['GET'])
def get_issues_by_number(mobile):
    issues = Issue.query.filter_by(
        mobile=mobile).order_by(sql_desc(Issue.date)).all()
    result = issues_schema.dump(issues)

    return jsonify(result)


@app.route('/issue/forward', methods=["POST"])
def forward_request():
    id = request.form['id']

    issue = Issue.query.filter_by(id=id).first()
    issue.status = Issue.STATUS_MAINTAINER
    db.session.commit()
    return redirect(url_for('admin'))


@app.route('/issue/decline', methods=["POST"])
def accpet_request():
    id = request.form['id']

    issue = Issue.query.filter_by(id=id).first()
    issue.status = Issue.STATUS_DECLINED
    db.session.commit()
    return redirect(url_for('admin'))


@app.route('/issue/accpet', methods=["POST"])
def decline_request():
    id = request.form['id']

    issue = Issue.query.filter_by(id=id).first()
    issue.status = Issue.STATUS_ACCEPTED
    db.session.commit()
    return redirect(url_for('admin'))


@app.route('/maps/<float:latitude>/<float:longitude>')
def maps(latitude, longitude):
    return render_template("maps.html", latitude=latitude, longitude=longitude)