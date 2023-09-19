from flask import Flask, render_template, request, redirect,jsonify, abort, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import sys

import config #config file where password and keys stored

#set up app and connections
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = config.database_uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)

#ToDoList Model
class ToDoList(db.Model):
    __tablename__ = 'todolists'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False)
    completed = db.Column(db.Boolean, nullable=False, default=False)
    todos = db.relationship('ToDo', backref='list', lazy=True)
    def __repr__(self):
        return f'<ID: {self.id}, Description: {self.description}>'

#ToDo Model
class ToDo(db.Model):
    __tablename__ = 'todos'
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(), nullable=False)
    completed = db.Column(db.Boolean, nullable=False, default=False)
    list_id=db.Column(db.Integer, db.ForeignKey('todolists.id'),nullable=False)
    def __repr__(self):
        return f'<ID: {self.id}, Description: {self.description}>'

with app.app_context():
    db.create_all()

#routes
@app.route('/todos/create', methods=['POST'])
def create_todo():
  error = False
  body = {}
  try:
    description = request.get_json()['description']
    list_id = request.get_json()['list_id']
    todo = ToDo(description=description, list_id=list_id)
    db.session.add(todo)
    db.session.commit()
    body['description'] = todo.description
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    abort (400)
  else:
    return jsonify(body)
    
@app.route('/todos/<todo_id>/set-completed', methods=['POST'])
def complete_todo(todo_id):
  error = False
  body = {}
  try:
    completed = request.get_json()['completed']
    todo = ToDo.query.get(todo_id)
    todo.completed=completed
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    abort (400)
  else:
    return redirect(url_for('index'))
  
@app.route('/todos/<todo_id>', methods=['DELETE'])
def delete_todo(todo_id):
  try:
    ToDo.query.filter_by(id=todo_id).delete()
    db.session.commit()
  except:
    db.session.rollback()
  finally:
    db.session.close()
  return jsonify({ 'success': True })

@app.route('/lists/<list_id>/delete', methods=['DELETE'])
def delete_list(list_id):
  try:
    list = ToDoList.query.get(list_id)
    for todo in list.todos:
        db.session.delete(todo)

    db.session.delete(list)
    db.session.commit()
  except:
    db.session.rollback()
  finally:
    db.session.close()
  return jsonify({ 'success': True })

@app.route('/lists/create', methods=['POST'])
def create_list():
  error = False
  body = {}
  try:
    name = request.get_json()['name']
    list = ToDoList(name=name)
    db.session.add(list)
    db.session.commit()
    body['name'] = list.name
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    abort (400)
  else:
    return jsonify(body)

@app.route('/lists/<list_id>/set-completed', methods=['POST'])
def complete_list(list_id):
  error = False
  body = {}
  try:
    completed = request.get_json()['completed']
    list = ToDoList.query.get(list_id)
    list.completed=completed
    for todo in list.todos:
            todo.completed = True
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    abort (400)
  else:
    return redirect(url_for('index'))  

@app.route('/lists/<list_id>')
def get_list_todos(list_id):
    return render_template('index.html', 
    lists=ToDoList.query.order_by('id').all(),
    active_list=ToDoList.query.get(list_id),
    todos=ToDo.query.filter_by(list_id=list_id).order_by('id').all())

@app.route('/')
def index():
    return redirect(url_for('get_list_todos', list_id=1))

if __name__ == '__main__':
   app.run(host="0.0.0.0", port=3000) 