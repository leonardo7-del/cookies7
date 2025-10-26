import os

class Config:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
            cls._instance._load_config()
        return cls._instance
    
    def _load_config(self):
        # Configuración para MySQL - Con tus datos de conexión
        self.db_host = '127.0.0.1'
        self.db_port = '3306'
        self.db_name = 'tech_solutions'
        self.db_user = 'root'
        self.db_password = ''  # Tu contraseña de MySQL
    
    def get_db_config(self):
        return {
            'host': self.db_host,
            'port': self.db_port,
            'database': self.db_name,
            'user': self.db_user,
            'password': self.db_password
        }