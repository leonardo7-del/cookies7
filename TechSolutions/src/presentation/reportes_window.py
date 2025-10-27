import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime, timedelta
import os
import subprocess
import platform
from src.data_access.reports.report_generator import ReportGenerator

class ReportesWindow:
    def __init__(self, parent, auth_service):
        self.parent = parent
        self.auth_service = auth_service
        self.report_generator = ReportGenerator()
        
        self._create_window()
    
    def _create_window(self):
        self.window = tk.Toplevel(self.parent)
        self.window.title("Generación de Reportes")
        self.window.geometry("600x500")
        self.window.transient(self.parent)
        self.window.grab_set()
        
        # Frame principal
        main_frame = ttk.Frame(self.window, padding="20")
        main_frame.pack(fill='both', expand=True)
        
        # Título
        title_label = ttk.Label(main_frame, text="Generación de Reportes", 
                               font=("Arial", 16, "bold"))
        title_label.pack(pady=(0, 20))
        
        # Notebook para diferentes tipos de reportes
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill='both', expand=True, pady=(0, 20))
        
        # Tab 1: Reporte de Ventas
        ventas_frame = ttk.Frame(notebook, padding="20")
        notebook.add(ventas_frame, text="Reporte de Ventas")
        
        # Sección de fechas para reporte de ventas
        fechas_frame = ttk.LabelFrame(ventas_frame, text="Período del Reporte", padding="15")
        fechas_frame.pack(fill='x', pady=(0, 20))
        
        # Fecha inicio
        ttk.Label(fechas_frame, text="Fecha Inicio:").grid(row=0, column=0, sticky='w', pady=5)
        self.fecha_inicio = tk.StringVar()
        fecha_inicio_entry = ttk.Entry(fechas_frame, textvariable=self.fecha_inicio, width=15)
        fecha_inicio_entry.grid(row=0, column=1, sticky='w', padx=(10, 0), pady=5)
        
        # Fecha fin
        ttk.Label(fechas_frame, text="Fecha Fin:").grid(row=1, column=0, sticky='w', pady=5)
        self.fecha_fin = tk.StringVar()
        fecha_fin_entry = ttk.Entry(fechas_frame, textvariable=self.fecha_fin, width=15)
        fecha_fin_entry.grid(row=1, column=1, sticky='w', padx=(10, 0), pady=5)
        
        # Formato de fecha
        ttk.Label(fechas_frame, text="Formato: YYYY-MM-DD", 
                 font=("Arial", 8)).grid(row=2, column=1, sticky='w', padx=(10, 0))
        
        # Botones de fechas predefinidas
        botones_frame = ttk.Frame(fechas_frame)
        botones_frame.grid(row=3, column=0, columnspan=2, pady=(10, 0), sticky='w')
        
        ttk.Button(botones_frame, text="Hoy", 
                  command=self._set_fecha_hoy).pack(side='left', padx=(0, 5))
        ttk.Button(botones_frame, text="Esta Semana", 
                  command=self._set_fecha_semana).pack(side='left', padx=(0, 5))
        ttk.Button(botones_frame, text="Este Mes", 
                  command=self._set_fecha_mes).pack(side='left')
        
        # Botón generar reporte de ventas
        ttk.Button(ventas_frame, text="Generar Reporte de Ventas", 
                  command=self._generar_reporte_ventas,
                  style='Accent.TButton').pack(pady=20)
        
        # Tab 2: Reporte de Inventario
        inventario_frame = ttk.Frame(notebook, padding="20")
        notebook.add(inventario_frame, text="Reporte de Inventario")
        
        # Opciones de inventario
        opciones_frame = ttk.LabelFrame(inventario_frame, text="Opciones de Reporte", padding="15")
        opciones_frame.pack(fill='x', pady=(0, 20))
        
        self.tipo_inventario = tk.StringVar(value="bajo_stock")
        
        ttk.Radiobutton(opciones_frame, text="Productos con Stock Bajo", 
                       variable=self.tipo_inventario, value="bajo_stock").pack(anchor='w', pady=5)
        ttk.Radiobutton(opciones_frame, text="Inventario Completo", 
                       variable=self.tipo_inventario, value="completo").pack(anchor='w', pady=5)
        
        # Botón generar reporte de inventario
        ttk.Button(inventario_frame, text="Generar Reporte de Inventario", 
                  command=self._generar_reporte_inventario,
                  style='Accent.TButton').pack(pady=20)
        
        # Tab 3: Reporte de Clientes
        clientes_frame = ttk.Frame(notebook, padding="20")
        notebook.add(clientes_frame, text="Reporte de Clientes")
        
        # Información del reporte de clientes
        info_frame = ttk.LabelFrame(clientes_frame, text="Información", padding="15")
        info_frame.pack(fill='x', pady=(0, 20))
        
        ttk.Label(info_frame, text="Este reporte incluye todos los clientes activos\n"
                                  "con su información de contacto y estadísticas básicas.",
                 justify='left').pack(anchor='w')
        
        # Botón generar reporte de clientes
        ttk.Button(clientes_frame, text="Generar Reporte de Clientes", 
                  command=self._generar_reporte_clientes,
                  style='Accent.TButton').pack(pady=20)
        
        # Frame de estado
        self.status_frame = ttk.Frame(main_frame)
        self.status_frame.pack(fill='x')
        
        self.status_label = ttk.Label(self.status_frame, text="Listo para generar reportes")
        self.status_label.pack(side='left')
        
        # Botón cerrar
        ttk.Button(main_frame, text="Cerrar", 
                  command=self.window.destroy).pack(side='right', pady=(10, 0))
        
        # Establecer fechas por defecto (último mes)
        self._set_fecha_mes()
    
    def _set_fecha_hoy(self):
        hoy = datetime.now()
        self.fecha_inicio.set(hoy.strftime('%Y-%m-%d'))
        self.fecha_fin.set(hoy.strftime('%Y-%m-%d'))
    
    def _set_fecha_semana(self):
        hoy = datetime.now()
        inicio_semana = hoy - timedelta(days=hoy.weekday())
        self.fecha_inicio.set(inicio_semana.strftime('%Y-%m-%d'))
        self.fecha_fin.set(hoy.strftime('%Y-%m-%d'))
    
    def _set_fecha_mes(self):
        hoy = datetime.now()
        inicio_mes = hoy.replace(day=1)
        self.fecha_inicio.set(inicio_mes.strftime('%Y-%m-%d'))
        self.fecha_fin.set(hoy.strftime('%Y-%m-%d'))
    
    def _validar_fechas(self):
        try:
            fecha_inicio = datetime.strptime(self.fecha_inicio.get(), '%Y-%m-%d')
            fecha_fin = datetime.strptime(self.fecha_fin.get(), '%Y-%m-%d')
            
            if fecha_inicio > fecha_fin:
                messagebox.showerror("Error", "La fecha de inicio no puede ser mayor que la fecha fin")
                return False
            
            return True
        except ValueError:
            messagebox.showerror("Error", "Formato de fecha inválido. Use YYYY-MM-DD")
            return False
    
    def _generar_reporte_ventas(self):
        if not self._validar_fechas():
            return
        
        try:
            self.status_label.config(text="Generando reporte de ventas...")
            self.window.update()
            
            # Generar el reporte
            archivo_pdf = self.report_generator.generar_reporte_ventas(
                self.fecha_inicio.get(), 
                self.fecha_fin.get()
            )
            
            if archivo_pdf and os.path.exists(archivo_pdf):
                self.status_label.config(text=f"Reporte generado: {archivo_pdf}")
                
                # Preguntar si desea abrir el archivo
                if messagebox.askyesno("Reporte Generado", 
                                     f"Reporte generado exitosamente:\n{archivo_pdf}\n\n¿Desea abrirlo ahora?"):
                    self._abrir_archivo(archivo_pdf)
            else:
                self.status_label.config(text="Error al generar el reporte")
                messagebox.showerror("Error", "No se pudo generar el reporte de ventas")
                
        except Exception as e:
            self.status_label.config(text="Error al generar reporte")
            messagebox.showerror("Error", f"Error al generar el reporte: {str(e)}")
    
    def _generar_reporte_inventario(self):
        try:
            self.status_label.config(text="Generando reporte de inventario...")
            self.window.update()
            
            if self.tipo_inventario.get() == "bajo_stock":
                archivo_pdf = self.report_generator.generar_reporte_productos_bajo_stock()
            else:
                # Para inventario completo, podríamos agregar otro método al ReportGenerator
                messagebox.showinfo("Información", "Reporte de inventario completo no implementado aún")
                return
            
            if archivo_pdf and os.path.exists(archivo_pdf):
                self.status_label.config(text=f"Reporte generado: {archivo_pdf}")
                
                if messagebox.askyesno("Reporte Generado", 
                                     f"Reporte generado exitosamente:\n{archivo_pdf}\n\n¿Desea abrirlo ahora?"):
                    self._abrir_archivo(archivo_pdf)
            else:
                self.status_label.config(text="Error al generar el reporte")
                messagebox.showerror("Error", "No se pudo generar el reporte de inventario")
                
        except Exception as e:
            self.status_label.config(text="Error al generar reporte")
            messagebox.showerror("Error", f"Error al generar el reporte: {str(e)}")
    
    def _generar_reporte_clientes(self):
        try:
            self.status_label.config(text="Generando reporte de clientes...")
            self.window.update()
            
            archivo_pdf = self.report_generator.generar_reporte_clientes()
            
            if archivo_pdf and os.path.exists(archivo_pdf):
                self.status_label.config(text=f"Reporte generado: {archivo_pdf}")
                
                if messagebox.askyesno("Reporte Generado", 
                                     f"Reporte generado exitosamente:\n{archivo_pdf}\n\n¿Desea abrirlo ahora?"):
                    self._abrir_archivo(archivo_pdf)
            else:
                self.status_label.config(text="Error al generar el reporte")
                messagebox.showerror("Error", "No se pudo generar el reporte de clientes")
                
        except Exception as e:
            self.status_label.config(text="Error al generar reporte")
            messagebox.showerror("Error", f"Error al generar el reporte: {str(e)}")
    
    def _abrir_archivo(self, archivo_path):
        """Abre el archivo PDF con el visor predeterminado del sistema"""
        try:
            if platform.system() == 'Windows':
                os.startfile(archivo_path)
            elif platform.system() == 'Darwin':  # macOS
                subprocess.run(['open', archivo_path])
            else:  # Linux
                subprocess.run(['xdg-open', archivo_path])
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir el archivo: {str(e)}")