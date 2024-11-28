from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from send_email import send_email



# Initialize Flask app and set up SQLite database
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key' 
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///agile_dashboard.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True




# Initialize SQLAlchemy
db = SQLAlchemy(app)

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)


# Route to display the login form
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Query the database for the user
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password, password):
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'danger')
            return redirect(url_for('login'))
    
    return render_template('login.html')


@app.route('/forgotpassword', methods=['GET', 'POST'])
def forgotpassword():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        sender_email = "ankitaisadoctor@gmail.com"
        sender_password = "ihkskbdmdlitzbbh"  # Use an app password if using Gmail
        receiver_email = email
        password_to_send = "T01254"  
        
        send_email(sender_email, sender_password, receiver_email, password_to_send)
        flash('Email sent successfully!', 'success')
        return redirect(url_for('login'))

    
         
    return render_template('forgotpassword.html')
        



@app.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    if request.method == 'POST':
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']

        if new_password == confirm_password:
            # Logic to reset the user's password in the database
            flash('Your password has been successfully reset!', 'success')
            return redirect(url_for('login'))
        else:
            flash('Passwords do not match. Please try again.', 'error')

    return render_template('reset_password.html')





# Route for the dashboard after successful login
@app.route('/dashboard')
def dashboard():
    return "Welcome to the Dashboard!"


# Route for the signup page
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        # Get data from the form
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        # Validate inputs
        if password != confirm_password:
            flash("Passwords do not match!", "error")
            return redirect(url_for('signup'))

        # Check if username or email already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash("Username already exists!", "error")
            return redirect(url_for('signup'))

        existing_email = User.query.filter_by(email=email).first()
        if existing_email:
            flash("Email already exists!", "error")
            return redirect(url_for('signup'))

        # Hash the password before storing
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

        # Create new user and add to the database
        new_user = User(username=username, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        
        flash("Signup successful! You can now log in.", "success")
        return redirect(url_for('login'))

    return render_template('signup.html')

# Main block to run the app
if __name__ == '__main__':
    app.run(debug=True)



