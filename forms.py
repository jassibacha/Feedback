from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField
from wtforms.validators import InputRequired, Email, Length


class RegisterForm(FlaskForm):
    username = StringField("Username", validators=[InputRequired(), Length(min=3, max=20)])
    password = PasswordField("Password", validators=[InputRequired()])
    email = StringField("Email Address", validators=[InputRequired(), Length(min=1, max=50), Email(message='Must be a valid email address')])
    first_name = StringField("First Name", validators=[InputRequired(), Length(min=1, max=30)])
    last_name = StringField("Last Name", validators=[InputRequired(), Length(min=1, max=30)])

class LoginForm(FlaskForm):
    username = StringField("Username", validators=[InputRequired(), Length(min=3, max=20)])
    password = PasswordField("Password", validators=[InputRequired()])

class FeedbackForm(FlaskForm):
    title = StringField("Title", validators=[InputRequired(), Length(min=1, max=100)])
    content = TextAreaField("Feedback", validators=[InputRequired()])

# class TweetForm(FlaskForm):
#     text = StringField("Tweet Text", validators=[InputRequired()])
