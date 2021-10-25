from flask_wtf import FlaskForm, validators
from wtforms import StringField
from flaskChat.models import User
from wtforms.fields.simple import PasswordField, StringField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError



class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember me')
    submit = SubmitField('log in')


class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(max=60)])
    email = StringField('Email', validators=[DataRequired(), Length(max=180), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(max=60)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), Length(max=60), EqualTo('password')])
    submit = SubmitField('register me')

    
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username already exists. Try a different one.')


    def validate_email(self, email):
        email = User.query.filter_by(email=email.data).first()
        if email:
            raise ValidationError('Already is an user using this email.')



class ResetRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('reset request')


    def validate_email(self, email):
        email = User.query.filter_by(email=email.data).first()
        if not email:
            raise ValidationError('There is no user with that email.')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('New Password', validators=[DataRequired(), Length(max=60)])
    confirm_password = PasswordField('Confirm New Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('reset password')
    