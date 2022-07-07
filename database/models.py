import os
from flask import abort
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, String, Integer, create_engine, DateTime, ForeignKey
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_login import (
    UserMixin,
    login_user,
    LoginManager,
    current_user,
    logout_user,
    login_required,
)


# database_name = "project"

# database_path = "postgresql:///"+database_name
database_path = "postgres://tkqwgaxuehseft:c1e46be0ae11ab829011c47c8a2fcfc6a1cbe5d62c0c363962fe865a9b77d696@ec2-34-239-241-121.compute-1.amazonaws.com:5432/d3q0895e1aahhv"
db = SQLAlchemy()


def setup_db(app, database_path=database_path):
    app.secret_key = 'secret-key'
    app.config["SQLALCHEMY_DATABASE_URI"] = database_path
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
    db.app = app
    db.init_app(app)
    migrate = Migrate(app, db)


class Base(db.Model):
    __abstract__ = True

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()


class User(UserMixin, Base):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    pwd = db.Column(db.String(300), nullable=False, unique=True)

    # def validate_email(self, email):
    #     if User.query.filter_by(email=email.data).first():
    #         raise ValidationError("Email already registered!")

    # def validate_uname(self, uname):
    #     if User.query.filter_by(username=username.data).first():
    #         raise ValidationError("Username already taken!")

    def formate(self):
        return {
            'id': this.id,
            'username': this.username,
            'email': this.email,
            'pwd': this.pwd
        }


class Project(Base):
    __tablename__ = 'project'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    tasks = db.relationship('Task', backref='project',
                            cascade="all, delete", lazy=True)

    def __init__(self, name):
        self.name = name

    def formate(self):
        return {
            'id': self.id,
            'name': self.name,
        }


class Task(Base):
    __tablename__ = 'task'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    project_id = Column(Integer, ForeignKey('project.id'), nullable=False)

    def __init__(self, name, project_id):
        self.name = name
        self.project_id = project_id

    def formate(self):
        return {
            'id': self.id,
            'name': self.name,
            'project_id': self.project_id
        }
