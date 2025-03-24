from models import db,usuarios
from app import app 


with app.app_context():
    nuevo_usuario = usuarios(
        nombre='',
        usuario='Eduardo',
        correo='',        
    )
    nuevo_usuario.set_password("2468")  

    db.session.add(nuevo_usuario) 
    db.session.commit()  

    print("Usuario creado con éxito")