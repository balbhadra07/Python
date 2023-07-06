from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector
from wtforms.validators import ValidationError

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:root@localhost/todo_app'  # Replace with your own MySQL connection details
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)  # Add the first_name field
    tasks = db.relationship('Task', backref='user', lazy=True)

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200))
    status = db.Column(db.String(20), default='pending')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

def create_tables():
    with app.app_context():
        db.create_all()

create_tables()

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        first_name = request.form['first_name']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password != confirm_password:
            error = 'Passwords do not match!'
            flash(error, 'error')
            return redirect(url_for('register'))

        if User.query.filter_by(email=email).first():
            error = 'Email already exists!'
            flash(error, 'error')
            return redirect(url_for('register'))

        # Truncate the password value if it exceeds the maximum length
        max_password_length = 100  # Replace with the actual maximum length for the password column
        if len(password) > max_password_length:
            password = password[:max_password_length]

        hashed_password = generate_password_hash(password)
        user = User(email=email, password=hashed_password, first_name=first_name)
        db.session.add(user)
        db.session.commit()
        flash('Registration successful!', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        if not email or not password:
            flash('Please enter both email and password.', 'error')
            return redirect(url_for('login'))

        user = User.query.filter_by(email=email).first()

        if not user or not check_password_hash(user.password, password):
            error = 'Invalid email or password.'
            return redirect(url_for('login', error=error))

        session['user_id'] = user.id
        return redirect(url_for('dashboard'))

    # Retrieve the error message from the URL parameter
    error = request.args.get('error')
    return render_template('login.html', error=error)

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    user = User.query.get(user_id)

    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        task = Task(title=title, description=description, user_id=user.id, status='pending')  # Set the status to 'pending'
        db.session.add(task)
        db.session.commit()

    tasks = Task.query.filter_by(user_id=user.id).all()
    return render_template('dashboard.html', user=user, tasks=tasks)


@app.route('/update_task/<int:task_id>', methods=['GET', 'POST'])
def update_task(task_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    task = Task.query.get(task_id)
    if not task:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        new_title = request.form['title']
        new_description = request.form['description']
        task.title = new_title
        task.description = new_description
        db.session.commit()
        return redirect(url_for('dashboard'))

    return render_template('update_task.html', task=task)

@app.route('/delete_task/<int:task_id>', methods=['POST'])
def delete_task(task_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    task = Task.query.get(task_id)
    if task:
        db.session.delete(task)
        db.session.commit()

    return redirect(url_for('dashboard'))

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
