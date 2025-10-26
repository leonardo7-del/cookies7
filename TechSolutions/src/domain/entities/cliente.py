class Cliente:
    def __init__(self, id=None, nombre=None, email=None, telefono=None, 
                 direccion=None, ruc=None, activo=True, fecha_creacion=None):
        self.id = id
        self.nombre = nombre
        self.email = email
        self.telefono = telefono
        self.direccion = direccion
        self.ruc = ruc
        self.activo = activo
        self.fecha_creacion = fecha_creacion
    
    def __str__(self):
        return f"Cliente {self.id}: {self.nombre}"