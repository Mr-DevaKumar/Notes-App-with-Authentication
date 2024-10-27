from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change this to a random secret key
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///notes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False, unique=True)
    password_hash = db.Column(db.String(256), nullable=False)

class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    note_content = db.Column(db.Text, nullable=False)

@app.route('/')
def home():
    return render_template('home.html')
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        password_hash = generate_password_hash(password)
        new_user = User(username=username, password_hash=password_hash)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            session['user_id'] = user.id
            return redirect(url_for('notes'))
    return render_template('login.html')

@app.route('/notes')
def notes():
    # Ensure user is logged in
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # Fetch all notes for the logged-in user
    user_id = session['user_id']
    user_notes = Note.query.filter_by(user_id=user_id).all()
    
    # Pass notes to the template
    return render_template('notes.html', notes=user_notes)

@app.route('/add_note', methods=['POST'])
def add_note():
    if 'user_id' in session:
        user_id = session['user_id']
        note_content = request.form['note_content']
        
        # Assuming you have a Note model
        new_note = Note(user_id=user_id, note_content=note_content)
        db.session.add(new_note)
        db.session.commit()
        
        # Redirect to the 'notes' page after adding the note
        return redirect(url_for('notes'))
    
    return redirect(url_for('login'))  # Redirect to login if user is not logged in


if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create database tables
    app.run(debug=True)
