-- Crear base de datos
CREATE DATABASE IF NOT EXISTS tech_solutions;
USE tech_solutions;

-- Tabla de usuarios
CREATE TABLE usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    nivel_acceso INT DEFAULT 1,
    activo BOOLEAN DEFAULT TRUE,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de clientes
CREATE TABLE clientes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    email VARCHAR(100),
    telefono VARCHAR(20),
    direccion TEXT,
    ruc VARCHAR(20),
    activo BOOLEAN DEFAULT TRUE,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de productos
CREATE TABLE productos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    codigo VARCHAR(50) UNIQUE NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    descripcion TEXT,
    precio DECIMAL(10,2) NOT NULL,
    stock INT DEFAULT 0,
    stock_minimo INT DEFAULT 5,
    activo BOOLEAN DEFAULT TRUE,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de ventas
CREATE TABLE ventas (
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
);

-- Tabla de detalles de venta
CREATE TABLE venta_detalles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    venta_id INT,
    producto_id INT,
    cantidad INT NOT NULL,
    precio_unitario DECIMAL(10,2) NOT NULL,
    subtotal DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (venta_id) REFERENCES ventas(id) ON DELETE CASCADE,
    FOREIGN KEY (producto_id) REFERENCES productos(id)
);

-- Insertar usuarios de prueba
INSERT INTO usuarios (username, password, nombre, nivel_acceso) VALUES
('admin', 'admin123', 'Administrador Principal', 3),
('supervisor', 'super123', 'Supervisor de Ventas', 2),
('operador', 'oper123', 'Operador de Sistema', 1);

-- Insertar clientes de prueba
INSERT INTO clientes (nombre, email, telefono, direccion, ruc) VALUES
('Empresa ABC SA', 'abc@empresa.com', '123-4567', 'Av. Principal 123', '12345678901'),
('Comercial XYZ Ltda', 'xyz@comercial.com', '987-6543', 'Calle Secundaria 456', '98765432109');

-- Insertar productos de prueba
INSERT INTO productos (codigo, nombre, descripcion, precio, stock) VALUES
('LAP-001', 'Laptop Dell XPS 13', 'Laptop ultradelgada 13 pulgadas', 1500.00, 10),
('MON-001', 'Monitor Samsung 24"', 'Monitor LED Full HD 24 pulgadas', 250.00, 25),
('TEC-001', 'Teclado Mecánico RGB', 'Teclado mecánico retroiluminado', 120.00, 15);

-- Procedimiento almacenado para reporte de ventas
DELIMITER //
CREATE PROCEDURE GenerarReporteVentas(IN fecha_inicio DATE, IN fecha_fin DATE)
BEGIN
    SELECT
        v.numero_factura,
        v.fecha_venta,
        c.nombre as cliente,
        u.nombre as vendedor,
        v.subtotal,
        v.impuesto,
        v.total
    FROM ventas v
    LEFT JOIN clientes c ON v.cliente_id = c.id
    LEFT JOIN usuarios u ON v.usuario_id = u.id
    WHERE v.fecha_venta BETWEEN fecha_inicio AND fecha_fin
    AND v.estado = 'COMPLETADA'
    ORDER BY v.fecha_venta DESC;
END //
DELIMITER ;