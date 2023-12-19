#!/home/dhanesh/PycharmProjects/event/event_registration_system/venv/bin/python

from flask import Flask, request,render_template, redirect, url_for, flash, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_wtf.file import FileField, FileAllowed

from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, DateTimeField, IntegerField, PasswordField
from wtforms.validators import InputRequired, Email
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

from flask_uploads import UploadSet, configure_uploads, IMAGES, UploadNotAllowed
import csv
from io import StringIO

app = Flask(__name__)
# Assignment Requirement
# 6. Database and Backend:
# Use SQLite as the database backend for your chosen Python web framework.
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///events.db'
app.config['SECRET_KEY'] = 'your_secret_key'
db = SQLAlchemy(app)
migrate = Migrate(app, db)

login_manager = LoginManager(app)
login_manager.login_view = 'login'

photos = UploadSet("photos", IMAGES)
app.config["UPLOADED_PHOTOS_DEST"] = "uploads"
configure_uploads(app, photos)

# Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

# Assignment Requirement

# Event Information:
# Each event should have the following details:
# . Event Name
# . Event Date and Time
# . Event Location
# . Event Description
# . Maximum Number of Participants

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    date_time = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    max_participants = db.Column(db.Integer, nullable=False)
    participants = db.relationship('Participant', backref='event', lazy=True)
    image_path = db.Column(db.String(255))

    def __init__(self, name, date_time, location, description, max_participants,image_path=False):
        self.name = name
        self.date_time = date_time
        self.location = location
        self.description = description
        self.max_participants = max_participants
        # self.image_path = image_path if image_path else '/home/dhanesh/Downloads/129559647758niW3Iyg78OliyvttJxqWx (1).png'
        self.image_path = image_path if image_path else 'Getty.jpg'


# Assignment Requirement

# 2. Participants should provide their:
# . First Name, Last Name ,Profile Picture (optional)
#   Email Address (unique) and  Phone Number
class Participant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    profile_picture = FileField('Profile Picture', validators=[FileAllowed(['jpg', 'png'], 'Images only!')])
    email = db.Column(db.String(100), unique=True, nullable=False)
    phone_number = db.Column(db.String(20), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)


# Forms
class EventForm(FlaskForm):
    name = StringField('Event Name', validators=[InputRequired()])
    date_time = DateTimeField('Event Date and Time', validators=[InputRequired()])
    location = StringField('Event Location', validators=[InputRequired()])
    description = TextAreaField('Event Description', validators=[InputRequired()])
    max_participants = IntegerField('Max Participants', validators=[InputRequired()])

class ParticipantForm(FlaskForm):
    first_name = StringField('First Name', validators=[InputRequired()])
    last_name = StringField('Last Name', validators=[InputRequired()])
    profile_picture = FileField('Profile Picture')
    email = StringField('Email Address', validators=[InputRequired(), Email()])
    phone_number = StringField('Phone Number', validators=[InputRequired()])

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired()])
    password = PasswordField('Password', validators=[InputRequired()])

class SignUpForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired()])
    password = PasswordField('Password', validators=[InputRequired()])

# Routes
@app.route('/')
def index():

    search_term = request.args.get('search', '')
    # Assignment Requirement
    # 3. Filtering and Display:
    #  Users should be able to filter events by their type or by date.


    if search_term:
        events = Event.query.filter(
            (Event.name.ilike(f"%{search_term}%")) |
            (Event.date_time.ilike(f"%{search_term}%"))
        ).all()
    else:
        # A list of events should be displayed, showing their names, dates, and locations.
        events = Event.query.all()

    # events = Event.query.all()
    return render_template('index.html', events=events)


# 4. Event Details:
# 1. Clicking on an event's name should lead to its details page.
# 2. The event details page should display all information about the event.
@app.route('/event/<int:event_id>')
def event_details(event_id):
    event = Event.query.get(event_id)
    return render_template('event_details.html', event=event)

# Assignment Requirement
# 1. Users should be able to register for events.
@app.route('/register/<int:event_id>', methods=['GET', 'POST'])
# @login_required
def register(event_id):
    event = Event.query.get(event_id)
    form = ParticipantForm()

    if request.method == 'POST':
        existing_participant = Participant.query.filter_by(email=form.email.data).filter_by(event=event).first()
        print("existing_participant========= ", existing_participant)
        if existing_participant:
            flash('participant email already registered', 'error')
            render_template('register.html', form=form, event=event)
        # if form.validate_on_submit():
        else:
            participant = Participant(
                first_name=form.first_name.data,
                last_name=form.last_name.data,
                profile_picture=form.profile_picture.data,
                email=form.email.data,
                phone_number=form.phone_number.data,
                event=event
            )
            db.session.add(participant)
            db.session.commit()
            flash('Registration successful!', 'success')
            return redirect(url_for('event_details', event_id=event_id))

    return render_template('register.html', form=form, event=event)

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'csv'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignUpForm()

    if form.validate_on_submit():
        # Replace the next line with your actual user registration logic
        existing_user = User.query.filter_by(username=form.username.data).first()

        if existing_user:
            flash('Username already taken', 'error')
        else:
            # Create a new user
            new_user = User(username=form.username.data, password=form.password.data)
            db.session.add(new_user)
            db.session.commit()
            flash('Registration successful!', 'success')
            return redirect(url_for('login'))

    return render_template('signup.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        # Replace the next line with your actual user authentication logic
        user = User.query.filter_by(username=form.username.data).first()

        if user and user.password == form.password.data:
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('importer'))
        else:
            flash('Invalid username or password', 'error')

    return render_template('login.html', form=form)



# 5. Importer
# A secure importer is needed to bulk-add event details to the system.
# Only logged-in users should be able to access and use the importer.
# The importer should handle CSV files with event details and image filenames.
# If an image is missing, a default placeholder image should be used.
# 7. Authentication:
# Implement user authentication to secure access to the importer and other functionalities.
@app.route('/importer', methods=['GET', 'POST'])
@login_required
def importer():

    if request.method == 'POST':
        # Check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part', 'error')
            return redirect(request.url)

        file = request.files['file']

        # If the user does not select a file, browser submits an empty file without a filename
        if file.filename == '':
            flash('No selected file', 'error')
            return redirect(request.url)

        # If the file is valid, process it
        if file and allowed_file(file.filename):
            try:
                stream = StringIO(file.stream.read().decode("UTF8"), newline=None)
                csv_input = csv.DictReader(stream)

                for row in csv_input:
                    print("ROWS==============",row)
                    event = Event(
                        name=row['name'],
                        date_time=row['date_time'],
                        location=row['location'],
                        description=row['description'],
                        max_participants=row['max_participants']
                    )
                    db.session.add(event)
                db.session.commit()
                flash('Events imported successfully', 'success')
                return redirect(url_for('index'))
            except Exception as e:
                print(str(e))
                flash('Error importing events', 'error')
                return redirect(request.url)

    return render_template('importer.html')

# Additionally work to Download CSV file for events
@app.route('/download_csv')
def download_csv():

    data = [
        {'name': 'Event 1', 'date_time': '2023-01-01', 'location': 'City 1',
         'description':'any','max_participants':100},
    ]

    csv_output = StringIO()
    csv_writer = csv.DictWriter(csv_output, fieldnames=['name', 'date_time', 'location',
                                                        'description','max_participants'])
    csv_writer.writeheader()
    csv_writer.writerows(data)

    response = make_response(csv_output.getvalue())
    response.headers['Content-Disposition'] = 'attachment; filename=events.csv'
    response.headers['Content-Type'] = 'text/csv'

    return response


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


if __name__ == 'app':
    with app.app_context():
        db.create_all()
        print("ALL TABLES CREATED================")
    app.run(debug=True)
