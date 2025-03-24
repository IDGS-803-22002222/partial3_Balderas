#forms.py
from wtforms import Form
from wtforms import StringField, PasswordField, EmailField, BooleanField, SubmitField, IntegerField, RadioField, SelectMultipleField, DateField
from wtforms import validators
from wtforms.widgets import ListWidget, CheckboxInput
from datetime import date
from wtforms.validators import Regexp
from flask_wtf import FlaskForm

class Compra(Form):
	nombre = StringField("Nombre:",[
		validators.DataRequired(message="El campo nombre es requerido")
	])
	direccion = StringField("Dirección:",[
		validators.DataRequired(message="El campo dirección es requerido")
	])
	telefono = StringField("Teléfono:", [
        validators.DataRequired(message="El campo teléfono es requerido"),
        Regexp(r'^\d{10}$', message="El teléfono debe contener exactamente 10 dígitos y sin espacios o caracteres especiales")
    ])
	tamano = RadioField('Tamaño Pizza', choices=[('Chica', 'Chica $40'),('Mediana', 'Mediana $80') ,('Grande', 'Grande $120')], 
		validators=[validators.DataRequired(message="Debes seleccionar una opción")
	])
	ingredientes = SelectMultipleField(
		'Ingredientes',
		choices=[('Jamon', 'Jamón $10'), ('Pina', 'Pina $10'), ('Champinones', 'Champiñones $10')],
		widget=ListWidget(prefix_label=False),
		option_widget=CheckboxInput(),
		validators=[validators.DataRequired(message="Debes seleccionar al menos un ingrediente")]
	)
	num_pizzas = IntegerField("Num. de Pizzas:",[
		validators.DataRequired(message="El número de pizzas es requerido")
	])


class Busqueda(Form):
	tipo_busqueda = RadioField('Tipo de Busqueda', choices=[('mes', 'Mes'),('dia', 'Día')], 
		validators=[validators.DataRequired(message="Debes seleccionar una opción")
	])
	texto_busqueda = StringField("Dato a buscar",[
		validators.DataRequired(message="El campo de busqueda es requerido")
	])



class login(FlaskForm):
	usuario = StringField("Usuario: ",[
		validators.DataRequired(message="El campo nombre es requerido")
	])
	contra = StringField("Contraseña: ",[
		validators.DataRequired(message="El campo de busqueda es requerido")
	])