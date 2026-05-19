from app import db, login
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from typing import Optional
import sqlalchemy as sa
import sqlalchemy.orm as so

class User(UserMixin, db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    username: so.Mapped[str] = so.mapped_column(sa.String(64), unique=True, nullable=False)
    password_hash: so.Mapped[Optional[str]] = so.mapped_column(sa.String(256))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'
    
@login.user_loader
def load_user(id):
    return db.session.get(User, int(id))

class Inventory(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    kode_barang : so.Mapped[str] = so.mapped_column(sa.String(32), unique=True, nullable=False)
    nama_barang : so.Mapped[str] = so.mapped_column(sa.String(100), nullable=False)
    kategori: so.Mapped[str] = so.mapped_column(sa.String(64))
    satuan: so.Mapped[Optional[str]] = so.mapped_column(sa.String(32))
    qty: so.Mapped[float] = so.mapped_column(sa.Float, nullable=False, default=0)
    harga_beli: so.Mapped[Optional[int]] = so.mapped_column(sa.Integer)
    harga_jual: so.Mapped[Optional[int]] = so.mapped_column(sa.Integer)
    keterangan: so.Mapped[Optional[str]] = so.mapped_column(sa.String(256))
    recipes: so.WriteOnlyMapped['Recipe'] = so.relationship(back_populates='bahan', passive_deletes=True)

    def __repr__(self):
        return f'<Inventory {self.kode_barang} - {self.nama_barang}>'
    
class Menu(db.Model):
    id : so.Mapped[int] = so.mapped_column(primary_key=True)
    nama_menu: so.Mapped[str] = so.mapped_column(sa.String(100), nullable=False)
    harga: so.Mapped[int] = so.mapped_column(sa.Integer, nullable=False)
    deskripsi: so.Mapped[str] = so.mapped_column(sa.String(200))
    recipes: so.WriteOnlyMapped['Recipe'] = so.relationship(back_populates='menu', passive_deletes=True)

    def __repr__(self):
        return f'<Menu {self.nama_menu}>'
    
class Recipe(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    menu_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey('menu.id', ondelete='CASCADE'), nullable=False)
    inventory_id : so.Mapped[int] = so.mapped_column(sa.ForeignKey('inventory.id', ondelete='CASCADE'), nullable=False)
    jumlah : so.Mapped[float] = so.mapped_column(sa.Float, nullable=False)
    satuan: so.Mapped[Optional[str]] = so.mapped_column(sa.String(32))

    menu: so.Mapped['Menu'] = so.relationship(back_populates='recipes')
    bahan: so.Mapped['Inventory'] = so.relationship(back_populates='recipes')

    def __repr__(self):
        return f'<Recipe menu:{self.menu_id} bahan:{self.inventory_id}>'
