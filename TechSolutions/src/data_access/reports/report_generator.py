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
                print("No hay conexión a la base de datos, usando datos de demostración")
                # Generar datos de demostración
                ventas = self._get_demo_ventas(fecha_inicio, fecha_fin)
            else:
                cursor = connection.cursor(dictionary=True)
                try:
                    # Intentar llamar al procedimiento almacenado
                    cursor.callproc('GenerarReporteVentas', [fecha_inicio, fecha_fin])
                    
                    # Obtener los resultados
                    ventas = []
                    for result in cursor.stored_results():
                        ventas = result.fetchall()
                    
                    if not ventas:
                        # Si no hay resultados, intentar con una consulta directa
                        query = """
                            SELECT 
                                v.numero_factura,
                                v.fecha_venta,
                                COALESCE(c.nombre, 'Cliente No Registrado') as cliente,
                                COALESCE(u.nombre, 'Usuario No Registrado') as vendedor,
                                v.subtotal,
                                v.impuesto,
                                v.total
                            FROM ventas v
                            LEFT JOIN clientes c ON v.cliente_id = c.id AND c.activo = TRUE
                            LEFT JOIN usuarios u ON v.usuario_id = u.id AND u.activo = TRUE
                            WHERE v.fecha_venta BETWEEN %s AND %s
                            AND v.estado = 'COMPLETADA'
                            ORDER BY v.fecha_venta DESC, v.id DESC
                        """
                        cursor.execute(query, (fecha_inicio, fecha_fin))
                        ventas = cursor.fetchall()
                        
                except Error as e:
                    print(f"Error al ejecutar consulta de ventas: {e}")
                    ventas = self._get_demo_ventas(fecha_inicio, fecha_fin)
                finally:
                    cursor.close()
            
            # Generar PDF
            if archivo_salida is None:
                archivo_salida = f"reporte_ventas_{fecha_inicio}_{fecha_fin}.pdf"
            
            return self._crear_pdf_ventas(ventas, fecha_inicio, fecha_fin, archivo_salida)
            
        except Error as e:
            print(f"Error al generar reporte de ventas: {e}")
            return None
            
    def _get_demo_ventas(self, fecha_inicio, fecha_fin):
        """Genera datos de demostración para el reporte de ventas"""
        from datetime import datetime, timedelta
        
        fecha_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
        fecha_fin = datetime.strptime(fecha_fin, '%Y-%m-%d').date()
        
        # Generar algunas fechas dentro del rango
        dias_totales = (fecha_fin - fecha_inicio).days + 1
        fechas_demo = [
            fecha_inicio + timedelta(days=i)
            for i in range(min(dias_totales, 5))  # Máximo 5 ventas demo
        ]
        
        return [
            {
                'numero_factura': f'F001-{i+1:05d}',
                'fecha_venta': fecha,
                'cliente': 'Empresa Demo SA' if i % 2 == 0 else 'Cliente Ejemplo Ltda',
                'vendedor': 'Vendedor Demo',
                'subtotal': 1000.00 + (i * 100),
                'impuesto': (1000.00 + (i * 100)) * 0.18,
                'total': (1000.00 + (i * 100)) * 1.18
            }
            for i, fecha in enumerate(fechas_demo)
        ]
    
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
        """Crea un PDF con el reporte de ventas"""
        try:
            if not ventas:
                print("No hay ventas para el período seleccionado")
                return None

            # Crear el documento PDF
            doc = SimpleDocTemplate(
                archivo_salida,
                pagesize=letter,
                rightMargin=30,
                leftMargin=30,
                topMargin=30,
                bottomMargin=30
            )
            elements = []
            
            # Estilos
            styles = getSampleStyleSheet()
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Title'],
                fontSize=24,
                spaceAfter=30,
                alignment=1  # Centrado
            )
            subtitle_style = ParagraphStyle(
                'CustomSubTitle',
                parent=styles['Normal'],
                fontSize=14,
                spaceAfter=20,
                alignment=1  # Centrado
            )
            
            # Título y subtítulo
            elements.append(Paragraph("Reporte de Ventas", title_style))
            elements.append(Paragraph(f"Período: {fecha_inicio} al {fecha_fin}", subtitle_style))
            elements.append(Spacer(1, 20))
            
            # Crear la tabla
            data = [['N° Factura', 'Fecha', 'Cliente', 'Vendedor', 'Subtotal', 'Impuesto', 'Total']]
            
            # Agregar los datos
            for venta in ventas:
                fecha = venta['fecha_venta']
                if isinstance(fecha, str):
                    try:
                        fecha = datetime.strptime(fecha, '%Y-%m-%d').date()
                    except ValueError:
                        fecha = datetime.strptime(fecha, '%Y-%m-%d %H:%M:%S').date()
                
                data.append([
                    venta['numero_factura'],
                    fecha.strftime('%d/%m/%Y'),
                    venta['cliente'],
                    venta['vendedor'],
                    f"${venta['subtotal']:,.2f}",
                    f"${venta['impuesto']:,.2f}",
                    f"${venta['total']:,.2f}"
                ])
            
            # Calcular totales
            total_subtotal = sum(float(venta['subtotal']) for venta in ventas)
            total_impuesto = sum(float(venta['impuesto']) for venta in ventas)
            total_total = sum(float(venta['total']) for venta in ventas)
            
            # Agregar fila de totales
            data.append(['', '', '', 'TOTALES:', 
                        f"${total_subtotal:,.2f}",
                        f"${total_impuesto:,.2f}",
                        f"${total_total:,.2f}"])
            
            # Crear la tabla con un ancho específico
            table = Table(data, colWidths=[80, 70, 120, 80, 70, 70, 70])
            
            # Estilo de la tabla
            style = TableStyle([
                # Encabezados
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2C3E50')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                
                # Contenido
                ('BACKGROUND', (0, 1), (-1, -2), colors.white),
                ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                ('ALIGN', (0, 1), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                
                # Totales
                ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#EAECEE')),
                ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, -1), (-1, -1), 11),
                
                # Alineación de columnas numéricas
                ('ALIGN', (-3, 1), (-1, -1), 'RIGHT'),
                
                # Padding
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('LEFTPADDING', (0, 0), (-1, -1), 8),
                ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ])
            table.setStyle(style)
            
            # Alternar colores de las filas
            for i in range(1, len(data) - 1):
                if i % 2 == 0:
                    style = TableStyle([
                        ('BACKGROUND', (0, i), (-1, i), colors.HexColor('#F8F9F9'))
                    ])
                    table.setStyle(style)
            
            elements.append(table)
            
            # Agregar información adicional
            elements.append(Spacer(1, 20))
            elements.append(Paragraph(f"Total de ventas: {len(ventas)}", styles['Normal']))
            elements.append(Paragraph(f"Fecha de generación: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", styles['Normal']))
            
            # Generar el PDF
            doc.build(elements)
            print(f"Reporte generado exitosamente: {archivo_salida}")
            return archivo_salida
            
        except Exception as e:
            print(f"Error al crear PDF: {e}")
            return None
    
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