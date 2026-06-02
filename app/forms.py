from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, TextAreaField, SubmitField, SelectField, IntegerField
from wtforms.validators import DataRequired, Optional, NumberRange

class InventoryForm(FlaskForm):
    kode_barang = StringField('Kode Barang', validators=[DataRequired(message='Kode barang wajib diisi!')])
    nama_barang = StringField('Nama Barang', validators=[DataRequired(message='Nama barang wajib diisi!')])
    kategori = StringField('Kategori', validators=[Optional()])
    qty = FloatField('QTY', validators=[DataRequired(message='QTY wajib diisi!'), NumberRange(min=0, message='QTY tidak bisa minus!')])
    stok_minimum = FloatField('Stok Minimum', validators=[Optional(), NumberRange(min=0, message='Tidak bisa minus!')], default=0)
    satuan = SelectField('Satuan', choices=[
        ('gram', 'gram'),
        ('ml', 'ml'),
        ('pcs', 'pcs')
    ])
    keterangan = TextAreaField('Keterangan', validators=[Optional()])
    submit = SubmitField('Simpan')

class MenuForm(FlaskForm):
    nama_menu = StringField('Nama Menu', validators=[DataRequired(message='Harap isi menu!')])
    harga = IntegerField('Harga', validators=[DataRequired(message='Harga wajib diisi!')])
    deskripsi = TextAreaField('Deskripsi', validators=[Optional()])
    submit = SubmitField('Simpan')

class SaleForm(FlaskForm):
    catatan = StringField('Catatan', validators=[Optional()])
    submit = SubmitField('Simpan')