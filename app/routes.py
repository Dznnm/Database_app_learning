from flask import render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from datetime import datetime
from app import app, db
from app.models import User, Inventory, Menu, Recipe, Penjualan, ItemPenjualan
import sqlalchemy as sa
from app.forms import InventoryForm, MenuForm, SaleForm

@app.route('/')
@app.route('/dashboard')
@login_required
def dashboard():
    total_items = db.session.scalar(sa.select(sa.func.count()).select_from(Inventory))
    low_stock = db.session.scalars(sa.select(Inventory).where(Inventory.qty <= Inventory.stok_minimum)).all()
    total_menu = db.session.scalar(sa.select(sa.func.count()).select_from(Menu))
    sales = db.session.execute(sa.select(Penjualan).order_by(Penjualan.tanggal.desc()).limit(5)).scalars().all()
    return render_template('dashboard.html', 
                           total_items=total_items,
                           low_stock = low_stock,
                           total_menu = total_menu,
                           sales=sales
                           )                          


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
    form = InventoryForm()
    if form.validate_on_submit():
        existing = db.session.scalar(
            sa.select(Inventory).where(
                Inventory.kode_barang == form.kode_barang.data))
        if existing:
            form.kode_barang.errors.append('Kode barang sudah digunakan!')
            return render_template('add_inventory.html', form=form)
        
        item = Inventory(
            kode_barang=form.kode_barang.data,
            nama_barang=form.nama_barang.data,
            kategori=form.kategori.data,
            satuan=form.satuan.data,
            qty=form.qty.data,
            stok_minimum = form.stok_minimum.data or 0,
            keterangan=form.keterangan.data or None,
        )
        db.session.add(item)
        db.session.commit()
        flash('Item sudah ditambahkan!')
        return redirect(url_for('inventory'))
    return render_template('add_inventory.html', form=form)

@app.route('/inventory/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_inventory(id):
    item = db.session.get(Inventory, id)
    if item is None:
        flash('Item tidak ada!')
        return redirect(url_for('inventory'))
    form = InventoryForm(obj=item)
    if form.validate_on_submit():
        qty = form.qty.data
        existing = db.session.scalar(
            sa.select(Inventory).where(
                Inventory.kode_barang == form.kode_barang.data,
                Inventory.id != id ))
        if existing:
            form.kode_barang.errors.append('Kode barang sudah digunakan!')
            return render_template('edit_inventory.html', form=form, item=item)      
        item.kode_barang=form.kode_barang.data
        item.nama_barang=form.nama_barang.data
        item.kategori=form.kategori.data
        item.satuan=form.satuan.data
        item.qty=form.qty.data
        item.stok_minimum = form.stok_minimum.data or 0
        item.keterangan=form.keterangan.data or None
        db.session.commit()
        flash('Item sudah diupdate!')
        return redirect(url_for('inventory'))
    return render_template('edit_inventory.html', form=form, item=item)

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
    form = MenuForm()
    if form.validate_on_submit():
        m = Menu(
            nama_menu = form.nama_menu.data,
            harga = form.harga.data,
            deskripsi = form.deskripsi.data or None,
        ) 
        db.session.add(m)
        db.session.commit()
        flash('Menu berhasil ditambahkan!')
        return redirect(url_for('menu'))
    return render_template('add_menu.html', form=form)

@app.route('/menu/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_menu(id):
    m = db.session.get(Menu, id)
    if m is None:
        flash('Menu tidak ditemukan!')
        return redirect(url_for('menu'))
    form = MenuForm(obj=m)
    if form.validate_on_submit():
        m.nama_menu = form.nama_menu.data
        m.harga = form.harga.data
        m.deskripsi = form.deskripsi.data or None
        db.session.commit()
        flash('Menu berhasil diupdate!')
        return redirect(url_for('menu'))
    return render_template('edit_menu.html', form=form)

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

    menu = Menu.query.get_or_404(menu_id)

    recipes = Recipe.query.filter_by(
        menu_id=menu_id
    ).all()

    return render_template(
        'recipe.html',
        menu=menu,
        recipes=recipes
    )

@app.route('/menu/<int:menu_id>/recipe/add',
           methods=['GET', 'POST'])
@login_required
def add_recipe(menu_id):

    menu = Menu.query.get_or_404(menu_id)

    inventories = Inventory.query.all()

    if request.method == 'POST':

        recipe = Recipe(
            menu_id=menu_id,
            inventory_id=request.form['inventory_id'],
            jumlah=request.form['jumlah']
        )

        db.session.add(recipe)
        db.session.commit()

        flash('Resep berhasil ditambahkan')

        return redirect(
            url_for('recipe', menu_id=menu_id)
        )

    return render_template(
        'add_recipe.html',
        menu=menu,
        inventories=inventories
    )

@app.route('/recipe/delete/<int:id>')
@login_required
def delete_recipe(id):

    recipe = Recipe.query.get_or_404(id)

    menu_id = recipe.menu_id

    db.session.delete(recipe)
    db.session.commit()

    flash('Resep berhasil dihapus')

    return redirect(
        url_for('recipe', menu_id=menu_id)
    )

@app.route('/sales')
@login_required
def sales():
    penjualan = db.session.scalars(
        sa.select(Penjualan).order_by(Penjualan.tanggal.desc())).all()
    return render_template('sales.html', penjualan=penjualan)

@app.route('/sales/add', methods=['GET', 'POST'])
@login_required
def add_sale():
    form = SaleForm()
    if form.validate_on_submit():
        p = Penjualan(
            tanggal=datetime.now(),
            catatan=form.catatan.data or None  # ← ambil dari form
        )
        db.session.add(p)
        db.session.flush()

        menus = request.form.getlist('menu_id')
        jumlah = request.form.getlist('jumlah')

        for menu_id, jum in zip(menus, jumlah):
            if menu_id and jum and int(jum) > 0:
                recipes = db.session.scalars(
                    sa.select(Recipe).where(Recipe.menu_id == int(menu_id))).all()
        
                if not recipes:
                    menu_nama = db.session.get(Menu, int(menu_id)).nama_menu
                    db.session.rollback()
                    flash(f'Menu "{menu_nama}" belum mempunyai resep, tidak dapat diinput!')
                    return redirect(url_for('add_sale'))
                
                item = ItemPenjualan(
                    penjualan_id=p.id,
                    menu_id=int(menu_id),
                    jumlah=int(jum)
                )
                db.session.add(item)

                for recipe in recipes:
                    bahan = db.session.get(Inventory, recipe.inventory_id)
                    if bahan:
                        kebutuhan = recipe.jumlah * int(jum)
                        bahan.qty = bahan.qty - kebutuhan
                        if bahan.qty < 0:
                            flash(
                                f'⚠ Stok {bahan.nama_barang} minus {abs(bahan.qty):g} {bahan.satuan}. '
                                f'Order tetap disimpan, segera lakukan stock adjustment.',
                                'warning'
                            )
                        elif bahan.qty <= bahan.stok_minimum:
                            flash(f'{bahan.nama_barang}: sisa {bahan.qty:g} {bahan.satuan} — stok menipis!', 'warning')
                        else:
                            flash(f'✓ {bahan.nama_barang}: sisa {bahan.qty:g} {bahan.satuan}', 'info')

        db.session.commit()
        flash('Rekapan telah disimpan dan stok telah diupdate!')
            
        return redirect(url_for('sales'))

    menus = db.session.scalars(sa.select(Menu)).all()
    return render_template('add_sale.html', menus=menus, form=form)

@app.route('/sales/<int:id>')
@login_required
def sale_detail(id):
    p = db.session.get(Penjualan, id)
    if p is None:
        flash('Data tidak ditemukan!')
        return redirect(url_for('sales'))
    items = db.session.scalars(
        sa.select(ItemPenjualan).where(ItemPenjualan.penjualan_id == id)).all()
    return render_template('sales_detail.html', penjualan=p, items=items)

@app.route('/sales/delete/<int:id>')
@login_required
def delete_sale(id):
    p = db.session.get(Penjualan, id)
    if p is None:
        flash('Data tidak ditemukan!')
        return redirect(url_for('sales'))
    db.session.delete(p)
    db.session.commit()
    flash('Rekap penjualan telah dihapus!')
    return redirect(url_for('sales'))