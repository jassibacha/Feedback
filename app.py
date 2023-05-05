from flask import Flask, render_template, redirect, session, flash, url_for, abort, request
from functools import wraps
from flask_debugtoolbar import DebugToolbarExtension
from models import connect_db, db, User, Feedback
from forms import *
from sqlalchemy.exc import IntegrityError
#from secrets import SECRET_KEY

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///feedback"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True
app.config["SECRET_KEY"] = SECRET_KEY
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.app_context().push()


connect_db(app)
db.create_all()

toolbar = DebugToolbarExtension(app)


def logged_in(func):
    """Confirm that the user is logged in by username in session"""

    @wraps(func)
    def func_wrapper(*args, **kwargs):
        if "username" not in session:
            flash("Please login first!", "danger")
            return redirect('/login')

        return func(*args, **kwargs)

    return func_wrapper

def yourself_only(func):
    """Confirm that the user is logged in by username in session"""

    @wraps(func)
    def func_wrapper(username, *args, **kwargs):
        if "username" not in session:
            flash("Please login first!", "danger")
            return redirect('/login')

        if session['username'] != username:
            flash(f"User '{username}' isn't you! Redirecting to your profile page.", "danger")
            return redirect(f'/users/{session["username"]}')

        return func(username, *args, **kwargs)

    return func_wrapper

def login_username():
    """Return current login username"""
    return session.get('username', None)

@app.route('/')
def home_page():
    """The home page"""
    return redirect('/register')

@app.route('/register', methods=['GET', 'POST'])
def register_user():
    """Register page, GET & POST"""
    if login_username():
        return redirect(url_for("user_page", username=login_username()))
    form = RegisterForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        email = form.email.data
        first_name = form.first_name.data
        last_name = form.last_name.data
        new_user = User.register(username, password, email, first_name, last_name)

        db.session.add(new_user)
        try:
            db.session.commit()
        except IntegrityError:
            form.username.errors.append('Username taken. Please pick another')
            return render_template('register.html', form=form)
        session['username'] = new_user.username
        flash(f'Account created. Welcome {new_user.username}!', "success")
        return redirect(url_for("user_page", username=login_username()))

    return render_template('register.html', form=form)


# **GET */login :*** Show a form that when submitted will login a user. This form should accept a username and a password. Make sure you are using WTForms and that your password input hides the characters that the user is typing!

# **POST */login :*** Process the login form, ensuring the user is authenticated and going to ***/secret*** if so.

@app.route('/login', methods=['GET', 'POST'])
def login_user():
    """Login page"""
    if login_username():
        return redirect(url_for("user_page", username=login_username()))
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        user = User.authenticate(username, password)
        if user:
            flash(f"Welcome Back, {user.username}!", "primary")
            session['username'] = username
            return redirect(url_for("user_page", username=login_username()))
        else:
            form.username.errors = ['Invalid username or password.']

    return render_template('login.html', form=form)

# **GET */secret :*** Return the text “You made it!” (don’t worry, we’ll get rid of this soon)
@app.route('/secret', methods=['GET'])
@logged_in
def secret_page():

    return render_template("secret.html")

@app.route('/logout') #SHOULD BE A POST ROUTE, NOT A GET ROUTE. POST IS BEST PRACTICE
def logout_user():
    """Logout route"""
    session.pop('username')
    flash("You've been successfully logged out", "info")
    return redirect('/login')

@app.route('/users/<string:username>')
@yourself_only
def user_page(username):
    """User profile page"""
    user = User.query.get_or_404(username)
    return render_template("user-profile.html", user=user)

@app.route('/users/<string:username>/delete')
@yourself_only
def user_delete(username):
    """User profile page"""
    user = User.query.get_or_404(username)
    temp_username = user.username
    db.session.delete(user)
    db.session.commit()
    session.pop('username')
    flash(f'Deleted "{temp_username}".', 'primary')
    return redirect(url_for("register_user"))


@app.route('/users/<string:username>/feedback/add', methods=['GET', 'POST'])
@yourself_only
def feedback_add(username):
    """Form to add feedback and display feedback of current logged in user"""
    # import pdb
    # pdb.set_trace()
    form = FeedbackForm()
    user = User.query.get_or_404(username)

    if form.validate_on_submit():
        title = form.title.data
        content = form.content.data

        feedback = Feedback(title=title, content=content, username=user.username)
        if feedback:
            db.session.add(feedback)
            db.session.commit()
            flash(f'Feedback "{title}" Added!', 'primary')
            # session['username'] = username
            return redirect(url_for("user_page" , username=user.username))
        else:
            form.username.errors = ['Ensure both fields are not empty.']
    return render_template('feedback.html', form=form)



@app.route('/feedback/<int:feedback_id>/update', methods=['GET', 'POST'])
@logged_in
def feedback_update(feedback_id):
    """Form to update feedback and display feedback of current logged in user"""

    feedback = Feedback.query.get_or_404(feedback_id)
    username = feedback.username

    if feedback.username != login_username():
        flash('Update your own feedback only, Please!' , 'danger')
        return redirect(url_for("user_page" , username=login_username()))

    # obj=feedback helps auto populate the values, what a life saver
    form = FeedbackForm(obj=feedback)

    if form.validate_on_submit():
        # automatically update the attributes of feedback var with the values in form
        # another massive life saver
        form.populate_obj(feedback)
        db.session.commit()
        flash(f'Feedback "{feedback.title}" Updated!', 'primary')
        return redirect(url_for("user_page" , username=login_username()))
    # pass feedback in at the end to help swap the add/edit text on the html
    return render_template('feedback.html', form=form, feedback=feedback, username=username)


@app.route('/feedback/<int:feedback_id>/delete', methods=['POST'])
@logged_in
def feedback_delete(feedback_id):
    """Delete the feedback"""
    feedback = Feedback.query.get_or_404(feedback_id)
    temp_username = feedback.username
    temp_title = feedback.title
    if temp_username != login_username():
        flash('Delete your own feedback only please!' , 'danger')
        return redirect(url_for("user_page" , username=login_username()))
    db.session.delete(feedback)
    db.session.commit()
    flash(f'Feedback "{temp_title}" deleted.', 'primary')
    return redirect(url_for("user_page", username=temp_username))

# @app.route('/tweets/<int:id>', methods=["POST"])
# def delete_tweet(id):
#     """Delete tweet"""
#     if 'user_id' not in session:
#         flash("Please login first!", "danger")
#         return redirect('/login')
#     tweet = Tweet.query.get_or_404(id)
#     if tweet.user_id == session['user_id']:
#         db.session.delete(tweet)
#         db.session.commit()
#         flash("Tweet deleted!", "info")
#         return redirect('/tweets')
#     flash("You don't have permission to do that!", "danger")
#     return redirect('/tweets')
