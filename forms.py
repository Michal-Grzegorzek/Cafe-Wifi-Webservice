from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField, IntegerField, FloatField, DecimalField
from wtforms.validators import DataRequired, URL, NumberRange, Email, EqualTo, Length
from flask_ckeditor import CKEditorField


class MyFloatField(FloatField):
    def process_formdata(self, valuelist):
        if valuelist:
            try:
                self.data = float(valuelist[0].replace(',', '.'))
                self.data = round(self.data, 2)
            except ValueError:
                self.data = None
                raise ValueError(self.gettext('Not a valid float value'))


class MyEmailField(StringField):
    def process_formdata(self, valuelist):
        if valuelist:
            self.data = valuelist[0].lower()
            self.data = self.data.strip()


# #WTForm

class Cafe(FlaskForm):
    name = StringField("Name of the cafe", validators=[DataRequired()])
    map_url = StringField("Google Maps URL", validators=[DataRequired(), URL()])
    img_url = StringField("Cafe Image URL", validators=[DataRequired(), URL()])
    location = StringField("Cafe Location", validators=[DataRequired()])
    # coffee_price = FloatField("Cafe Price in €", validators=[DataRequired(), NumberRange(min=0)])
    coffee_price = MyFloatField("Cafe Price in €", validators=[DataRequired(), NumberRange(min=0)])
    seats = IntegerField('How Many Seats?', validators=[DataRequired(), NumberRange(min=0)])
    has_toilet = BooleanField("Toilets?")
    has_wifi = BooleanField("WiFi?")
    has_sockets = BooleanField("Sockets?")
    can_take_calls = BooleanField("Call taking?")
    submit = SubmitField("Add Cafe")


class RegisterForm(FlaskForm):
    email = MyEmailField("Email",  validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6, max=16)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    name = StringField('Name', validators=[DataRequired(), Length(min=3, max=20)])
    submit = SubmitField('Sign Me Up!')


class LoginForm(FlaskForm):
    email = MyEmailField("Email",  validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Let Me In!')


class RateForm(FlaskForm):
    rate = IntegerField('Rate', validators=[DataRequired(), NumberRange(min=0, max=10)])
    submit = SubmitField('Add Rate!')