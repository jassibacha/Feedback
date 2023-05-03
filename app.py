from flask import Flask, render_template, redirect, session, flash
from flask_debugtoolbar import DebugToolbarExtension
from models import connect_db, db, User
from forms import RegisterForm, LoginForm
from sqlalchemy.exc import IntegrityError
from secrets import SECRET_KEY

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///feedback"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True
app.config["SECRET_KEY"] = SECRET_KEY
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False



connect_db(app)
db.create_all()

toolbar = DebugToolbarExtension(app)


@app.route('/')
def home_page():
    return redirect('/register')

@app.route('/register', methods=['GET', 'POST'])
def register_user():
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
        return redirect('/secret')

    return render_template('register.html', form=form)


# **GET */login :*** Show a form that when submitted will login a user. This form should accept a username and a password. Make sure you are using WTForms and that your password input hides the characters that the user is typing!

# **POST */login :*** Process the login form, ensuring the user is authenticated and going to ***/secret*** if so.

@app.route('/login', methods=['GET', 'POST'])
def login_user():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        user = User.authenticate(username, password)
        if user:
            flash(f"Welcome Back, {user.username}!", "primary")
            session['username'] = username
            return redirect('/secret')
        else:
            form.username.errors = ['Invalid username or password.']

    return render_template('login.html', form=form)

# **GET */secret :*** Return the text “You made it!” (don’t worry, we’ll get rid of this soon)
@app.route('/secret', methods=['GET'])
def secret_page():
    if "username" not in session:
        flash("Please login first!", "danger")
        return redirect('/login')
    # form = TweetForm()
    # all_tweets = Tweet.query.all()
    # if form.validate_on_submit():
    #     text = form.text.data
    #     new_tweet = Tweet(text=text, user_id=session['user_id'])
    #     db.session.add(new_tweet)
    #     db.session.commit()
    #     flash('Tweet Created!', 'success')
    #     return redirect('/tweets')

    return render_template("secret.html")

@app.route('/logout') #SHOULD BE A POST ROUTE, NOT A GET ROUTE. POST IS BEST PRACTICE
def logout_user():
    session.pop('username')
    flash("You've been successfully logged out", "info")
    return redirect('/login')

# @app.route('/tweets', methods=['GET', 'POST'])
# def show_tweets():
#     if "user_id" not in session:
#         flash("Please login first!", "danger")
#         return redirect('/')
#     form = TweetForm()
#     all_tweets = Tweet.query.all()
#     if form.validate_on_submit():
#         text = form.text.data
#         new_tweet = Tweet(text=text, user_id=session['user_id'])
#         db.session.add(new_tweet)
#         db.session.commit()
#         flash('Tweet Created!', 'success')
#         return redirect('/tweets')

#     return render_template("tweets.html", form=form, tweets=all_tweets)


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


# @app.route('/login', methods=['GET', 'POST'])
# def login_user():
#     form = UserForm()
#     if form.validate_on_submit():
#         username = form.username.data
#         password = form.password.data

#         user = User.authenticate(username, password)
#         if user:
#             flash(f"Welcome Back, {user.username}!", "primary")
#             session['user_id'] = user.id
#             return redirect('/tweets')
#         else:
#             form.username.errors = ['Invalid username/password.']

#     return render_template('login.html', form=form)


# @app.route('/logout') #SHOULD BE A POST ROUTE, NOT A GET ROUTE. POST IS BEST PRACTICE
# def logout_user():
#     session.pop('user_id')
#     flash("Goodbye!", "info")
#     return redirect('/')
