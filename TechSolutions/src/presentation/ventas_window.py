import tkinter as tk
from tkinter import ttk, messagebox
from src.domain.services.venta_service import VentaService
from src.domain.services.cliente_service import ClienteService
from src.domain.services.producto_service import ProductoService

class VentasWindow:
    def __init__(self, parent, auth_service):
        self.parent = parent
        self.auth_service = auth_service
        self.venta_service = VentaService()
        self.cliente_service = ClienteService()
        self.producto_service = ProductoService()
        
        self.carrito = []
        
        self._create_window()
        self._load_clientes()
        self._load_productos()
    
    def _create_window(self):
        self.window = tk.Toplevel(self.parent)
        self.window.title("Registro de Ventas")
        self.window.geometry("1000x700")
        self.window.transient(self.parent)
        self.window.grab_set()
        
        # Frame principal
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.pack(fill='both', expand=True)
        
        # Sección de datos de la venta
        venta_frame = ttk.LabelFrame(main_frame, text="Datos de la Venta", padding="10")
        venta_frame.pack(fill='x', pady=(0, 10))
        
        # Cliente
        ttk.Label(venta_frame, text="Cliente:").grid(row=0, column=0, sticky='w', pady=5)
        self.cliente_combo = ttk.Combobox(venta_frame, width=40, state='readonly')
        self.cliente_combo.grid(row=0, column=1, sticky='w', pady=5, padx=(10, 0))
        
        # Sección para agregar productos
        productos_frame = ttk.LabelFrame(main_frame, text="Agregar Productos", padding="10")
        productos_frame.pack(fill='x', pady=(0, 10))
        
        ttk.Label(productos_frame, text="Producto:").grid(row=0, column=0, sticky='w', pady=5)
        self.producto_combo = ttk.Combobox(productos_frame, width=30, state='readonly')
        self.producto_combo.grid(row=0, column=1, sticky='w', pady=5, padx=(10, 0))
        
        ttk.Label(productos_frame, text="Cantidad:").grid(row=0, column=2, sticky='w', pady=5, padx=(20, 0))
        self.cantidad_entry = ttk.Entry(productos_frame, width=10)
        self.cantidad_entry.grid(row=0, column=3, sticky='w', pady=5, padx=(10, 0))
        
        ttk.Button(productos_frame, text="Agregar al Carrito", 
                  command=self._agregar_al_carrito).grid(row=0, column=4, sticky='w', pady=5, padx=(20, 0))
        
        # Carrito de compras
        carrito_frame = ttk.LabelFrame(main_frame, text="Carrito de Compra", padding="10")
        carrito_frame.pack(fill='both', expand=True, pady=(0, 10))
        
        # Treeview para el carrito
        columns = ('Producto', 'Precio Unitario', 'Cantidad', 'Subtotal')
        self.carrito_tree = ttk.Treeview(carrito_frame, columns=columns, show='headings')
        
        for col in columns:
            self.carrito_tree.heading(col, text=col)
            self.carrito_tree.column(col, width=120)
        
        self.carrito_tree.column('Producto', width=200)
        
        scrollbar = ttk.Scrollbar(carrito_frame, orient='vertical', command=self.carrito_tree.yview)
        self.carrito_tree.configure(yscrollcommand=scrollbar.set)
        
        self.carrito_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Botón para quitar del carrito
        ttk.Button(carrito_frame, text="Quitar Seleccionado", 
                  command=self._quitar_del_carrito).pack(side='bottom', pady=(10, 0))
        
        # Totales
        totales_frame = ttk.Frame(main_frame)
        totales_frame.pack(fill='x', pady=(0, 10))
        
        self.subtotal_label = ttk.Label(totales_frame, text="Subtotal: $0.00", font=("Arial", 10, "bold"))
        self.subtotal_label.pack(side='left', padx=(0, 20))
        
        self.impuesto_label = ttk.Label(totales_frame, text="Impuesto (10%): $0.00", font=("Arial", 10, "bold"))
        self.impuesto_label.pack(side='left', padx=(0, 20))
        
        self.total_label = ttk.Label(totales_frame, text="Total: $0.00", font=("Arial", 12, "bold"))
        self.total_label.pack(side='left')
        
        # Botones de acción
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill='x')
        
        ttk.Button(button_frame, text="Procesar Venta", 
                  command=self._procesar_venta, style='Accent.TButton').pack(side='left', padx=(0, 10))
        ttk.Button(button_frame, text="Limpiar Carrito", 
                  command=self._limpiar_carrito).pack(side='left', padx=(0, 10))
        ttk.Button(button_frame, text="Cancelar", 
                  command=self.window.destroy).pack(side='left')
        
        # Actualizar totales
        self._actualizar_totales()
    
    def _load_clientes(self):
        clientes = self.cliente_service.obtener_todos()
        cliente_options = [f"{cliente.id} - {cliente.nombre}" for cliente in clientes]
        self.cliente_combo['values'] = cliente_options
        if cliente_options:
            self.cliente_combo.current(0)
    
    def _load_productos(self):
        productos = self.producto_service.obtener_todos()
        producto_options = [f"{producto.id} - {producto.nombre} (Stock: {producto.stock})" for producto in productos]
        self.producto_combo['values'] = producto_options
        if producto_options:
            self.producto_combo.current(0)
    
    def _agregar_al_carrito(self):
        try:
            producto_seleccionado = self.producto_combo.get()
            cantidad_text = self.cantidad_entry.get().strip()
            
            if not producto_seleccionado or not cantidad_text:
                messagebox.showwarning("Advertencia", "Seleccione un producto y ingrese la cantidad")
                return
            
            cantidad = int(cantidad_text)
            if cantidad <= 0:
                messagebox.showwarning("Advertencia", "La cantidad debe ser mayor a 0")
                return
            
            # Obtener ID del producto
            producto_id = int(producto_seleccionado.split(' - ')[0])
            producto = self.producto_service.obtener_por_id(producto_id)
            
            if not producto:
                messagebox.showerror("Error", "Producto no encontrado")
                return
            
            if producto.stock < cantidad:
                messagebox.showerror("Error", f"Stock insuficiente. Stock disponible: {producto.stock}")
                return
            
            # Verificar si el producto ya está en el carrito
            for item in self.carrito:
                if item['producto'].id == producto.id:
                    messagebox.showwarning("Advertencia", "El producto ya está en el carrito")
                    return
            
            # Agregar al carrito
            subtotal = producto.precio * cantidad
            self.carrito.append({
                'producto': producto,
                'cantidad': cantidad,
                'subtotal': subtotal
            })
            
            # Agregar al treeview
            self.carrito_tree.insert('', 'end', values=(
                producto.nombre,
                f"${producto.precio:.2f}",
                cantidad,
                f"${subtotal:.2f}"
            ))
            
            # Actualizar totales
            self._actualizar_totales()
            
            # Limpiar campos
            self.cantidad_entry.delete(0, tk.END)
            
        except ValueError:
            messagebox.showerror("Error", "La cantidad debe ser un número válido")
    
    def _quitar_del_carrito(self):
        selected_item = self.carrito_tree.selection()
        if not selected_item:
            messagebox.showwarning("Advertencia", "Seleccione un producto para quitar")
            return
        
        # Obtener índice del item seleccionado
        index = self.carrito_tree.index(selected_item[0])
        
        # Remover del carrito y del treeview
        self.carrito.pop(index)
        self.carrito_tree.delete(selected_item[0])
        
        # Actualizar totales
        self._actualizar_totales()
    
    def _actualizar_totales(self):
        subtotal = sum(item['subtotal'] for item in self.carrito)
        impuesto = subtotal * 0.10  # 10% de impuesto
        total = subtotal + impuesto
        
        self.subtotal_label.config(text=f"Subtotal: ${subtotal:.2f}")
        self.impuesto_label.config(text=f"Impuesto (10%): ${impuesto:.2f}")
        self.total_label.config(text=f"Total: ${total:.2f}")
    
    def _limpiar_carrito(self):
        self.carrito.clear()
        for item in self.carrito_tree.get_children():
            self.carrito_tree.delete(item)
        self._actualizar_totales()
    
    def _procesar_venta(self):
        if not self.carrito:
            messagebox.showwarning("Advertencia", "El carrito está vacío")
            return
        
        cliente_seleccionado = self.cliente_combo.get()
        if not cliente_seleccionado:
            messagebox.showwarning("Advertencia", "Seleccione un cliente")
            return
        
        # Obtener ID del cliente
        cliente_id = int(cliente_seleccionado.split(' - ')[0])
        
        # Calcular totales
        subtotal = sum(item['subtotal'] for item in self.carrito)
        impuesto = subtotal * 0.10
        total = subtotal + impuesto
        
        # Preparar datos de la venta
        venta_data = {
            'cliente_id': cliente_id,
            'usuario_id': self.auth_service.obtener_usuario_actual().id,
            'subtotal': subtotal,
            'impuesto': impuesto,
            'total': total,
            'detalles': []
        }
        
        for item in self.carrito:
            venta_data['detalles'].append({
                'producto_id': item['producto'].id,
                'cantidad': item['cantidad'],
                'precio_unitario': item['producto'].precio,
                'subtotal': item['subtotal']
            })
        
        # Procesar la venta
        try:
            resultado = self.venta_service.procesar_venta(venta_data)
            if resultado['success']:
                messagebox.showinfo("Éxito", f"Venta procesada correctamente\nNúmero de Factura: {resultado['numero_factura']}")
                self._limpiar_carrito()
                self.window.destroy()
            else:
                messagebox.showerror("Error", f"No se pudo procesar la venta: {resultado['error']}")
        except Exception as e:
            messagebox.showerror("Error", f"Error al procesar la venta: {str(e)}")