import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

class Config:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
            cls._instance._load_config()
        return cls._instance
    
    def _load_config(self):
        # Configuración para MySQL - Con variables de entorno o valores por defecto
        self.db_host = os.getenv('DB_HOST', '127.0.0.1')
        self.db_port = int(os.getenv('DB_PORT', 3306))
        self.db_name = os.getenv('DB_NAME', 'tech_solutions')
        self.db_user = os.getenv('DB_USER', 'root')
        self.db_password = os.getenv('DB_PASSWORD', '')  # Tu contraseña de MySQL
        
        # Configuración de la aplicación
        self.app_name = "Tech Solutions CRM"
        self.app_version = "1.0.0"
        self.tax_rate = 0.10  # 10% de impuesto
    
    def get_db_config(self):
        return {
            'host': self.db_host,
            'port': self.db_port,
            'database': self.db_name,
            'user': self.db_user,
            'password': self.db_password,
            'autocommit': False,
            'charset': 'utf8mb4',
            'collation': 'utf8mb4_unicode_ci'
        }