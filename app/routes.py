from flask import (render_template, redirect, url_for, request, flash)
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
    total_items = db.session.scalar(
        sa.select(sa.func.count()).select_from(Inventory)
    )
    low_stock = db.session.scalars(
        sa.select(Inventory).where(Inventory.qty <= Inventory.stok_minimum)
    ).all()
    total_menu = db.session.scalar(
        sa.select(sa.func.count()).select_from(Menu)
    )
    sales = db.session.execute(
        sa.select(Penjualan).order_by(Penjualan.tanggal.desc()).limit(5)
    ).scalars().all()

    out_of_stock = []
    all_menus = db.session.scalars(sa.select(Menu)).all()
    for menu in all_menus:
        recipes = db.session.scalars(
            sa.select(Recipe).where(Recipe.menu_id == menu.id)
        ).all()
        for recipe in recipes:
            bahan = db.session.get(Inventory, recipe.inventory_id)
            if bahan and bahan.qty <= 0:
                out_of_stock.append(menu)
                break

    return render_template(
        'dashboard.html',
        total_items=total_items,
        low_stock=low_stock,
        total_menu=total_menu,
        sales=sales,
        out_of_stock=out_of_stock,
    )


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = db.session.scalar(
            sa.select(User).where(User.username == username)
        )
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
        existing_user = db.session.scalar(
            sa.select(User).where(User.username == username)
        )
        if existing_user:
            flash(
                'Username sudah terpakai, silahkan menggunakan yang lain'
            )
            return redirect(url_for('register'))
        user = User(username=username)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash('Registrasi berhasil!')
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
                Inventory.kode_barang == form.kode_barang.data
            )
        )
        if existing:
            form.kode_barang.errors.append('Kode barang sudah digunakan!')
            return render_template('add_inventory.html', form=form)

        item = Inventory(
            kode_barang=form.kode_barang.data,
            nama_barang=form.nama_barang.data,
            kategori=form.kategori.data,
            satuan=form.satuan.data,
            qty=form.qty.data,
            stok_minimum=form.stok_minimum.data or 0,
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
        existing = db.session.scalar(
            sa.select(Inventory).where(
                Inventory.kode_barang == form.kode_barang.data,
                Inventory.id != id,
            )
        )
        if existing:
            form.kode_barang.errors.append('Kode barang sudah digunakan!')
            return render_template('edit_inventory.html', form=form, item=item)
        item.nama_barang = form.nama_barang.data
        item.kategori = form.kategori.data
        item.satuan = form.satuan.data
        item.qty = form.qty.data
        item.stok_minimum = form.stok_minimum.data or 0
        item.keterangan = form.keterangan.data or None
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

    used_in_sale = db.session.scalar(
        sa.select(
            sa.select(ItemPenjualan)
            .join(Recipe, Recipe.id == ItemPenjualan.menu_id)
            .where(Recipe.inventory_id == id)
            .limit(1)
            .subquery()
        ).limit(1)
    )
    if used_in_sale:
        flash(
            f'{item.nama_barang} tidak dapat dihapus '
            f'karena sudah ada data penjualan terkait.',
            'danger',
        )
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
            nama_menu=form.nama_menu.data,
            harga=form.harga.data,
            deskripsi=form.deskripsi.data or None,
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
    m = db.session.get(Menu, id)
    if m is None:
        flash('Menu tidak ditemukan!')
        return redirect(url_for('menu'))

    existing_sale = db.session.scalar(
        sa.select(ItemPenjualan).where(ItemPenjualan.menu_id == id).limit(1)
    )
    if existing_sale:
        flash(
            f'Menu "{m.nama_menu}" tidak dapat dihapus karena sudah ada '
            f'data penjualan. Kamu bisa menonaktifkannya dengan mengubah namanya.',
            'danger',
        )
        return redirect(url_for('menu'))

    db.session.delete(m)
    db.session.commit()
    flash('Menu berhasil dihapus!')
    return redirect(url_for('menu'))


@app.route('/menu/<int:menu_id>/recipe')
@login_required
def recipe(menu_id):
    menu = db.session.get(Menu, menu_id)
    if menu is None:
        flash('Menu tidak ditemukan!')
        return redirect(url_for('menu'))
    recipes = db.session.scalars(
        sa.select(Recipe).where(Recipe.menu_id == menu_id)
    ).all()
    return render_template('recipe.html', menu=menu, recipes=recipes)


@app.route('/menu/<int:menu_id>/recipe/add', methods=['GET', 'POST'])
@login_required
def add_recipe(menu_id):
    menu = db.session.get(Menu, menu_id)
    if menu is None:
        flash('Menu tidak ditemukan!')
        return redirect(url_for('menu'))
    inventories = db.session.scalars(sa.select(Inventory)).all()
    if request.method == 'POST':
        recipe = Recipe(
            menu_id=menu_id,
            inventory_id=request.form['inventory_id'],
            jumlah=request.form['jumlah'],
        )
        db.session.add(recipe)
        db.session.commit()
        flash('Resep berhasil ditambahkan')
        return redirect(url_for('recipe', menu_id=menu_id))
    return render_template(
        'add_recipe.html', menu=menu, inventories=inventories
    )


@app.route('/recipe/delete/<int:id>')
@login_required
def delete_recipe(id):
    recipe = db.session.get(Recipe, id)
    if recipe is None:
        flash('Resep tidak ditemukan!')
        return redirect(url_for('menu'))
    menu_id = recipe.menu_id
    db.session.delete(recipe)
    db.session.commit()
    flash('Resep berhasil dihapus')
    return redirect(url_for('recipe', menu_id=menu_id))


@app.route('/sales')
@login_required
def sales():
    penjualan = db.session.scalars(
        sa.select(Penjualan).order_by(Penjualan.tanggal.desc())
    ).all()
    return render_template('sales.html', penjualan=penjualan)


@app.route('/sales/add', methods=['GET', 'POST'])
@login_required
def add_sale():
    form = SaleForm()
    menus = db.session.scalars(sa.select(Menu)).all()

    def process_sale(menus_form, jumlah):
        """Proses penyimpanan penjualan dan pengurangan stok."""
        p = Penjualan(
            tanggal=datetime.now(), catatan=form.catatan.data or None
        )
        db.session.add(p)
        db.session.flush()

        for menu_id, jum in zip(menus_form, jumlah):
            if menu_id and jum and int(jum) > 0:
                recipes = db.session.scalars(
                    sa.select(Recipe).where(Recipe.menu_id == int(menu_id))
                ).all()

                if not recipes:
                    menu_obj = db.session.get(Menu, int(menu_id))
                    db.session.rollback()
                    flash(
                        f'Menu "{menu_obj.nama_menu if menu_obj else "???"}'
                        f' belum mempunyai resep, '
                        f'tidak dapat diinput!'
                    )
                    return redirect(url_for('add_sale'))

                menu_obj = db.session.get(Menu, int(menu_id))
                item = ItemPenjualan(
                    penjualan_id=p.id,
                    menu_id=int(menu_id),
                    nama_menu=(
                        menu_obj.nama_menu if menu_obj else '(Menu dihapus)'
                    ),
                    jumlah=int(jum),
                )
                db.session.add(item)

                for recipe in recipes:
                    bahan = db.session.get(Inventory, recipe.inventory_id)
                    if bahan:
                        kebutuhan = recipe.jumlah * int(jum)
                        bahan.qty = bahan.qty - kebutuhan
                        if bahan.qty < 0:
                            flash(
                                f'Stok {bahan.nama_barang} '
                                f'minus {abs(bahan.qty):g} {bahan.satuan}. '
                                f'Order tetap disimpan, '
                                f'segera lakukan stock adjustment.',
                                'warning',
                            )
                        elif bahan.qty <= bahan.stok_minimum:
                            flash(
                                f'{bahan.nama_barang}: sisa '
                                f'{bahan.qty:g} {bahan.satuan} '
                                f'- stok menipis!',
                                'warning',
                            )
                        else:
                            flash(
                                f'{bahan.nama_barang}: sisa '
                                f'{bahan.qty:g} {bahan.satuan}',
                                'info',
                            )

        db.session.commit()
        flash('Rekapan telah disimpan dan stok telah diupdate!')
        return redirect(url_for('sales'))

    if request.method == 'POST':
        menus_form = request.form.getlist('menu_id')
        jumlah = request.form.getlist('jumlah')

        has_order = any(j and int(j) > 0 for j in jumlah)
        if not has_order:
            flash('Pilih minimal satu menu yang terjual!')
            return redirect(url_for('add_sale'))

        for menu_id, jum in zip(menus_form, jumlah):
            if menu_id and jum and int(jum) > 0:
                recipes = db.session.scalars(
                    sa.select(Recipe).where(Recipe.menu_id == int(menu_id))
                ).all()
                if not recipes:
                    menu_obj = db.session.get(Menu, int(menu_id))
                    flash(
                        f'Menu "{menu_obj.nama_menu if menu_obj else "???"}'
                        f' belum mempunyai resep, '
                        f'tidak dapat diinput!'
                    )
                    return redirect(url_for('add_sale'))

        if request.form.get('confirm') == '1':
            return process_sale(menus_form, jumlah)

        shortage_items = []
        for menu_id, jum in zip(menus_form, jumlah):
            if menu_id and jum and int(jum) > 0:
                order_qty = int(jum)
                recipes = db.session.scalars(
                    sa.select(Recipe).where(Recipe.menu_id == int(menu_id))
                ).all()
                for recipe in recipes:
                    bahan = db.session.get(Inventory, recipe.inventory_id)
                    if bahan:
                        kebutuhan = recipe.jumlah * order_qty
                        if bahan.qty < kebutuhan:
                            menu_obj_check = db.session.get(
                                Menu, int(menu_id)
                            )
                            shortage_items.append({
                                'menu_nama': (
                                    menu_obj_check.nama_menu
                                    if menu_obj_check else 'Tidak ditemukan'
                                ),
                                'bahan_nama': bahan.nama_barang,
                                'stok_tersedia': bahan.qty,
                                'kebutuhan': kebutuhan,
                                'satuan': bahan.satuan,
                                'kekurangan': kebutuhan - bahan.qty,
                            })

        if shortage_items:
            return render_template(
                'add_sale.html',
                menus=menus,
                form=form,
                confirm=True,
                shortage_items=shortage_items,
                posted_menus=menus_form,
                posted_jumlah=jumlah,
            )

        return process_sale(menus_form, jumlah)

    return render_template('add_sale.html', menus=menus, form=form)


@app.route('/sales/<int:id>')
@login_required
def sale_detail(id):
    p = db.session.get(Penjualan, id)
    if p is None:
        flash('Data tidak ditemukan!')
        return redirect(url_for('sales'))
    items = db.session.scalars(
        sa.select(ItemPenjualan).where(ItemPenjualan.penjualan_id == id)
    ).all()
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
