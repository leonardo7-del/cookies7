import tkinter as tk
from tkinter import ttk, messagebox
from src.domain.services.venta_service import VentaService
from src.domain.services.cliente_service import ClienteService
from src.domain.services.producto_service import ProductoService
from src.domain.entities.venta import Venta
from src.domain.entities.venta_detalle import VentaDetalle
from src.domain.entities.cliente import Cliente
from src.domain.entities.usuario import Usuario

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
        
        # Centrar ventana
        from src.presentation.main_window import MainWindow
        MainWindow.center_window(self.window)
        
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
            
            # Verificar si producto es un diccionario o un objeto
            if isinstance(producto, dict):
                if producto['stock'] < cantidad:
                    messagebox.showerror("Error", f"Stock insuficiente. Stock disponible: {producto['stock']}")
                    return
                
                # Verificar si el producto ya está en el carrito
                for item in self.carrito:
                    if item['producto']['id'] == producto['id']:
                        messagebox.showwarning("Advertencia", "El producto ya está en el carrito")
                        return
                
                # Agregar al carrito
                subtotal = producto['precio'] * cantidad
                self.carrito.append({
                    'producto': producto,
                    'cantidad': cantidad,
                    'subtotal': subtotal
                })
            else:
                # Manejo para objeto
                if producto.stock < cantidad:
                    messagebox.showerror("Error", f"Stock insuficiente. Stock disponible: {producto.stock}")
                    return
                
                # Verificar si el producto ya está en el carrito
                for item in self.carrito:
                    if isinstance(item['producto'], dict):
                        if item['producto']['id'] == producto.id:
                            messagebox.showwarning("Advertencia", "El producto ya está en el carrito")
                            return
                    else:
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
            nombre_producto = producto['nombre'] if isinstance(producto, dict) else producto.nombre
            precio_producto = producto['precio'] if isinstance(producto, dict) else producto.precio
            
            self.carrito_tree.insert('', 'end', values=(
                nombre_producto,
                f"${precio_producto:.2f}",
                cantidad,
                f"${subtotal:.2f}"
            ))
            
            # Asegurar que los elementos sean visibles
            self.carrito_tree.yview_moveto(1.0)  # Desplazar a la última fila
            
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
        # Convertir a float para evitar problemas con Decimal
        if hasattr(subtotal, 'to_float'):
            subtotal = subtotal.to_float()
        elif hasattr(subtotal, '__float__'):
            subtotal = float(subtotal)
            
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
        
        # Crear objetos de entidades
        cliente = Cliente(id=cliente_id)
        
        # Obtener el usuario actual completo
        usuario_actual = self.auth_service.obtener_usuario_actual()
        
        # Crear la venta
        venta = Venta(
            cliente=cliente,
            usuario=usuario_actual
        )
        
        # Agregar detalles de la venta
        for item in self.carrito:
            producto = item['producto']
            
            # Verificar si producto es un diccionario o un objeto
            if isinstance(producto, dict):
                producto_id = producto['id']
                precio_unitario = producto['precio']
            else:
                producto_id = producto.id
                precio_unitario = producto.precio
                
            # Crear el detalle con los valores correctos
            detalle = VentaDetalle(
                producto_id=producto_id,
                cantidad=item['cantidad'],
                precio_unitario=precio_unitario,
                subtotal=item['subtotal']
            )
            # Asignar el producto completo para referencia
            detalle.producto = producto
            venta.agregar_detalle(detalle)
        
        # Procesar la venta
        try:
            resultado = self.venta_service.procesar_venta(venta)
            if resultado['success']:
                messagebox.showinfo("Éxito", f"Venta procesada correctamente\nNúmero de Factura: {resultado['numero_factura']}")
                self._limpiar_carrito()
                self._load_productos()  # Recargar productos para actualizar stock
                self.window.destroy()
            else:
                messagebox.showerror("Error", f"No se pudo procesar la venta: {resultado['error']}")
        except Exception as e:
            messagebox.showerror("Error", f"Error al procesar la venta: {str(e)}")