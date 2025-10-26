import tkinter as tk
from tkinter import ttk, messagebox
from src.domain.services.producto_service import ProductoService

class ProductosWindow:
    def __init__(self, parent, auth_service):
        self.parent = parent
        self.auth_service = auth_service
        self.producto_service = ProductoService()
        
        self._create_window()
        self._load_productos()
    
    def _create_window(self):
        self.window = tk.Toplevel(self.parent)
        self.window.title("Gestión de Productos")
        self.window.geometry("900x600")
        self.window.transient(self.parent)
        self.window.grab_set()
        
        # Frame principal
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.pack(fill='both', expand=True)
        
        # Barra de herramientas
        toolbar_frame = ttk.Frame(main_frame)
        toolbar_frame.pack(fill='x', pady=(0, 10))
        
        ttk.Button(toolbar_frame, text="Nuevo Producto", 
                  command=self._nuevo_producto).pack(side='left', padx=(0, 5))
        ttk.Button(toolbar_frame, text="Editar", 
                  command=self._editar_producto).pack(side='left', padx=(0, 5))
        ttk.Button(toolbar_frame, text="Eliminar", 
                  command=self._eliminar_producto).pack(side='left', padx=(0, 5))
        ttk.Button(toolbar_frame, text="Actualizar", 
                  command=self._load_productos).pack(side='left')
        
        # Treeview para lista de productos
        columns = ('ID', 'Código', 'Nombre', 'Precio', 'Stock', 'Stock Mínimo')
        self.tree = ttk.Treeview(main_frame, columns=columns, show='headings')
        
        # Configurar columnas
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)
        
        self.tree.column('Nombre', width=200)
        self.tree.column('Código', width=120)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(main_frame, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Bind double click
        self.tree.bind('<Double-1>', self._editar_producto)
    
    def _load_productos(self):
        # Limpiar treeview
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Cargar productos
        productos = self.producto_service.obtener_todos()
        for producto in productos:
            self.tree.insert('', 'end', values=(
                producto.id,
                producto.codigo,
                producto.nombre,
                f"${producto.precio:.2f}",
                producto.stock,
                producto.stock_minimo
            ))
    
    def _nuevo_producto(self):
        self._mostrar_formulario_producto()
    
    def _editar_producto(self, event=None):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Advertencia", "Seleccione un producto para editar")
            return
        
        producto_id = self.tree.item(selected_item[0])['values'][0]
        producto = self.producto_service.obtener_por_id(producto_id)
        
        if producto:
            self._mostrar_formulario_producto(producto)
    
    def _eliminar_producto(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Advertencia", "Seleccione un producto para eliminar")
            return
        
        producto_id = self.tree.item(selected_item[0])['values'][0]
        producto_nombre = self.tree.item(selected_item[0])['values'][2]
        
        if messagebox.askyesno("Confirmar", f"¿Está seguro de eliminar el producto {producto_nombre}?"):
            if self.producto_service.eliminar_producto(producto_id):
                messagebox.showinfo("Éxito", "Producto eliminado correctamente")
                self._load_productos()
            else:
                messagebox.showerror("Error", "No se pudo eliminar el producto")
    
    def _mostrar_formulario_producto(self, producto=None):
        form_window = tk.Toplevel(self.window)
        form_window.title("Nuevo Producto" if not producto else "Editar Producto")
        form_window.geometry("400x400")
        form_window.transient(self.window)
        form_window.grab_set()
        
        # Frame principal
        main_frame = ttk.Frame(form_window, padding="20")
        main_frame.pack(fill='both', expand=True)
        
        # Campos del formulario
        ttk.Label(main_frame, text="Código:").grid(row=0, column=0, sticky='w', pady=5)
        codigo_entry = ttk.Entry(main_frame, width=30)
        codigo_entry.grid(row=0, column=1, sticky='w', pady=5, padx=(10, 0))
        
        ttk.Label(main_frame, text="Nombre:").grid(row=1, column=0, sticky='w', pady=5)
        nombre_entry = ttk.Entry(main_frame, width=30)
        nombre_entry.grid(row=1, column=1, sticky='w', pady=5, padx=(10, 0))
        
        ttk.Label(main_frame, text="Descripción:").grid(row=2, column=0, sticky='w', pady=5)
        descripcion_text = tk.Text(main_frame, width=30, height=4)
        descripcion_text.grid(row=2, column=1, sticky='w', pady=5, padx=(10, 0))
        
        ttk.Label(main_frame, text="Precio:").grid(row=3, column=0, sticky='w', pady=5)
        precio_entry = ttk.Entry(main_frame, width=30)
        precio_entry.grid(row=3, column=1, sticky='w', pady=5, padx=(10, 0))
        
        ttk.Label(main_frame, text="Stock:").grid(row=4, column=0, sticky='w', pady=5)
        stock_entry = ttk.Entry(main_frame, width=30)
        stock_entry.grid(row=4, column=1, sticky='w', pady=5, padx=(10, 0))
        
        ttk.Label(main_frame, text="Stock Mínimo:").grid(row=5, column=0, sticky='w', pady=5)
        stock_minimo_entry = ttk.Entry(main_frame, width=30)
        stock_minimo_entry.grid(row=5, column=1, sticky='w', pady=5, padx=(10, 0))
        
        # Si estamos editando, cargar datos
        if producto:
            codigo_entry.insert(0, producto.codigo)
            nombre_entry.insert(0, producto.nombre)
            descripcion_text.insert('1.0', producto.descripcion or '')
            precio_entry.insert(0, str(producto.precio))
            stock_entry.insert(0, str(producto.stock))
            stock_minimo_entry.insert(0, str(producto.stock_minimo))
        
        # Botones
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=6, column=0, columnspan=2, pady=20)
        
        def guardar_producto():
            try:
                codigo = codigo_entry.get().strip()
                nombre = nombre_entry.get().strip()
                precio = float(precio_entry.get().strip())
                stock = int(stock_entry.get().strip())
                stock_minimo = int(stock_minimo_entry.get().strip())
                
                if not codigo or not nombre:
                    messagebox.showerror("Error", "Código y nombre son obligatorios")
                    return
                
                datos_producto = {
                    'codigo': codigo,
                    'nombre': nombre,
                    'descripcion': descripcion_text.get('1.0', 'end-1c').strip() or None,
                    'precio': precio,
                    'stock': stock,
                    'stock_minimo': stock_minimo
                }
                
                if producto:
                    # Actualizar
                    if self.producto_service.actualizar_producto(producto.id, datos_producto):
                        messagebox.showinfo("Éxito", "Producto actualizado correctamente")
                        form_window.destroy()
                        self._load_productos()
                    else:
                        messagebox.showerror("Error", "No se pudo actualizar el producto")
                else:
                    # Crear nuevo
                    if self.producto_service.crear_producto(datos_producto):
                        messagebox.showinfo("Éxito", "Producto creado correctamente")
                        form_window.destroy()
                        self._load_productos()
                    else:
                        messagebox.showerror("Error", "No se pudo crear el producto")
            
            except ValueError:
                messagebox.showerror("Error", "Precio, stock y stock mínimo deben ser números válidos")
        
        ttk.Button(button_frame, text="Guardar", 
                  command=guardar_producto).pack(side='left', padx=(0, 10))
        ttk.Button(button_frame, text="Cancelar", 
                  command=form_window.destroy).pack(side='left')
        
        # Focus en el primer campo
        codigo_entry.focus()