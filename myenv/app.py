from flask import Flask, render_template, request, flash, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mydatabase.db'
app.config['SECRET_KEY'] = 'off911on999m5m3m4orrs6orghost'
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    fullname = db.Column(db.String(100), unique=True, nullable=False)
    is_active = db.Column(db.Boolean, default=True)  
    
    def is_authenticated(self):
        return True

    def is_active(self):
        return self.is_active

    def is_anonymous(self):
        return False
    
    
    def get_id(self):
        return str(self.id)

login_manager = LoginManager(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@login_manager.unauthorized_handler
def unauthorized_callback():
    flash("You need to log in to access this page.")
    return redirect('/login')

class Sculpture(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    image_path = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)



@app.route("/")
@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Retrieve form data
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        fullname = request.form.get('fullname')
     
        # Check if the fullname already exists in the database
        existing_user = User.query.filter_by(fullname=fullname).first()
        if existing_user:
            return "Error: Fullname already exists. Please choose a different fullname."
        
        # Create a new User object
        new_user = User(username=username, email=email, password=password, fullname=fullname)

        # Add the new user to the database
        db.session.add(new_user)
        db.session.commit()

        # Redirect to a success page or perform any other desired action after registration
        return redirect("/profile")

    # Handle registration logic
    return render_template('register.html')

@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Retrieve form data
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Check if the user exists in the database and the password is correct
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            login_user(user)  # Log in the user
            return redirect("/profile")
        else:
            flash("Invalid username or password")
    
    # Render the login form
    return render_template('login.html')

@app.route("/logout")
@login_required
def logout():
    logout_user()  # Log out the user
    return redirect("/login")

@app.route("/profile")
@login_required
def profile():
    user = User.query.get(current_user.id)
    return render_template("profile.html", user=user)

@app.route("/update_profile", methods=["POST"])
@login_required
def update_profile():
    # Retrieve form data
    fullname = request.form.get("fullname")
    email = request.form.get("email")
    
    # Update the user's information in the database
    user = User.query.get(current_user.id)
    user.fullname = fullname
    user.email = email
    db.session.commit()
    
    # Redirect to the updated profile page or a success message
    flash("Profile updated successfully")
    return redirect("/profile")

@app.route("/upload_sculpture", methods=["POST"])
@login_required
def upload_sculpture():
    # Retrieve form data
    sculpture_name = request.form.get("sculpture_name")
    sculpture_image = request.files.get("sculpture_image")
    sculpture_price = request.form.get("sculpture_price")
    
    # Process and store the uploaded sculpture data
    image_filename = secure_filename(sculpture_image.filename)
    image_path = os.path.join(app.config["UPLOAD_FOLDER"], image_filename)
    sculpture_image.save(image_path)
    
    new_sculpture = Sculpture(
        name=sculpture_name,
        image_path=image_path,
        price=sculpture_price,
        user_id=current_user.id
    )
    db.session.add(new_sculpture)
    db.session.commit()
    
    flash("Sculpture uploaded successfully")
    return redirect("/profile")

@app.route("/sculptures")
def sculptures():
    sculptures = Sculpture.query.all()
    return render_template("sculptures.html", sculptures=sculptures)



if __name__ == '__main__':
    app.config['UPLOAD_FOLDER'] = 'static/img'
    with app.app_context():
         db.create_all() 
    
    app.run(debug=True)