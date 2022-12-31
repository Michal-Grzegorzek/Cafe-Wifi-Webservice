import werkzeug
from functools import wraps
from flask import g, request, redirect, url_for
from flask import Flask, render_template, redirect, url_for, flash, request, abort
from flask_bootstrap import Bootstrap
from flask_ckeditor import CKEditor
from datetime import date
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from forms import Cafe, RegisterForm, LoginForm, RateForm
from sqlalchemy.dialects.mysql import FLOAT
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
# app.config['SECRET_KEY'] = 'secret'
Bootstrap(app)
login_manager = LoginManager()
login_manager.init_app(app)


##CONNECT TO DB
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL",  "sqlite:///cafes.db")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


def admin_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.id != 1:
            return abort(403)
        return f(*args, **kwargs)
    return decorated_function

##CONFIGURE TABLES

class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))

    cafes = relationship("AllCafes", back_populates="author")
    rev_cafe = relationship("Reviews", back_populates="author")


class AllCafes(db.Model):
    __tablename__ = "all_cafes"
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    author = relationship("User", back_populates="cafes")
    id_cafe = relationship("Reviews", back_populates="caffe_review")
    name = db.Column(db.String(250), unique=True, nullable=True)
    map_url = db.Column(db.String(500), nullable=True)
    img_url = db.Column(db.String(500), nullable=True)
    location = db.Column(db.String(250), nullable=True)
    seats = db.Column(db.String(250), nullable=True)
    has_toilet = db.Column(db.Boolean, nullable=True)
    has_wifi = db.Column(db.Boolean, nullable=True)
    has_sockets = db.Column(db.Boolean, nullable=True)
    can_take_calls = db.Column(db.Boolean, nullable=True)
    coffee_price = db.Column(db.String(250), nullable=True)
    avg_review = db.Column(FLOAT(unsigned=True))


class Reviews(db.Model):
    __tablename__ = "all_reviews"
    id = db.Column(db.Integer, primary_key=True)
    cafe_id = db.Column(db.Integer, db.ForeignKey('all_cafes.id'))
    caffe_review = relationship("AllCafes", back_populates="id_cafe")

    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    author = relationship("User", back_populates="rev_cafe")
    rate = db.Column(db.Integer)



# db.create_all()


@app.route('/')
@app.route('/home')
def home():
    cafes = AllCafes.query.all()
    reviews = Reviews.query.all()
    condition = request.args.get('condition')

    return render_template("index.html", condition=condition, all_cafes=cafes, all_reviews=reviews, title="Home Page")


@login_required
@app.route('/cafes-added-by-you')
def cafes_added_by_you():
    if not current_user.is_authenticated:
        flash("You need to login or register to use this tab.")
        return redirect(url_for("login"))

    cafes = AllCafes.query.all()
    reviews = Reviews.query.all()
    return render_template("cafes-added-by-you.html", all_cafes=cafes, all_reviews=reviews, title="Added By You")


@app.route('/register', methods=["POST", "GET"])
def register():
    form = RegisterForm()

    if form.validate_on_submit():
        if User.query.filter_by(email=form.email.data).first():
            flash("You've already signed up with that email, log in instead!")
            return redirect(url_for('login'))

        password_after_hashed = werkzeug.security.generate_password_hash(password=form.password.data,
                                                                             method='pbkdf2:sha256', salt_length=8)
        new_user = User(
            email=form.email.data,
            password=password_after_hashed,
            name=form.name.data
            )
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for("home"))

    return render_template("register.html", form=form, title="Register Page")


@app.route('/login', methods=["POST", "GET"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if request.method == "POST":
        email = form.email.data
        password = form.password.data

        user = User.query.filter_by(email=email).first()
        if not user:
            flash("That email does not exist, please try again.")
            return redirect(url_for('login'))
        if werkzeug.security.check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for("home"))
        else:
            flash("Password incorrect, try again.")
            return redirect(url_for('login'))

    return render_template("login.html", form=form, title="Login Page")


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route("/add-cafe", methods=["POST", "GET"])
def add_new_cafe():
    if not current_user.is_authenticated:
        flash("You need to login or register to adding new cafe.")
        return redirect(url_for("login"))
    form = Cafe()
    if form.validate_on_submit():
        new_cafe = AllCafes(
            name=form.name.data,
            author_id=current_user.id,
            map_url=form.map_url.data,
            img_url=form.img_url.data,
            location=form.location.data,
            seats=form.seats.data,
            has_toilet=form.has_toilet.data,
            has_wifi=form.has_wifi.data,
            has_sockets=form.has_sockets.data,
            can_take_calls=form.can_take_calls.data,
            coffee_price=form.coffee_price.data,
        )

        db.session.add(new_cafe)
        db.session.commit()
        conditionn = "true"
        return redirect(url_for("home", condition=conditionn))
    return render_template("add-cafe.html", form=form, title="Add Cafe")


@app.route("/review/<int:cafe_id>", methods=["POST", "GET"])
def review(cafe_id):
    form = RateForm()
    requested_cafe = AllCafes.query.get(cafe_id)
    requested_review = Reviews.query.get(cafe_id)

    rev_list_to_check = Reviews.query.filter_by(cafe_id=cafe_id).all()

    if form.validate_on_submit():
        if not current_user.is_authenticated:
            flash("You need to login or register to add review.")
            return redirect(url_for("login"))

        for i in rev_list_to_check:
            if i.author_id == current_user.id:
                return redirect(url_for("logout"))

        new_review = Reviews(
            cafe_id=cafe_id,
            author_id=current_user.id,
            rate=form.rate.data
        )

        db.session.add(new_review)

        list_reviews = Reviews.query.filter_by(cafe_id=cafe_id).all()
        count_reviews = 0
        sum_reviews = 0

        for i in list_reviews:
            sum_reviews += i.rate
            count_reviews += 1
        requested_cafe.avg_review = round((sum_reviews/count_reviews), 1)
        db.session.commit()
        conditionn = "true"
        return redirect(url_for("home", condition=conditionn))
    return render_template("review.html", title="Add Review",
                           cafes=requested_cafe, form=form)


@app.route("/delete-cafe/<int:cafe_id>", methods=["POST", "GET"])
def delete_cafe(cafe_id):
    if not current_user.is_authenticated:
        flash("You need to login or register to delete a cafe.")
        return redirect(url_for("login"))

    cafe_to_delete = AllCafes.query.get(cafe_id)
    db.session.delete(cafe_to_delete)
    db.session.commit()

    return redirect(url_for("cafes_added_by_you"))

if __name__ == "__main__":
    app.run(debug=True)
