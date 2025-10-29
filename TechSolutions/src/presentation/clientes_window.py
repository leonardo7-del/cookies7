import tkinter as tk
from tkinter import ttk, messagebox
from src.domain.services.cliente_service import ClienteService

class ClientesWindow:
    def __init__(self, parent, auth_service):
        self.parent = parent
        self.auth_service = auth_service
        self.cliente_service = ClienteService()
        
        self._create_window()
        self._load_clientes()
    
    def _create_window(self):
        self.window = tk.Toplevel(self.parent)
        self.window.title("Gestión de Clientes")
        self.window.geometry("800x600")
        self.window.transient(self.parent)
        self.window.grab_set()
        
        # Centrar ventana
        from src.presentation.main_window import MainWindow
        MainWindow.center_window(self.window)
        
        # Frame principal
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.pack(fill='both', expand=True)
        
        # Barra de herramientas
        toolbar_frame = ttk.Frame(main_frame)
        toolbar_frame.pack(fill='x', pady=(0, 10))
        
        ttk.Button(toolbar_frame, text="Nuevo Cliente", 
                  command=self._nuevo_cliente).pack(side='left', padx=(0, 5))
        ttk.Button(toolbar_frame, text="Editar", 
                  command=self._editar_cliente).pack(side='left', padx=(0, 5))
        ttk.Button(toolbar_frame, text="Eliminar", 
                  command=self._eliminar_cliente).pack(side='left', padx=(0, 5))
        ttk.Button(toolbar_frame, text="Actualizar", 
                  command=self._load_clientes).pack(side='left')
        
        # Búsqueda
        search_frame = ttk.Frame(toolbar_frame)
        search_frame.pack(side='right')
        
        ttk.Label(search_frame, text="Buscar:").pack(side='left')
        self.search_entry = ttk.Entry(search_frame, width=20)
        self.search_entry.pack(side='left', padx=(5, 0))
        self.search_entry.bind('<KeyRelease>', self._buscar_clientes)
        
        # Treeview para lista de clientes
        columns = ('ID', 'Nombre', 'Email', 'Teléfono', 'RUC')
        self.tree = ttk.Treeview(main_frame, columns=columns, show='headings')
        
        # Configurar columnas
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)
        
        self.tree.column('Nombre', width=200)
        self.tree.column('Email', width=150)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(main_frame, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Bind double click
        self.tree.bind('<Double-1>', self._editar_cliente)
    
    def _load_clientes(self):
        # Limpiar treeview
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Cargar clientes
        clientes = self.cliente_service.obtener_todos()
        for cliente in clientes:
            self.tree.insert('', 'end', values=(
                cliente.id,
                cliente.nombre,
                cliente.email or '',
                cliente.telefono or '',
                cliente.ruc or ''
            ))
    
    def _buscar_clientes(self, event=None):
        search_term = self.search_entry.get().strip()
        if not search_term:
            self._load_clientes()
            return
        
        # Limpiar treeview
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Buscar clientes
        clientes = self.cliente_service.buscar_por_nombre(search_term)
        for cliente in clientes:
            self.tree.insert('', 'end', values=(
                cliente.id,
                cliente.nombre,
                cliente.email or '',
                cliente.telefono or '',
                cliente.ruc or ''
            ))
    
    def _nuevo_cliente(self):
        self._mostrar_formulario_cliente()
    
    def _editar_cliente(self, event=None):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Advertencia", "Seleccione un cliente para editar")
            return
        
        cliente_id = self.tree.item(selected_item[0])['values'][0]
        cliente = self.cliente_service.obtener_por_id(cliente_id)
        
        if cliente:
            self._mostrar_formulario_cliente(cliente)
    
    def _eliminar_cliente(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Advertencia", "Seleccione un cliente para eliminar")
            return
        
        cliente_id = self.tree.item(selected_item[0])['values'][0]
        cliente_nombre = self.tree.item(selected_item[0])['values'][1]
        
        if messagebox.askyesno("Confirmar", f"¿Está seguro de eliminar al cliente {cliente_nombre}?"):
            if self.cliente_service.eliminar_cliente(cliente_id):
                messagebox.showinfo("Éxito", "Cliente eliminado correctamente")
                self._load_clientes()
            else:
                messagebox.showerror("Error", "No se pudo eliminar el cliente")
    
    def _mostrar_formulario_cliente(self, cliente=None):
        form_window = tk.Toplevel(self.window)
        form_window.title("Nuevo Cliente" if not cliente else "Editar Cliente")
        form_window.geometry("400x300")
        form_window.transient(self.window)
        form_window.grab_set()
        
        # Centrar ventana
        from src.presentation.main_window import MainWindow
        MainWindow.center_window(form_window)
        
        # Frame principal
        main_frame = ttk.Frame(form_window, padding="20")
        main_frame.pack(fill='both', expand=True)
        
        # Campos del formulario
        ttk.Label(main_frame, text="Nombre:").grid(row=0, column=0, sticky='w', pady=5)
        nombre_entry = ttk.Entry(main_frame, width=30)
        nombre_entry.grid(row=0, column=1, sticky='w', pady=5, padx=(10, 0))
        
        ttk.Label(main_frame, text="Email:").grid(row=1, column=0, sticky='w', pady=5)
        email_entry = ttk.Entry(main_frame, width=30)
        email_entry.grid(row=1, column=1, sticky='w', pady=5, padx=(10, 0))
        
        ttk.Label(main_frame, text="Teléfono:").grid(row=2, column=0, sticky='w', pady=5)
        telefono_entry = ttk.Entry(main_frame, width=30)
        telefono_entry.grid(row=2, column=1, sticky='w', pady=5, padx=(10, 0))
        
        ttk.Label(main_frame, text="Dirección:").grid(row=3, column=0, sticky='w', pady=5)
        direccion_text = tk.Text(main_frame, width=30, height=4)
        direccion_text.grid(row=3, column=1, sticky='w', pady=5, padx=(10, 0))
        
        ttk.Label(main_frame, text="RUC:").grid(row=4, column=0, sticky='w', pady=5)
        ruc_entry = ttk.Entry(main_frame, width=30)
        ruc_entry.grid(row=4, column=1, sticky='w', pady=5, padx=(10, 0))
        
        # Si estamos editando, cargar datos
        if cliente:
            nombre_entry.insert(0, cliente.nombre)
            email_entry.insert(0, cliente.email or '')
            telefono_entry.insert(0, cliente.telefono or '')
            direccion_text.insert('1.0', cliente.direccion or '')
            ruc_entry.insert(0, cliente.ruc or '')
        
        # Botones
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=5, column=0, columnspan=2, pady=20)
        
        def guardar_cliente():
            nombre = nombre_entry.get().strip()
            if not nombre:
                messagebox.showerror("Error", "El nombre es obligatorio")
                return
            
            datos_cliente = {
                'nombre': nombre,
                'email': email_entry.get().strip() or None,
                'telefono': telefono_entry.get().strip() or None,
                'direccion': direccion_text.get('1.0', 'end-1c').strip() or None,
                'ruc': ruc_entry.get().strip() or None
            }
            
            if cliente:
                # Actualizar
                if self.cliente_service.actualizar_cliente(cliente.id, datos_cliente):
                    messagebox.showinfo("Éxito", "Cliente actualizado correctamente")
                    form_window.destroy()
                    self._load_clientes()
                else:
                    messagebox.showerror("Error", "No se pudo actualizar el cliente")
            else:
                # Crear nuevo
                if self.cliente_service.crear_cliente(datos_cliente):
                    messagebox.showinfo("Éxito", "Cliente creado correctamente")
                    form_window.destroy()
                    self._load_clientes()
                else:
                    messagebox.showerror("Error", "No se pudo crear el cliente")
        
        ttk.Button(button_frame, text="Guardar", 
                  command=guardar_cliente).pack(side='left', padx=(0, 10))
        ttk.Button(button_frame, text="Cancelar", 
                  command=form_window.destroy).pack(side='left')
        
        # Focus en el primer campo
        nombre_entry.focus()