# app.py
from flask import Flask, render_template, request, redirect, url_for, flash
from flask import flash
from flask_wtf.csrf import CSRFProtect
from flask import g
from config import DeveplopmentConfig
from forms import login
from sqlalchemy import func, extract
import forms
import os
from models import db
from models import Compras
from forms import login, RegistroForm
from models import usuarios
from datetime import datetime
from forms import RegistroForm
from flask_login import LoginManager, login_user, logout_user, login_required, current_user

app = Flask(__name__)
app.config.from_object(DeveplopmentConfig)
csrf = CSRFProtect()
#db.init_app(app)

login_manager = LoginManager() 
login_manager.init_app(app)
login_manager.login_message = 'Por favor inicia sesión para acceder a esta página.'
login_manager.login_view = 'login_view'


@login_manager.user_loader
def load_user(user_id):
    return usuarios.query.get(int(user_id))

@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def login_view():
    login_form = login(request.form)
    registro_form = RegistroForm(request.form)  
    
    if request.method == 'POST':
        if 'submit_login' in request.form and login_form.validate():
            usu = login_form.usuario.data
            contra = login_form.contra.data
            user = usuarios.query.filter_by(usuario=usu).first()
            if user and user.check_password(contra):
                login_user(user, remember=True)
                flash('Inicio de sesión exitoso.', 'success')
                return redirect(url_for('insertar'))
            else:
                flash('Los datos son incorrectos', 'danger')
        
        elif 'submit_registro' in request.form and registro_form.validate():
            existing_user = usuarios.query.filter_by(usuario=registro_form.usuario.data).first()
            if existing_user:
                flash('El nombre de usuario ya está en uso', 'danger')
                return render_template('index.html', form=login_form, registro_form=registro_form)
            
            existing_email = usuarios.query.filter_by(correo=registro_form.correo.data).first()
            if existing_email:
                flash('El correo electrónico ya está registrado', 'danger')
                return render_template('index.html', form=login_form, registro_form=registro_form)
            
            new_user = usuarios(
                nombre=registro_form.nombre.data,
                usuario=registro_form.usuario.data,
                correo=registro_form.correo.data
            )
            new_user.set_password(registro_form.contra.data)
            
            db.session.add(new_user)
            db.session.commit()
            
            flash('Registro exitoso. Ahora puedes iniciar sesión.', 'success')
            return redirect(url_for('login_view'))
    
    return render_template('index.html', form=login_form, registro_form=registro_form)



@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Has cerrado sesión', 'info')
    return redirect(url_for('login_view'))



compras = []
@app.route("/pizza", methods=['GET', 'POST'])
@login_required
def insertar():
     compra_class=forms.Compra(request.form)
     busqueda_class = forms.Busqueda(request.form)
     get_all_compras =Compras.query.all()
     user = current_user
     if request.method == 'POST' and compra_class.validate():
          compra = {
               'nombre': compra_class.nombre.data,
               'direccion': compra_class.direccion.data,
               'telefono': compra_class.telefono.data,
               'tamano': compra_class.tamano.data,
               'ingredientes': compra_class.ingredientes.data,
               'num_pizzas': compra_class.num_pizzas.data,
               'subtotal': calcular_subtotal(compra_class.tamano.data, compra_class.ingredientes.data, compra_class.num_pizzas.data)
          }

          compras.append(compra)
          with open("pedidos.txt", "a") as file:
              file.write(
                   f"{compra['nombre']},"
                   f"{compra['direccion']},"
                   f"{compra['telefono']},"
                   f"{compra['tamano']},"
                   f"{compra['ingredientes']},"
                   f"{compra['num_pizzas']},"
                   f"{compra['subtotal']}\n"
               )

          compra_class.nombre.data = compra['nombre']
          compra_class.direccion.data = compra['direccion']
          compra_class.telefono.data = compra['telefono']
          compra_class.tamano.data = ""
          compra_class.ingredientes.data = ""
     total = 0
     for venta in get_all_compras:
        total += venta.total
     return render_template("pizza.html", form=compra_class, form2=busqueda_class, compras=compras, get_all = get_all_compras, total=total, user=user)

@app.route("/quitar", methods=['POST'])
@login_required
def quitar_compra():
     compra_class=forms.Compra(request.form)
     busqueda_class = forms.Busqueda(request.form)
     if compras:
          if os.path.exists("pedidos.txt"):
               with open("pedidos.txt", "r") as file:
                    lines = file.readlines()
               
               with open("pedidos.txt", "w") as file:
                    file.writelines(lines[:-1])

          compra_class.nombre.data = compras[0]['nombre']
          compra_class.direccion.data = compras[0]['direccion']
          compra_class.telefono.data = compras[0]['telefono']
          compra_class.tamano.data = ""
          compra_class.ingredientes.data = ""
          compras.pop()
     
     return render_template("pizza.html", form=compra_class, form2=busqueda_class, compras=compras)

@app.route("/terminar", methods=['POST'])
@login_required
def terminar_pedido():
    total = 0

    try:
        with open("pedidos.txt", "r") as file:
            lineas = file.readlines()
            if not lineas:
                flash("El archivo de pedidos está vacío.", "danger")
                return redirect(url_for("insertar"))
            
            for linea in lineas:
                datos = linea.strip().split(",")
                subtotal = float(datos[-1])
                total += subtotal
               
            compra = Compras(nombre=datos[0], direccion=datos[1], telefono=datos[2], total=total)
            db.session.add(compra)
            db.session.commit()
    except FileNotFoundError:
        flash("No hay pedidos registrados.", "danger")
        return redirect(url_for("insertar"))

    flash(f"El costo total del pedido es: ${total:.2f}", "success")

    open("pedidos.txt", "w").close()

    compras.clear()

    return redirect(url_for("insertar"))

@app.route('/buscar', methods=['GET', 'POST'])
@login_required
def buscar():
    busqueda_class = forms.Busqueda(request.form)
    compra_class = forms.Compra(request.form)

    ventas = []
    error = ""
    if request.method == 'POST' and busqueda_class.validate():
        tipo_busqueda = busqueda_class.tipo_busqueda.data
        texto_busqueda = busqueda_class.texto_busqueda.data.strip().lower()
        
        try:
            if tipo_busqueda == 'dia':
                if texto_busqueda.isdigit():
                    ventas = Compras.query.filter(extract('day', Compras.fecha_compra) == int(texto_busqueda)).all()
                else:
                    error = "Ingrese un número válido para el día."

            elif tipo_busqueda == 'mes':
                meses = {
                    'enero': 1, 'febrero': 2, 'marzo': 3, 'abril': 4, 'mayo': 5, 'junio': 6,
                    'julio': 7, 'agosto': 8, 'septiembre': 9, 'octubre': 10, 'noviembre': 11, 'diciembre': 12
                }
                if texto_busqueda in meses:
                    numero_mes = meses[texto_busqueda]
                    ventas = Compras.query.filter(extract('month', Compras.fecha_compra) == numero_mes).all()
                else:
                    error = "Ingrese un nombre de mes válido."

        except Exception as e:
            flash(f"Error en la búsqueda: {str(e)}", "danger")
    total = 0
    for venta in ventas:
        total += venta.total

    return render_template('pizza.html', form=compra_class, form2=busqueda_class, ventas=ventas, total=total, e=error)

def calcular_subtotal(tamano, ingredientes, num_pizzas):
    precios_tamano = {'Chica': 40, 'Mediana': 80, 'Grande': 120}
    precio_ingredientes = len(ingredientes) * 10
    subtotal = (precios_tamano.get(tamano, 0) + precio_ingredientes) * num_pizzas
    return subtotal

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if current_user.is_authenticated:
        return redirect(url_for('insertar'))
    
    form = RegistroForm(request.form)
    
    if request.method == 'POST' and form.validate():
        existing_user = usuarios.query.filter_by(usuario=form.usuario.data).first()
        if existing_user:
            flash('El nombre de usuario ya está en uso', 'danger')
            return render_template('index.html', form=login(), registro_form=form)
        
        existing_email = usuarios.query.filter_by(correo=form.correo.data).first()
        if existing_email:
            flash('El correo electrónico ya está registrado', 'danger')
            return render_template('index.html', form=login(), registro_form=form)
        
        new_user = usuarios(
            nombre=form.nombre.data,
            usuario=form.usuario.data,
            correo=form.correo.data
        )
        new_user.set_password(form.contra.data)
        
        db.session.add(new_user)
        db.session.commit()
        
        flash('Registro exitoso. Ahora puedes iniciar sesión.', 'success')
        return redirect(url_for('login_view'))
    
    return render_template('index.html', form=login(), registro_form=form)

if __name__ == '__main__':
    csrf.init_app(app)
    db.init_app(app)
    
    with app.app_context():
        db.create_all()
    app.run()