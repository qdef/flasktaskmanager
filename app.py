from datetime import datetime

from flask import (
    Flask, render_template, url_for,
    request, redirect,
)
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'

db = SQLAlchemy(app)


def create_app():
    with app.app_context():
        db.init_app(app)
        db.create_all()
   
    return app


class Tasks(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<Task %r>' % self.id


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        task_content = request.form.get('content', 'No content')
        new_task = Tasks(content=task_content)
        try:
            db.session.add(new_task)
            db.session.commit()
            return redirect('/')
        except Exception as e:
            return f"An error occurred when adding the task to the database: {e}"

    else:
        tasks = Tasks.query.order_by(Tasks.updated_at.desc()).all()
        return render_template('index.html', tasks=tasks)


@app.route('/delete_task/<int:task_id>', methods=['GET'])
def delete_task(task_id):
    task_to_delete = Tasks.query.get_or_404(task_id)
    try: 
        db.session.delete(task_to_delete)
        db.session.commit()
        return redirect('/')
    except Exception as e:
        return f"An error occurred when deleting task #{task_id}: {e}"


@app.route('/update_task/<int:task_id>', methods=['GET', 'POST'])
def update_task(task_id):
    task = Tasks.query.get_or_404(task_id)
    
    if request.method == 'POST':
        # Update current Task
        task.content = request.form['content']
        task.updated_at = datetime.utcnow()
        try:
            # Add updated task to DB and go back to index page
            db.session.commit()
            return redirect('/task_updated/')
        except Exception as e:
            return f"An error occurred when updating task #{task_id}: {e}"
    else:
        # Display current Task
        return render_template('update_task.html', task=task)

@app.route('/task_updated/')
def task_updated():
    return render_template('task_updated.html')


if __name__ == '__main__':
    app.run(debug=True)
    db.create_all()

