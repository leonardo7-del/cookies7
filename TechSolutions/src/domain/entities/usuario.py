class Usuario:
    def __init__(self, id, username, nombre, nivel_acceso):
        self.id = id
        self.username = username
        self.nombre = nombre
        self.nivel_acceso = nivel_acceso
    
    def tiene_acceso(self, nivel_requerido):
        return self.nivel_acceso >= nivel_requerido
    
    def es_administrador(self):
        return self.nivel_acceso == 3
    
    def es_supervisor(self):
        return self.nivel_acceso >= 2