from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, FileField  
from wtforms.validators import DataRequired, Length, EqualTo
from wtforms.fields import SelectMultipleField, IntegerField  
from flask_wtf.file import FileAllowed
from wtforms.widgets import ListWidget, CheckboxInput
from .models import Genre

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=150)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6, max=256)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(min=2, max=150)])
    first_name = StringField('First Name', validators=[DataRequired(), Length(min=2, max=150)])
    middle_name = StringField('Middle Name', validators=[Length(max=150)])
    submit = SubmitField('Register')

class BookForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    year = StringField('Year', validators=[DataRequired()])
    publisher = StringField('Publisher', validators=[DataRequired()])
    author = StringField('Author', validators=[DataRequired()])
    pages = StringField('Pages', validators=[DataRequired()])
    genres = SelectMultipleField('Genres', validators=[DataRequired()])
    submit = SubmitField('Submit')

class AddBookForm(BookForm):
    cover = FileField('Cover', validators=[FileAllowed(['jpg', 'png'], 'Images only!')])
    genres = SelectMultipleField('Genres', validators=[Length(min=1, message='Please select at least one genre.')], widget=ListWidget(prefix_label=False), option_widget=CheckboxInput())

    def __init__(self, *args, **kwargs):
        super(AddBookForm, self).__init__(*args, **kwargs)
        self.genres.choices = [(genre.id, genre.name) for genre in Genre.query.all()]


class EditBookForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(max=200)])
    description = TextAreaField('Description', validators=[DataRequired()])
    year = IntegerField('Year', validators=[DataRequired()])
    publisher = StringField('Publisher', validators=[DataRequired(), Length(max=200)])
    author = StringField('Author', validators=[DataRequired(), Length(max=200)])
    pages = IntegerField('Pages', validators=[DataRequired()])
    genres = SelectMultipleField('Genres', coerce=int, validators=[DataRequired()], widget=ListWidget(prefix_label=False), option_widget=CheckboxInput())
    submit = SubmitField('Submit')

    def __init__(self, *args, **kwargs):
        super(EditBookForm, self).__init__(*args, **kwargs)
        self.genres.choices = [(genre.id, genre.name) for genre in Genre.query.all()]