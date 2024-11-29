from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from send_email import send_email
from itsdangerous import URLSafeTimedSerializer
from flask import render_template_string




# Initialize Flask app and set up SQLite database
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key' 
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///agile_dashboard.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
serializer = URLSafeTimedSerializer(app.secret_key)




# Initialize SQLAlchemy
db = SQLAlchemy(app)

class User(db.Model):
    __tablename__ = 'users'
    UserID = db.Column(db.Integer, primary_key=True)
    UserName = db.Column(db.String(150), unique=True, nullable=False)
    Email = db.Column(db.String(150), unique=True, nullable=False)
    Password = db.Column(db.String(150), nullable=False)


# Route to display the login form
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Query the database for the user
        user = User.query.filter_by(UserName=username).first()
        
        if user and check_password_hash(user.Password, password):
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'danger')
            return redirect(url_for('login'))
    
    return render_template('login.html')
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
    email = request.form.get('email', '').strip()
    print(email)
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        print(email)

         # Generate token valid for 15 minutes (900 seconds)
        token = serializer.dumps(email, salt='password-reset-salt')

        # Generate the reset link with the token
        reset_link = url_for('reset_password', token=token, _external=True)

        sender_email = "ankitaisadoctor@gmail.com"
        sender_password = "ihkskbdmdlitzbbh"  # Use an app password if using Gmail
        receiver_email = "aayushaayush438@gmail.com"
        subject = "Password Reset Request"
        
        send_email(sender_email, sender_password, receiver_email, subject, reset_link)
        flash('Email sent successfully!', 'success')
        return redirect(url_for('login'))   
    return render_template('forgotpassword.html')
        



@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    
    try:
        # Validate token (expires in 900 seconds = 15 minutes)
        email = serializer.loads(token, salt='password-reset-salt', max_age=900)
    except Exception as e:
        flash('The reset link is invalid or has expired.', 'danger')
        return redirect(url_for('forgotpassword'))


    if request.method == 'POST':
            new_password = request.form['new-password']
            # Here, you should hash the new password and update the user's password in the database
            flash('Your password has been updated successfully!', 'success')
            return redirect(url_for('reset_password'))
    return render_template('reset_password.html', token=token)




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
        existing_user = User.query.filter_by(UserName=username).first()
        if existing_user:
            flash("Username already exists!", "error")
            return redirect(url_for('signup'))

        existing_email = User.query.filter_by(Email=email).first()
        if existing_email:
            flash("Email already exists!", "error")
            return redirect(url_for('signup'))

        # Hash the password before storing
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

        # Create new user and add to the database
        new_user = User(UserName=username, Email=email, Password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        
        flash("Signup successful! You can now log in.", "success")
        return redirect(url_for('login'))

    return render_template('signup.html')
    

# Main block to run the app
if __name__ == '__main__':
    app.run(debug=True)



