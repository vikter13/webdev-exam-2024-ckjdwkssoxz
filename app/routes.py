from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user, login_required
from . import app, db
from .models import User, Role, Book, Cover, Genre, Review
from .forms import LoginForm, AddBookForm, EditBookForm, RegisterForm
from werkzeug.security import generate_password_hash, check_password_hash
import os
import hashlib
from werkzeug.utils import secure_filename
import bleach

@app.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    books = Book.query.order_by(Book.year.desc()).paginate(page=page, per_page=10)
    return render_template('index.html', books=books)

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
            flash('Invalid username or password.', 'error')
    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        existing_user = User.query.filter_by(username=form.username.data).first()
        if existing_user:
            flash('Username already exists. Please choose a different one.', 'error')
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
        
        flash('Registration successful. You can now log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html', form=form)

@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/add_book', methods=['GET', 'POST'])
@login_required
def add_book():
    if current_user.role.name not in ['Администратор', 'Модератор']:
        flash('У вас недостаточно прав для выполнения данного действия.')
        return redirect(url_for('index'))
    form = AddBookForm()
    if form.validate_on_submit():
        cover = form.cover.data
        if cover:
            cover_filename = secure_filename(cover.filename)
            cover_path = os.path.join(app.config['UPLOAD_FOLDER'], cover_filename)
            
            print(f"Uploaded file: {cover_filename}")
            print(f"Upload path: {cover_path}")

            cover_data = cover.read()
            cover_md5 = hashlib.md5(cover_data).hexdigest()
            print(f"MD5 hash: {cover_md5}")

            cover.seek(0)

            existing_cover = Cover.query.filter_by(md5_hash=cover_md5).first()
            if existing_cover:
                cover_id = existing_cover.id
            else:
                try:
                    cover.save(cover_path)
                    print(f"File saved to: {cover_path}")  
                    new_cover = Cover(filename=cover_filename, mime_type=cover.mimetype, md5_hash=cover_md5)
                    db.session.add(new_cover)
                    db.session.flush()
                    cover_id = new_cover.id
                except Exception as e:
                    flash('Ошибка при сохранении обложки: ' + str(e), 'error')
                    return redirect(url_for('add_book'))
        else:
            flash('Обложка не загружена', 'error')
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
        print(f"File content length: {len(cover_data)}")
        genres = Genre.query.filter(Genre.id.in_(form.genres.data)).all()
        new_book.genres.extend(genres)
        db.session.add(new_book)
        db.session.commit()
        flash('Книга успешно добавлена!')
        return redirect(url_for('index'))
    return render_template('add_edit_book.html', form=form, title="Добавить книгу", action_url=url_for('add_book'))

@app.route('/edit_book/<int:book_id>', methods=['GET', 'POST'])
@login_required
def edit_book(book_id):
    if current_user.role.name not in ['Администратор', 'Модератор']:
        flash('У вас недостаточно прав для выполнения данного действия.')
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
            flash('Книга успешно обновлена!')
            return redirect(url_for('view_book', book_id=book.id))
        except Exception as e:
            db.session.rollback()
            flash('При сохранении данных возникла ошибка. Проверьте корректность введённых данных.', 'error')
            print(e)
    else:
        form.genres.data = [genre.id for genre in book.genres]
    return render_template('add_edit_book.html', form=form, title="Редактировать книгу", action_url=url_for('edit_book', book_id=book.id))

@app.route('/view_book/<int:book_id>')
def view_book(book_id):
    book = Book.query.get_or_404(book_id)
    cover = Cover.query.get(book.cover_id)
    print("Cover filename:", cover.filename)
    return render_template('view_book.html', book=book, cover=cover)

@app.route('/delete_book/<int:book_id>', methods=['POST'])
@login_required
def delete_book(book_id):
    if current_user.role.name not in ['Администратор', 'Модератор']:
        flash('У вас недостаточно прав для выполнения данного действия.')
        return redirect(url_for('index'))

    if request.json and request.json.get('_method') == 'DELETE':
        book = Book.query.get_or_404(book_id)

        cover = Cover.query.get(book.cover_id)
        if cover:
            cover_path = os.path.join(app.config['UPLOAD_FOLDER'], cover.filename)
            if os.path.exists(cover_path):
                os.remove(cover_path)
            db.session.delete(cover)

        db.session.delete(book)
        db.session.commit()

        flash('Книга успешно удалена!', 'success')
        return '', 204  

    flash('Ошибка при удалении книги.', 'error')
    return redirect(url_for('index'))

