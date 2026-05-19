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
    items = db.session.scalars(sa.select(Inventory)).all()
    return render_template('inventory.html', items=items)

@app.route('/menu')
@login_required
def menu():
    menus = db.session.scalars(sa.select(Menu)).all()
    return render_template('menu.html', menus=menus)

@app.route('/inventory/add', methods=['GET', 'POST'])
@login_required
def add_inventory():
    if request.method == 'POST':
        item = Inventory(
            kode_barang = request.form['kode_barang'],
            nama_barang = request.form['nama_barang'],
            kategori = request.form['kategori'],
            satuan = request.form['satuan'],
            qty = request.form['qty'],
            harga_beli = request.form['harga_beli'] or None,
            harga_jual = request.form['harga_jual'] or None,
            keterangan = request.form['keterangan'] or None,
        )
        db.session.add(item)
        db.session.commit()
        flash('Item sudah ditambahkan!')
        return redirect(url_for('inventory'))
    return render_template('add_inventory.html')

@app.route('/inventory/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_inventory(id):
    item = db.session.get(Inventory, id)
    if item is None:
        flash('Item tidak ada!')
        return redirect(url_for('inventory'))
    if request.method == 'POST':
        item.kode_barang = request.form['kode_barang']
        item.nama_barang = request.form['nama_barang']
        item.kategori = request.form['kategori'] or None
        item.satuan = request.form['satuan'] or None
        item.qty = request.form['qty']
        item.harga_beli = request.form['harga_beli'] or None
        item.harga_jual = request.form['harga_jual'] or None
        item.keterangan = request.form['keterangan'] or None
        db.session.commit()
        flash('Item berhasil diupdate!')
        return redirect(url_for('inventory'))
    return render_template('edit_inventory.html', item=item)

@app.route('/inventory/delete/<int:id>')
@login_required
def delete_inventory(id):
    item = db.session.get(Inventory, id)
    if item is None:
        flash('Item tidak ditemukan!')
        return redirect(url_for('inventory'))
    db.session.delete(item)
    db.session.commit()
    flash('Item telah berhasil dihapus!')
    return redirect(url_for('inventory'))

@app.route('/menu/add', methods=['GET', 'POST'])
@login_required
def add_menu():
    if request.method == 'POST':
        m = Menu(
            nama_menu = request.form['nama_menu'],
            harga = request.form['harga'],
            deskripsi = request.form['deskripsi'] or None,
        ) 
        db.session.add(m)
        db.session.commit()
        flash('Menu berhasil ditambahkan!')
        return redirect(url_for('menu'))
    return render_template('add_menu.html')

@app.route('/menu/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_menu(id):
    m = db.session.get(Menu, id)
    if m is None:
        flash('Menu tidak ditemukan!')
        return redirect(url_for('menu'))
    if request.method == 'POST':
        print(request.form)
        m.nama_menu = request.form['nama_menu']
        m.harga = request.form['harga']
        m.deskripsi = request.form['deskripsi'] or None
        db.session.commit()
        flash('Menu berhasil diupdate!')
        return redirect(url_for('menu'))
    return render_template('edit_menu.html', menu=m)

@app.route('/menu/delete/<int:id>')
@login_required
def delete_menu(id):
    m = db.session.get(Menu,id)
    if m is None:
        flash('Menu tidak ditemukan!')
        return redirect(url_for('menu'))
    db.session.delete(m)
    db.session.commit()
    flash('Menu berhasil dihapus!')
    return redirect(url_for('menu'))

@app.route('/menu/<int:menu_id>/recipe')
@login_required
def recipe(menu_id):
    return "coming soon"
