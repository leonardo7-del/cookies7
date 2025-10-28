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
                
                # Primero intentar conectar sin especificar la base de datos
                basic_config = {
                    'host': config.db_host,
                    'user': config.db_user,
                    'password': config.db_password,
                    'autocommit': False,
                    'buffered': True,
                    'raise_on_warnings': True,
                    'connection_timeout': 10,
                    'pool_name': 'techsolutions_pool',
                    'pool_size': 5
                }
                
                try:
                    self._connection = mysql.connector.connect(**basic_config)
                except Error as e:
                    if "Can't connect to MySQL server" in str(e):
                        print("❌ MySQL no está instalado o no está en ejecución")
                        print("ℹ️ Por favor, instala MySQL y asegúrate de que esté en ejecución")
                        print("ℹ️ Mientras tanto, se usarán datos de demostración")
                        return None
                    raise e
                
                # Crear y seleccionar la base de datos
                cursor = self._connection.cursor()
                cursor.execute(f"CREATE DATABASE IF NOT EXISTS {config.db_name}")
                cursor.execute(f"USE {config.db_name}")
                
                # Crear tablas si no existen
                self._create_tables(cursor)
                
                self._connection.commit()
                cursor.close()
                
                print("✅ Conexión a MySQL establecida exitosamente")
                
            except Error as e:
                print(f"❌ Error al conectar a MySQL: {e}")
                if self._connection:
                    try:
                        self._connection.close()
                    except:
                        pass
                self._connection = None
                return None  # Retornar None para usar datos demo
        
        return self._connection
    
    def close_connection(self):
        if self._connection and self._connection.is_connected():
            self._connection.close()
            self._connection = None
            print("Conexión a MySQL cerrada")
            
    def _create_tables(self, cursor):
        # Crear tabla de usuarios
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL,
                nombre VARCHAR(100) NOT NULL,
                nivel_acceso INT DEFAULT 1,
                activo BOOLEAN DEFAULT TRUE,
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Crear tabla de clientes
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS clientes (
                id INT AUTO_INCREMENT PRIMARY KEY,
                nombre VARCHAR(100) NOT NULL,
                email VARCHAR(100),
                telefono VARCHAR(20),
                direccion TEXT,
                ruc VARCHAR(20),
                activo BOOLEAN DEFAULT TRUE,
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Crear tabla de productos
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS productos (
                id INT AUTO_INCREMENT PRIMARY KEY,
                codigo VARCHAR(50) UNIQUE NOT NULL,
                nombre VARCHAR(100) NOT NULL,
                descripcion TEXT,
                precio DECIMAL(10,2) NOT NULL,
                stock INT DEFAULT 0,
                stock_minimo INT DEFAULT 5,
                activo BOOLEAN DEFAULT TRUE,
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Crear tabla de ventas
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ventas (
                id INT AUTO_INCREMENT PRIMARY KEY,
                numero_factura VARCHAR(50) UNIQUE NOT NULL,
                cliente_id INT,
                usuario_id INT,
                fecha_venta DATE NOT NULL,
                subtotal DECIMAL(10,2) NOT NULL,
                impuesto DECIMAL(10,2) NOT NULL,
                total DECIMAL(10,2) NOT NULL,
                estado ENUM('PENDIENTE', 'COMPLETADA', 'CANCELADA') DEFAULT 'COMPLETADA',
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (cliente_id) REFERENCES clientes(id),
                FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
            )
        """)
        
        # Crear tabla de detalles de venta
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS venta_detalles (
                id INT AUTO_INCREMENT PRIMARY KEY,
                venta_id INT,
                producto_id INT,
                cantidad INT NOT NULL,
                precio_unitario DECIMAL(10,2) NOT NULL,
                subtotal DECIMAL(10,2) NOT NULL,
                FOREIGN KEY (venta_id) REFERENCES ventas(id) ON DELETE CASCADE,
                FOREIGN KEY (producto_id) REFERENCES productos(id)
            )
        """)
        
        # Insertar usuarios de prueba si no existen
        cursor.execute("SELECT COUNT(*) FROM usuarios")
        if cursor.fetchone()[0] == 0:
            cursor.execute("""
                INSERT INTO usuarios (username, password, nombre, nivel_acceso) VALUES 
                ('admin', 'admin123', 'Administrador Principal', 3),
                ('supervisor', 'super123', 'Supervisor de Ventas', 2),
                ('operador', 'oper123', 'Operador de Sistema', 1)
            """)
        
        # Insertar clientes de prueba si no existen
        cursor.execute("SELECT COUNT(*) FROM clientes")
        if cursor.fetchone()[0] == 0:
            cursor.execute("""
                INSERT INTO clientes (nombre, email, telefono, direccion, ruc) VALUES 
                ('Empresa ABC SA', 'abc@empresa.com', '123-4567', 'Av. Principal 123', '12345678901'),
                ('Comercial XYZ Ltda', 'xyz@comercial.com', '987-6543', 'Calle Secundaria 456', '98765432109')
            """)
        
        # Insertar productos de prueba si no existen
        cursor.execute("SELECT COUNT(*) FROM productos")
        if cursor.fetchone()[0] == 0:
            cursor.execute("""
                INSERT INTO productos (codigo, nombre, descripcion, precio, stock) VALUES 
                ('LAP-001', 'Laptop Dell XPS 13', 'Laptop ultradelgada 13 pulgadas', 1500.00, 10),
                ('MON-001', 'Monitor Samsung 24"', 'Monitor LED Full HD 24 pulgadas', 250.00, 25),
                ('TEC-001', 'Teclado Mecánico RGB', 'Teclado mecánico retroiluminado', 120.00, 15)
            """)
            
        try:
            # Crear procedimiento almacenado para reporte de ventas
            cursor.execute("SET GLOBAL log_bin_trust_function_creators = 1")
            cursor.execute("DROP PROCEDURE IF EXISTS GenerarReporteVentas")
            cursor.execute("""
                DELIMITER //
                CREATE PROCEDURE GenerarReporteVentas(IN fecha_inicio DATE, IN fecha_fin DATE)
                BEGIN
                    SELECT 
                        v.numero_factura,
                        v.fecha_venta,
                        COALESCE(c.nombre, 'Cliente No Registrado') as cliente,
                        COALESCE(u.nombre, 'Usuario No Registrado') as vendedor,
                        CAST(v.subtotal AS DECIMAL(10,2)) as subtotal,
                        CAST(v.impuesto AS DECIMAL(10,2)) as impuesto,
                        CAST(v.total AS DECIMAL(10,2)) as total,
                        v.estado,
                        v.fecha_creacion
                    FROM ventas v
                    LEFT JOIN clientes c ON v.cliente_id = c.id AND c.activo = TRUE
                    LEFT JOIN usuarios u ON v.usuario_id = u.id AND u.activo = TRUE
                    WHERE v.fecha_venta BETWEEN fecha_inicio AND fecha_fin
                    AND v.estado = 'COMPLETADA'
                    ORDER BY v.fecha_venta DESC, v.id DESC;
                END //
                DELIMITER ;
            """)
            print("✅ Procedimiento almacenado GenerarReporteVentas creado exitosamente")
        except Error as e:
            print(f"⚠️ Error al crear el procedimiento almacenado GenerarReporteVentas: {e}")
            # Intentar crear una versión más simple del procedimiento
            try:
                cursor.execute("""
                    CREATE PROCEDURE GenerarReporteVentas(IN fecha_inicio DATE, IN fecha_fin DATE)
                    BEGIN
                        SELECT 
                            v.numero_factura,
                            v.fecha_venta,
                            COALESCE(c.nombre, 'Cliente No Registrado') as cliente,
                            COALESCE(u.nombre, 'Usuario No Registrado') as vendedor,
                            v.subtotal,
                            v.impuesto,
                            v.total
                        FROM ventas v
                        LEFT JOIN clientes c ON v.cliente_id = c.id
                        LEFT JOIN usuarios u ON v.usuario_id = u.id
                        WHERE v.fecha_venta BETWEEN fecha_inicio AND fecha_fin
                        AND v.estado = 'COMPLETADA'
                        ORDER BY v.fecha_venta DESC;
                    END
                """)
                print("✅ Procedimiento almacenado GenerarReporteVentas creado en modo básico")
            except Error as e2:
                print(f"❌ Error al crear el procedimiento almacenado en modo básico: {e2}")
                # No lanzar excepción para permitir que la aplicación continúe funcionando

class Transaction:
    def __init__(self):
        self.db = DatabaseConnection()
        self.connection = None
        self.cursor = None
        
    def __enter__(self):
        self.connection = self.db.get_connection()
        if not self.connection:
            return None
            
        try:
            self.cursor = self.connection.cursor(dictionary=True)
            return self
        except Error as e:
            print(f"Error al iniciar la transacción: {e}")
            if self.connection:
                try:
                    self.connection.close()
                except:
                    pass
            return None
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            if exc_type is None and self.connection:
                # Si no hubo excepciones, confirmar los cambios
                self.connection.commit()
            elif self.connection:
                # Si hubo una excepción, deshacer los cambios
                self.connection.rollback()
                
        except Error as e:
            print(f"Error al finalizar la transacción: {e}")
            if self.connection:
                try:
                    self.connection.rollback()
                except:
                    pass
        finally:
            if self.cursor:
                try:
                    self.cursor.close()
                except:
                    pass
            self.cursor = None
    
    def cursor(self, dictionary=True):
        """Retorna el cursor de la transacción"""
        if not self.cursor:
            if not self.connection:
                return None
            try:
                self.cursor = self.connection.cursor(dictionary=dictionary)
            except Error as e:
                print(f"Error al crear el cursor: {e}")
                return None
        return self.cursor
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