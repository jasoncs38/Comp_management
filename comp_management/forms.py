from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed,FileField
from wtforms_sqlalchemy.fields import QuerySelectField
from wtforms import StringField,PasswordField,SubmitField,BooleanField,TextAreaField
from wtforms.validators import DataRequired,Length,Email,EqualTo,ValidationError,Optional
from comp_management.models import Category,User
from flask_login import current_user


def get_categories():
    return Category.query.all()

class RegistrationForm(FlaskForm):
    username=StringField('Username',validators=[DataRequired(),Length(min=2,max=30)])
    email=StringField('Email',validators=[DataRequired(),Email(),Length(min=2,max=120)])
    password=PasswordField('Password',validators=[DataRequired(),Length(min=2,max=20)])
    confirm_password=PasswordField('Confirm Password',validators=[DataRequired(),EqualTo('password')])
    submit=SubmitField('Sign Up')

    def validate_username(self,username):
        user=User.query.filter_by(username=username.data).first()
        if user:
         raise ValidationError('This Username is taken. Please choose different one.')

    def validate_email(self,email):
        user=User.query.filter_by(email=email.data).first()
        if user:
         raise ValidationError('This Email is taken. Please choose different one.')

class LoginForm(FlaskForm):
    email=StringField('Email',validators=[DataRequired(),Email(),Length(max=120)])
    password=PasswordField('Password',validators=[DataRequired(),Length(min=2,max=20)])
    remember=BooleanField('Remember me')
    submit=SubmitField('Sign In')

class UpdateAccountForm(FlaskForm):
    username=StringField('Username',validators=[DataRequired(),Length(min=2,max=20)])
    email=StringField('Email',validators=[DataRequired(),Email()])
    password = PasswordField('Password',validators=[Optional(), Length(min=2, max=20)])
    confirm_password = PasswordField('Confirm Password',validators=[Optional(), EqualTo('password', message='Passwords must match.')])
    submit=SubmitField('Update')

    def validate_username(self,username):
        if username.data!=current_user.username:
            user=User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('This Username is already taken.Please choose a different one.')

    def validate_email(self,email):
        if email.data!=current_user.email:
            user=User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('This Email is already taken.Please choose a different one.')

class ComplaintForm(FlaskForm):
    title=StringField('Title',validators=[DataRequired()])
    content=TextAreaField('Content',validators=[DataRequired()])
    category=QuerySelectField('Category',query_factory=get_categories,
                              get_label='name',validators=[DataRequired()])
    image=FileField('Upload Image(optional)',validators=[FileAllowed(['jpg','png'])])
    submit=SubmitField('Sumbit')

class ResponseForm(FlaskForm):
   content=TextAreaField('Content',validators=[DataRequired()])
   submit=SubmitField('Sumbit')

class ResolveForm(FlaskForm):
    submit = SubmitField('Mark as Resolved')

class CategoryForm(FlaskForm):
   name=StringField('Name',validators=[DataRequired()])
   submit = SubmitField('Save')