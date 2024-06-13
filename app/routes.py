from . import app, db
from .models import User, Role, Book, Cover, Genre, Review
from .forms import LoginForm, AddBookForm, EditBookForm, RegisterForm, ReviewForm

from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from sqlalchemy import func
from markupsafe import Markup

import os
import hashlib
import bleach
import markdown


@app.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    books = Book.query.order_by(Book.year.desc()).paginate(page=page, per_page=10)
    
    book_avg_ratings = {}
    reviews_count = {}
    for book in books.items:
        avg_rating = db.session.query(func.avg(Review.rating)).filter(Review.book_id == book.id).scalar()
        book_avg_ratings[book.id] = round(avg_rating, 2) if avg_rating is not None else "No rating"
        reviews_count[book.id] = Review.query.filter(Review.book_id == book.id).count()
    
    return render_template('index.html', books=books, book_avg_ratings=book_avg_ratings, reviews_count=reviews_count)



@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password_hash, form.password.data):
            login_user(user, remember=form.remember_me.data)
            next_page = request.args.get('next', url_for('index'))
            return redirect(next_page)
        else:
            flash('Error while authentification with this log and pass', 'error')
    return render_template('login.html', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        existing_user = User.query.filter_by(username=form.username.data).first()
        if existing_user:
            flash('Username already exists. Please choose a different one', 'error')
            return redirect(url_for('register'))
        
        hashed_password = generate_password_hash(form.password.data)
        role_id = 3
        new_user = User(
            username=form.username.data,
            password_hash=hashed_password,
            last_name=form.last_name.data,
            first_name=form.first_name.data,
            middle_name=form.middle_name.data,
            role_id=role_id
        )

        db.session.add(new_user)
        db.session.commit()
        
        flash('Registration successful. You can now log in', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html', form=form)


@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    flash('Successfully logged out', 'success')
    return redirect(url_for('index'))


@app.route('/add_book', methods=['GET', 'POST'])
@login_required
def add_book():
    if current_user.role.name not in ['Администратор', 'Модератор']:
        flash('You do not have sufficient permissions for this action')
        return redirect(url_for('index'))
    
    form = AddBookForm()
    if form.validate_on_submit():
        try:
            cover = form.cover.data
            if cover:
                cover_filename = secure_filename(cover.filename)
                cover_path = os.path.join(app.config['UPLOAD_FOLDER'], cover_filename)
                
                cover_data = cover.read()
                cover_md5 = hashlib.md5(cover_data).hexdigest()
                cover.seek(0)

                existing_cover = Cover.query.filter_by(md5_hash=cover_md5).first()
                if existing_cover:
                    cover_id = existing_cover.id
                else:
                    cover.save(cover_path)
                    new_cover = Cover(filename=cover_filename, mime_type=cover.mimetype, md5_hash=cover_md5)
                    db.session.add(new_cover)
                    db.session.flush()  # Получить ID до фиксации
                    cover_id = new_cover.id
            else:
                flash('Cover was not loaded', 'error')
                return redirect(url_for('add_book'))

            sanitized_description = bleach.clean(form.description.data)
            new_book = Book(
                title=form.title.data,
                description=sanitized_description,
                year=form.year.data,
                publisher=form.publisher.data,
                author=form.author.data,
                pages=form.pages.data,
                cover_id=cover_id
            )

            genres = Genre.query.filter(Genre.id.in_(form.genres.data)).all()
            new_book.genres.extend(genres)
            db.session.add(new_book)
            db.session.commit()
            flash('The book was successfully added', 'success')
            return redirect(url_for('index'))
        except Exception as e:
            db.session.rollback()
            flash('Error while saving the book: ' + str(e), 'error')
            return redirect(url_for('add_book'))

    return render_template('add_edit_book.html', form=form, title="Добавить книгу", action_url=url_for('add_book'))


@app.route('/edit_book/<int:book_id>', methods=['GET', 'POST'])
@login_required
def edit_book(book_id):
    if current_user.role.name not in ['Администратор', 'Модератор']:
        flash('You do not have sufficient permissions for this action')
        return redirect(url_for('index'))
    
    book = Book.query.get_or_404(book_id)
    form = EditBookForm(obj=book)
    if form.validate_on_submit():
        try:
            book.title = form.title.data
            book.description = bleach.clean(form.description.data)
            book.year = form.year.data
            book.publisher = form.publisher.data
            book.author = form.author.data
            book.pages = form.pages.data

            genres = Genre.query.filter(Genre.id.in_(form.genres.data)).all()
            book.genres = genres

            db.session.commit()
            flash('The book was successfully edited', 'success')
            return redirect(url_for('view_book', book_id=book.id))
        except Exception as e:
            db.session.rollback()
            flash('Error while editing the book: ' + str(e), 'error')
            return redirect(url_for('edit_book', book_id=book.id))
    else:
        form.genres.data = [genre.id for genre in book.genres]
    
    return render_template('add_edit_book.html', form=form, title="Редактировать книгу", action_url=url_for('edit_book', book_id=book.id))


@app.route('/add_review/<int:book_id>', methods=['GET', 'POST'])
@login_required
def add_review(book_id):
    book = Book.query.get_or_404(book_id)
    if current_user.has_reviewed(book):
        flash('You have already written a review for this book', 'error')
        return redirect(url_for('view_book', book_id=book_id))

    form = ReviewForm()
    if form.validate_on_submit():
        sanitized_text = bleach.clean(form.text.data)
        new_review = Review(
            book_id=book.id,
            user_id=current_user.id,
            rating=int(form.rating.data),
            text=sanitized_text
        )
        db.session.add(new_review)
        db.session.commit()
        flash('Review was successfully uploaded', 'success')
        return redirect(url_for('view_book', book_id=book_id))

    return render_template('review_form.html', form=form, book=book)


@app.route('/view_book/<int:book_id>')
def view_book(book_id):
    book = Book.query.get_or_404(book_id)
    cover = Cover.query.get(book.cover_id)
    user_review = None
    if current_user.is_authenticated:
        user_review = Review.query.filter_by(user_id=current_user.id, book_id=book.id).first()
    
    reviews = Review.query.filter_by(book_id=book.id).all()
    reviews_count = len(reviews)  
    reviews = [
        {
            'username': User.query.get(review.user_id).username,
            'rating': review.rating,
            'text': Markup(markdown.markdown(review.text)),
            'date_added': review.date_added
        } for review in reviews
    ]
    return render_template('view_book.html', book=book, cover=cover, user_review=user_review, reviews=reviews, reviews_count=reviews_count)


@app.route('/delete_book/<int:book_id>', methods=['POST'])
@login_required
def delete_book(book_id):
    if current_user.role.name not in ['Администратор', 'Модератор']:
        flash('You do not have sufficient permissions for this action')
        return redirect(url_for('index'))

    if request.json and request.json.get('_method') == 'DELETE':
        try:
            book = Book.query.get_or_404(book_id)

            cover = Cover.query.get(book.cover_id)
            if cover:
                cover_path = os.path.join(app.config['UPLOAD_FOLDER'], cover.filename)
                if os.path.exists(cover_path):
                    os.remove(cover_path)
                db.session.delete(cover)

            db.session.delete(book)
            db.session.commit()
            flash('Book was successfully deleted', 'success')
        except Exception as e:
            db.session.rollback()
            flash('Error while deleting the book: ' + str(e), 'error')
    return redirect(url_for('index'))

@app.route('/about')
def about():
    return render_template('about.html')