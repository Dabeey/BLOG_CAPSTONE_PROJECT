from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, URL
from flask_ckeditor import CKEditor, CKEditorField


class RegisterForm(FlaskForm):
    name = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up!') # Register button


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Let Me In') # Login button


class CreatePostForm(FlaskForm):
    title = StringField("Blog Post Title", validators=[DataRequired()])
    subtitle = StringField("Subtitle", validators=[DataRequired()])
    author = StringField("Your Name", validators=[DataRequired()])
    img_url = StringField("Blog Image URL", validators=[DataRequired(), URL()])
    body = CKEditorField("Blog Content", validators=[DataRequired()])
    submit = SubmitField("Submit Post")


class CommentForm(FlaskForm):
    comment = CKEditorField('Comment    ', validators=[DataRequired()])
    submit = SubmitField('Submit Comment')
    


class ContactForm(FlaskForm):
    name = StringField('Your Name', 
                      validators=[DataRequired(), Length(min=2, max=50)],
                      render_kw={"placeholder": "John Doe"})
    
    email = StringField('Email',
                      validators=[DataRequired(), Email()],
                      render_kw={"placeholder": "your@email.com",
                               "type": "email"})
    
    message = TextAreaField('Message',
                          validators=[DataRequired(), Length(min=10)],
                          render_kw={"placeholder": "Your message...",
                                   "rows": 5})
    
    submit = SubmitField('Send Message')