from flask import render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from app import app, db
from app.models import User, Inventory, Menu, Recipe
import sqlalchemy as sa

@app.route('/')
@app.route('/dashboard')
@login_required
def dashboard():
    total_items = db.session.scalar(sa.select(sa.func.count()).select_from(Inventory))
    low_stock = db.session.scalars(sa.select(Inventory).where(Inventory.qty <= 5)).all()
    total_menu = db.session.scalar(sa.select(sa.func.count()).select_from(Menu))
    return render_template('dashboard.html', 
                           total_items=total_items,
                           low_stock = low_stock,
                           total_menu = total_menu)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = db.session.scalar(sa.select(User).where(User.username == username))
        if user is None or not user.check_password(password):
            flash('Username atau Password salah!')
            return redirect(url_for('login'))
        login_user(user)
        return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        token = request.form['token']
        if token != app.config['REGISTER_TOKEN']:
            flash('Token salah!')
            return redirect(url_for('register'))
        username = request.form['username']
        password = request.form['password']
        existing_user = db.session.scalar(sa.select(User).where(User.username))
        if existing_user:
            flash('Username sudah terpakai, silahkan menggunakan yang lain')
            return redirect(url_for('register'))
        user = User(username=username)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash ('Registrasi berhasil!')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/inventory')
@login_required
def inventory():
    return "inventory page - coming soon"

@app.route('/menu')
@login_required
def menu():
    return "menu page - coming soon"
