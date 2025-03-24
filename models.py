# models.py
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import datetime
from flask_login import UserMixin

db = SQLAlchemy()

class Compras(db.Model):
    __tablename__ = 'compras'
    id_compra = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(100), nullable=False)
    direccion = db.Column(db.String(100), nullable=False)
    telefono = db.Column(db.String(10), nullable=False)
    fecha_compra = db.Column(db.Date, default=datetime.date.today)
    total = db.Column(db.Integer, nullable=False)



class usuarios(db.Model, UserMixin):
    __tablename__ = 'usuarios'
    idUsuario = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(100), nullable=False)
    usuario = db.Column(db.String(100), nullable=False)
    contra = db.Column(db.String(255), nullable=False)
    correo = db.Column(db.String(100), nullable=False)

    def set_password(self, contra):
        """Guarda la contraseña encriptada."""
        self.contra = generate_password_hash(contra)

    def check_password(self, contra):
        """Verifica la contraseña encriptada."""
        return check_password_hash(self.contra, contra)

    def get_id(self):
        """Devuelve el identificador único del usuario."""
        return str(self.idUsuario)    