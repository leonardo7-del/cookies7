from ..database import DatabaseConnection
from mysql.connector import Error
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from datetime import datetime
import os

class ReportGenerator:
    def __init__(self):
        self.db = DatabaseConnection()
        self.styles = getSampleStyleSheet()
        
    def generar_reporte_ventas(self, fecha_inicio, fecha_fin, archivo_salida=None):
        """Genera reporte de ventas usando el procedimiento almacenado"""
        try:
            connection = self.db.get_connection()
            if connection is None:
                raise Exception("No se pudo conectar a la base de datos")
            
            cursor = connection.cursor(dictionary=True)
            
            # Llamar al procedimiento almacenado
            cursor.callproc('GenerarReporteVentas', [fecha_inicio, fecha_fin])
            
            # Obtener los resultados
            ventas = []
            for result in cursor.stored_results():
                ventas = result.fetchall()
            
            cursor.close()
            
            # Generar PDF
            if archivo_salida is None:
                archivo_salida = f"reporte_ventas_{fecha_inicio}_{fecha_fin}.pdf"
            
            return self._crear_pdf_ventas(ventas, fecha_inicio, fecha_fin, archivo_salida)
            
        except Error as e:
            print(f"Error al generar reporte de ventas: {e}")
            return None
    
    def generar_reporte_productos_bajo_stock(self, archivo_salida=None):
        """Genera reporte de productos con stock bajo"""
        try:
            connection = self.db.get_connection()
            if connection is None:
                raise Exception("No se pudo conectar a la base de datos")
            
            cursor = connection.cursor(dictionary=True)
            
            query = """
                SELECT codigo, nombre, stock, stock_minimo, precio
                FROM productos 
                WHERE stock <= stock_minimo AND activo = 1
                ORDER BY stock ASC
            """
            cursor.execute(query)
            productos = cursor.fetchall()
            
            cursor.close()
            
            if archivo_salida is None:
                archivo_salida = f"productos_bajo_stock_{datetime.now().strftime('%Y%m%d')}.pdf"
            
            return self._crear_pdf_productos_bajo_stock(productos, archivo_salida)
            
        except Error as e:
            print(f"Error al generar reporte de productos: {e}")
            return None
    
    def generar_reporte_clientes(self, archivo_salida=None):
        """Genera reporte de clientes activos"""
        try:
            connection = self.db.get_connection()
            if connection is None:
                raise Exception("No se pudo conectar a la base de datos")
            
            cursor = connection.cursor(dictionary=True)
            
            query = """
                SELECT c.nombre, c.email, c.telefono, c.ruc,
                       COUNT(v.id) as total_ventas,
                       COALESCE(SUM(v.total), 0) as total_compras
                FROM clientes c
                LEFT JOIN ventas v ON c.id = v.cliente_id AND v.estado = 'COMPLETADA'
                WHERE c.activo = 1
                GROUP BY c.id, c.nombre, c.email, c.telefono, c.ruc
                ORDER BY total_compras DESC
            """
            cursor.execute(query)
            clientes = cursor.fetchall()
            
            cursor.close()
            
            if archivo_salida is None:
                archivo_salida = f"reporte_clientes_{datetime.now().strftime('%Y%m%d')}.pdf"
            
            return self._crear_pdf_clientes(clientes, archivo_salida)
            
        except Error as e:
            print(f"Error al generar reporte de clientes: {e}")
            return None
    
    def _crear_pdf_ventas(self, ventas, fecha_inicio, fecha_fin, archivo_salida):
        """Crea PDF del reporte de ventas"""
        doc = SimpleDocTemplate(archivo_salida, pagesize=A4)
        elementos = []
        
        # Título
        titulo_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=16,
            spaceAfter=30,
            alignment=1  # Centrado
        )
        titulo = Paragraph(f"Reporte de Ventas<br/>Del {fecha_inicio} al {fecha_fin}", titulo_style)
        elementos.append(titulo)
        
        if not ventas:
            elementos.append(Paragraph("No se encontraron ventas en el período especificado.", self.styles['Normal']))
        else:
            # Tabla de ventas
            data = [['Factura', 'Fecha', 'Cliente', 'Vendedor', 'Subtotal', 'Impuesto', 'Total']]
            
            total_subtotal = 0
            total_impuesto = 0
            total_general = 0
            
            for venta in ventas:
                data.append([
                    venta['numero_factura'],
                    venta['fecha_venta'].strftime('%d/%m/%Y') if venta['fecha_venta'] else '',
                    venta['cliente'] or 'N/A',
                    venta['vendedor'] or 'N/A',
                    f"${venta['subtotal']:.2f}",
                    f"${venta['impuesto']:.2f}",
                    f"${venta['total']:.2f}"
                ])
                total_subtotal += float(venta['subtotal'])
                total_impuesto += float(venta['impuesto'])
                total_general += float(venta['total'])
            
            # Fila de totales
            data.append(['', '', '', 'TOTALES:', f"${total_subtotal:.2f}", f"${total_impuesto:.2f}", f"${total_general:.2f}"])
            
            tabla = Table(data)
            tabla.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -2), colors.beige),
                ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
                ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            elementos.append(tabla)
        
        doc.build(elementos)
        return archivo_salida
    
    def _crear_pdf_productos_bajo_stock(self, productos, archivo_salida):
        """Crea PDF del reporte de productos con stock bajo"""
        doc = SimpleDocTemplate(archivo_salida, pagesize=A4)
        elementos = []
        
        # Título
        titulo_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=16,
            spaceAfter=30,
            alignment=1
        )
        titulo = Paragraph("Reporte de Productos con Stock Bajo", titulo_style)
        elementos.append(titulo)
        
        if not productos:
            elementos.append(Paragraph("Todos los productos tienen stock suficiente.", self.styles['Normal']))
        else:
            # Tabla de productos
            data = [['Código', 'Nombre', 'Stock Actual', 'Stock Mínimo', 'Precio']]
            
            for producto in productos:
                data.append([
                    producto['codigo'],
                    producto['nombre'],
                    str(producto['stock']),
                    str(producto['stock_minimo']),
                    f"${producto['precio']:.2f}"
                ])
            
            tabla = Table(data)
            tabla.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            elementos.append(tabla)
        
        doc.build(elementos)
        return archivo_salida
    
    def _crear_pdf_clientes(self, clientes, archivo_salida):
        """Crea PDF del reporte de clientes"""
        doc = SimpleDocTemplate(archivo_salida, pagesize=A4)
        elementos = []
        
        # Título
        titulo_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=16,
            spaceAfter=30,
            alignment=1
        )
        titulo = Paragraph("Reporte de Clientes", titulo_style)
        elementos.append(titulo)
        
        if not clientes:
            elementos.append(Paragraph("No se encontraron clientes.", self.styles['Normal']))
        else:
            # Tabla de clientes
            data = [['Nombre', 'Email', 'Teléfono', 'RUC', 'Total Ventas', 'Total Compras']]
            
            for cliente in clientes:
                data.append([
                    cliente['nombre'],
                    cliente['email'] or 'N/A',
                    cliente['telefono'] or 'N/A',
                    cliente['ruc'] or 'N/A',
                    str(cliente['total_ventas']),
                    f"${cliente['total_compras']:.2f}"
                ])
            
            tabla = Table(data)
            tabla.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            elementos.append(tabla)
        
        doc.build(elementos)
        return archivo_salida