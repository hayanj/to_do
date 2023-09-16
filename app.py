from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import config #config file where password and keys stored

#set up app and connections
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = config.database_uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)

#ToDo Model
class ToDo(db.Model):
    __tablename__ = 'todos'
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(), nullable=False)
    completed = db.Column(db.Boolean, nullable=False, default=False)
    def __repr__(self):
        return f'<ID: {self.id}, Description: {self.description}>'

with app.app_context():
    db.create_all()

#routes
@app.route('/todos/create', methods=['POST'])
def create():
    todo_item=ToDo(description=request.form.get('description'),
                    completed=False)
    db.session.add(todo_item)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/')
def index():
    return render_template('index.html', data=ToDo.query.all())



if __name__ == '__main__':
   app.run(host="0.0.0.0", port=3000)