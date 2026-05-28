from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, TextAreaField, SubmitField, SelectField
from wtforms.validators import DataRequired, Optional, NumberRange

class InventoryForm(FlaskForm):
    kode_barang = StringField('Kode Barang', validators=[DataRequired()])
    nama_barang = StringField('Nama Barang', validators=[DataRequired(message='Nama barang wajib diisi!')])
    kategori = StringField('Kategori', validators=[Optional()])
    qty = FloatField('QTY', validators=[DataRequired(), NumberRange(min=0, message='QTY tidak bisa minus!')])
    satuan = SelectField('Satuan', choices=[
        ('gram', 'gram'),
        ('kg', 'kg'),
        ('ml', 'ml'),
        ('liter', 'liter'),
        ('pcs', 'pcs')
    ])
    keterangan = TextAreaField('Keterangan', validators=[Optional()])
    submit = SubmitField('Simpan')