import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
from datetime import datetime, timedelta

# Cambiar estas líneas de importación
try:
    from .clientes_window import ClientesWindow
    from .productos_window import ProductosWindow
    from .ventas_window import VentasWindow
    from .reportes_window import ReportesWindow
except ImportError:
    # Si falla la importación relativa, usar absoluta
    from src.presentation.clientes_window import ClientesWindow
    from src.presentation.productos_window import ProductosWindow
    from src.presentation.ventas_window import VentasWindow
    from src.presentation.reportes_window import ReportesWindow

from src.domain.services.auth_service import AuthService
from src.domain.services.venta_service import VentaService
from src.domain.services.producto_service import ProductoService

class MainWindow:
    def __init__(self, usuario):
        self.usuario = usuario
        self.root = tk.Tk()
        self.root.title(f"Tech Solutions - Sistema de Gestión")
        self.root.geometry("1000x700")
        self.root.state('zoomed')  # Maximizada
        
        self.auth_service = AuthService()
        self.auth_service.usuario_actual = usuario
        self.venta_service = VentaService()
        self.producto_service = ProductoService()
        
        self._create_menu()
        self._create_widgets()
        self._create_status_bar()
        
        # Timer para actualizaciones automáticas
        self._setup_timer()
    
    @staticmethod
    def center_window(window):
        """Centra cualquier ventana en la pantalla."""
        window.update_idletasks()
        width = window.winfo_width()
        height = window.winfo_height()
        x = (window.winfo_screenwidth() // 2) - (width // 2)
        y = (window.winfo_screenheight() // 2) - (height // 2)
        window.geometry(f'{width}x{height}+{x}+{y}')
    
    def _create_menu(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # Menú Archivo
        archivo_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Archivo", menu=archivo_menu)
        archivo_menu.add_command(label="Salir", command=self.root.quit)
        
        # Menú Gestión
        gestion_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Gestión", menu=gestion_menu)
        gestion_menu.add_command(label="Clientes", command=self._abrir_clientes)
        gestion_menu.add_command(label="Productos", command=self._abrir_productos)
        gestion_menu.add_command(label="Ventas", command=self._abrir_ventas)
        
        # Menú Reportes
        reportes_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Reportes", menu=reportes_menu)
        reportes_menu.add_command(label="Reporte de Ventas", command=self._generar_reporte_ventas)
        reportes_menu.add_command(label="Reporte de Inventario", command=self._generar_reporte_inventario)
        
        # Menú Sistema
        sistema_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Sistema", menu=sistema_menu)
        sistema_menu.add_command(label="Cambiar Usuario", command=self._cambiar_usuario)
        sistema_menu.add_command(label="Acerca de", command=self._mostrar_acerca_de)
    
    def _create_widgets(self):
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configurar grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Banner de bienvenida
        welcome_frame = ttk.Frame(main_frame, relief='raised', padding="10")
        welcome_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        welcome_label = tk.Label(
            welcome_frame,
            text=f"Bienvenido, {self.usuario.nombre}",
            font=("Arial", 14, "bold"),
            fg="#2c3e50"
        )
        welcome_label.pack()
        
        # Panel de acceso rápido
        quick_access_frame = ttk.LabelFrame(main_frame, text="Acceso Rápido", padding="10")
        quick_access_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        
        # Botones de acceso rápido
        ttk.Button(
            quick_access_frame,
            text="Gestión de Clientes",
            command=self._abrir_clientes,
            width=20
        ).pack(pady=5)
        
        ttk.Button(
            quick_access_frame,
            text="Gestión de Productos",
            command=self._abrir_productos,
            width=20
        ).pack(pady=5)
        
        ttk.Button(
            quick_access_frame,
            text="Registro de Ventas",
            command=self._abrir_ventas,
            width=20
        ).pack(pady=5)
        
        ttk.Button(
            quick_access_frame,
            text="Reportes",
            command=self._generar_reporte_ventas,
            width=20
        ).pack(pady=5)
        
        # Área de dashboard
        dashboard_frame = ttk.LabelFrame(main_frame, text="Dashboard", padding="10")
        dashboard_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Contenido del dashboard
        self._create_dashboard(dashboard_frame)
    
    def _create_dashboard(self, parent):
        # Frame principal para el dashboard
        dashboard_main_frame = ttk.Frame(parent)
        dashboard_main_frame.pack(fill='both', expand=True)
        
        # Frame superior para métricas
        metrics_frame = ttk.Frame(dashboard_main_frame)
        metrics_frame.pack(fill='x', expand=False, pady=(0, 10))
        
        # Ejemplo de métricas
        metrics = [
            ("Ventas del Mes", "$15,250"),
            ("Clientes Activos", "142"),
            ("Productos en Stock", "856"),
            ("Ventas Pendientes", "23")
        ]
        
        for i, (title, value) in enumerate(metrics):
            metric_frame = ttk.Frame(metrics_frame, relief='solid', padding="10")
            metric_frame.grid(row=0, column=i, padx=5, pady=5, sticky=(tk.W, tk.E, tk.N, tk.S))
            
            ttk.Label(metric_frame, text=title, font=("Arial", 10)).pack()
            ttk.Label(metric_frame, text=value, font=("Arial", 16, "bold")).pack()
        
        for i in range(4):
            metrics_frame.columnconfigure(i, weight=1)
        metrics_frame.rowconfigure(0, weight=1)
        
        # Frame inferior para gráficos
        charts_frame = ttk.Frame(dashboard_main_frame)
        charts_frame.pack(fill='both', expand=True)
        
        # Crear gráficos
        self._create_ventas_chart(charts_frame)
        self._create_productos_chart(charts_frame)
    
    def _create_ventas_chart(self, parent):
        # Frame para el gráfico de ventas
        ventas_frame = ttk.LabelFrame(parent, text="Ventas por Mes")
        ventas_frame.grid(row=0, column=0, padx=10, pady=10, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Datos de ejemplo para el gráfico
        meses = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun']
        ventas = [12500, 9800, 14200, 15250, 10300, 16700]
        
        # Crear figura y ejes
        fig, ax = plt.subplots(figsize=(5, 4))
        ax.bar(meses, ventas, color='#3498db')
        ax.set_title('Ventas Mensuales')
        ax.set_ylabel('Ventas ($)')
        ax.grid(axis='y', linestyle='--', alpha=0.7)
        
        # Añadir el gráfico al frame
        canvas = FigureCanvasTkAgg(fig, master=ventas_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True)
    
    def _create_productos_chart(self, parent):
        # Frame para el gráfico de productos
        productos_frame = ttk.LabelFrame(parent, text="Productos más Vendidos")
        productos_frame.grid(row=0, column=1, padx=10, pady=10, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Datos de ejemplo para el gráfico
        productos = ['Auriculares', 'Monitores', 'Teclados', 'Mouse', 'Cámaras']
        cantidades = [42, 35, 28, 25, 20]
        
        # Crear figura y ejes
        fig, ax = plt.subplots(figsize=(5, 4))
        ax.pie(cantidades, labels=productos, autopct='%1.1f%%', startangle=90, 
               shadow=True, explode=[0.05, 0, 0, 0, 0])
        ax.set_title('Productos más Vendidos')
        
        # Añadir el gráfico al frame
        canvas = FigureCanvasTkAgg(fig, master=productos_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True)
        
        # Configurar el grid para que los gráficos se expandan
        parent.columnconfigure(0, weight=1)
        parent.columnconfigure(1, weight=1)
        parent.rowconfigure(0, weight=1)
    
    def _create_status_bar(self):
        status_bar = ttk.Frame(self.root, relief='sunken')
        status_bar.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        user_info = f"Usuario: {self.usuario.nombre} | Nivel: {self.obtener_nivel_texto(self.usuario.nivel_acceso)}"
        ttk.Label(status_bar, text=user_info).pack(side=tk.LEFT, padx=5)
        
        from datetime import datetime
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ttk.Label(status_bar, text=f"Última actualización: {current_time}").pack(side=tk.RIGHT, padx=5)
    
    def obtener_nivel_texto(self, nivel):
        niveles = {1: "Operador", 2: "Supervisor", 3: "Administrador"}
        return niveles.get(nivel, "Desconocido")
    
    def _setup_timer(self):
        def update_time():
            from datetime import datetime
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            # Aquí puedes actualizar el status bar o hacer otras actualizaciones automáticas
            self.root.after(60000, update_time)  # Actualizar cada minuto
        
        update_time()
    
    def _abrir_clientes(self):
        if self.auth_service.verificar_acceso(1):  # Nivel mínimo requerido: Operador
            ClientesWindow(self.root, self.auth_service)
        else:
            messagebox.showerror("Acceso Denegado", "No tiene permisos para acceder a esta función")
    
    def _abrir_productos(self):
        if self.auth_service.verificar_acceso(1):
            ProductosWindow(self.root, self.auth_service)
        else:
            messagebox.showerror("Acceso Denegado", "No tiene permisos para acceder a esta función")
    
    def _abrir_ventas(self):
        if self.auth_service.verificar_acceso(1):
            VentasWindow(self.root, self.auth_service)
        else:
            messagebox.showerror("Acceso Denegado", "No tiene permisos para acceder a esta función")
    
    def _generar_reporte_ventas(self):
        if self.auth_service.verificar_acceso(2):  # Nivel mínimo requerido: Supervisor
            ReportesWindow(self.root, self.auth_service)
        else:
            messagebox.showerror("Acceso Denegado", "No tiene permisos para generar reportes")
    
    def _generar_reporte_inventario(self):
        if self.auth_service.verificar_acceso(2):
            ReportesWindow(self.root, self.auth_service)
        else:
            messagebox.showerror("Acceso Denegado", "No tiene permisos para generar reportes")
    
    def _cambiar_usuario(self):
        self.root.destroy()
        from main import main
        main()
    
    def _mostrar_acerca_de(self):
        messagebox.showinfo("Acerca de", 
            "Tech Solutions - Sistema de Gestión\n"
            "Versión 1.0.0\n"
            "Desarrollado con Python y Tkinter\n"
            "Arquitectura N-Capas"
        )
    
    def run(self):
        self.root.mainloop()