from datetime import datetime
from flask import url_for
from marshmallow import fields
from rddserver import db, ma, app


class User(db.Model):
    ROLE_INSPECTOR = "ins"
    ROLE_MAINTAINER = "mai"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    role = db.Column(db.String(3), nullable=False)

    def __repr__(self):
        return f"<User {self.username}, {self.role}>"


class Issue(db.Model):
    STATUS_INSPECTOR = "ins"
    STATUS_MAINTAINER = "mai"
    STATUS_ACCEPTED = "acc"
    STATUS_DECLINED = "dec"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False)
    mobile = db.Column(db.String(10), nullable=False)
    details = db.Column(db.String(250), nullable=False)
    location = db.Column(db.String(50), nullable=False)
    photo = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(3), default=STATUS_INSPECTOR, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Complain {self.name}, {self.details}>, {self.date}"

# Schema Classes
class IssueSchema(ma.Schema):
    photo = fields.Function(lambda obj: url_for('static', filename=f"uploads/{obj.photo}"))
    date= fields.Function(lambda obj: f"{obj.date:%d, %b %Y}")
    class Meta:
        fields = ('id', 'name', 'mobile', 'details', 'location', 'photo' ,'status', 'date')


# Schema variables 
issue_schema = IssueSchema()
issues_schema = IssueSchema(many=True)