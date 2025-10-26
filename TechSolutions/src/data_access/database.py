"""
Versión para MySQL con transacciones y rollback
"""
import mysql.connector
from mysql.connector import Error
from .config import Config

class DatabaseConnection:
    _instance = None
    _connection = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseConnection, cls).__new__(cls)
        return cls._instance
    
    def get_connection(self):
        if self._connection is None or not self._connection.is_connected():
            try:
                config = Config()
                db_config = config.get_db_config()
                self._connection = mysql.connector.connect(**db_config)
                print("✅ Conexión a MySQL establecida exitosamente")
            except Error as e:
                print(f"❌ Error al conectar a MySQL: {e}")
                # Fallback a datos demo si no hay conexión
                self._connection = None
        return self._connection
    
    def close_connection(self):
        if self._connection and self._connection.is_connected():
            self._connection.close()
            self._connection = None
            print("Conexión a MySQL cerrada")

class Transaction:
    def __init__(self):
        self.db = DatabaseConnection()
        self.connection = self.db.get_connection()
    
    def __enter__(self):
        if self.connection:
            self.connection.start_transaction()
        return self.connection
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.connection:
            if exc_type is not None:
                self.connection.rollback()
                print("❌ Transacción revertida debido a un error")
                return False
            else:
                self.connection.commit()
                print("✅ Transacción completada exitosamente")
                return True