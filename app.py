import os
import sys
from flask import Flask, request, abort, jsonify, render_template, redirect, url_for
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from flask_login import (
    UserMixin,
    login_user,
    LoginManager,
    current_user,
    logout_user,
    login_required,
)

from database.models import setup_db, db, Project, Task, User

bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.session_protection = "strong"
login_manager.login_view = "login"
login_manager.login_message_category = "info"


def create_app():
    app = Flask(__name__)
    setup_db(app)
    CORS(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)

    return app


app = create_app()


@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Headers',
                         'Content-Type,Authorization,true')
    response.headers.add('Access-Control-Allow-Methods',
                         'GET,PUT,POST,DELETE,OPTIONS,PATCH')
    return response


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        uname = request.form.get('username', '')
        passwd = request.form.get('password', '')
        # passwd = bcrypt.generate_password_hash(passwd)
        user = User.query.filter(
            User.username == uname).one_or_none()
        if(user):
            if bcrypt.check_password_hash(user.pwd, passwd):
                login_user(user)
                return redirect(url_for('index'))

    return render_template('login.html')


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        uname = request.form.get('username', '')
        passwd = request.form.get('password', '')
        email = request.form.get('username', '')
        user = User.query.filter((User.username == uname) | (
            User.email == email)).one_or_none()
        if not user:
            u = User(username=uname, email=email,
                     pwd=bcrypt.generate_password_hash(passwd).decode('utf-8'))
            u.insert()
            return redirect(url_for('login'))
    return render_template("signup.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    return render_template('index.html')


@app.route('/projects')
@login_required
def projects():
    try:
        formated_projects = [p.formate() for p in Project.query.all()]
        return jsonify({'success': True, 'data': formated_projects})
    except:
        db.session.rollback()
        abort(422)
    finally:
        db.session.close()


@app.route('/task/<int:id>')
@login_required
def task(id):
    task = Task.query.filter(Task.id == id).one_or_none()
    project = Project.query.get(task.project_id).formate()
    if task:
        return jsonify({'success': True, 'task': task.formate(), 'project': project})


@app.route('/project', methods=['POST'])
@login_required
def add_project():
    try:
        body = request.get_json()
        if 'project' in body:
            p = Project(name=body.get('project'))
            p.insert()

        return jsonify({'success': True, 'data': Project.query.get(p.id).formate()})
    except:
        db.session.rollback()
    finally:
        db.session.close()


@app.route('/project/<int:id>', methods=['PATCH'])
@login_required
def update_project(id):
    try:
        body = request.get_json()
        p = Project.query.filter(Project.id == id).one_or_none()
        if p:
            p.name = body.get('name')
        p.update()
        return {'done': True}
    except:
        db.session.rollback()
        abort(422)
    finally:
        db.session.close()


@app.route('/project/<int:id>', methods=['DELETE'])
@login_required
def delete_project(id):
    try:
        p = Project.query.filter(Project.id == id).one_or_none()
        p.delete()
        return {'success': True}
    except:
        db.session.rollback()
    finally:
        db.session.close()


@app.errorhandler(404)
def not_found(error):
    return jsonify({'success': False, 'error': 404,
                    'message': 'resource not found'}), 404


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({'success': False, 'error': 422,
                    'message': 'unprocessable'}), 422


if __name__ == "__main__":
    app.run(debug=True)
