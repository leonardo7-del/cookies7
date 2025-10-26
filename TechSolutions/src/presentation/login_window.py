import tkinter as tk
from tkinter import messagebox
import sys
import os

# Configurar path para imports
current_dir = os.path.dirname(__file__)
src_dir = os.path.dirname(current_dir)  # Subir a src/
project_root = os.path.dirname(src_dir)  # Subir a TechSolutions/

# Agregar ambos paths
sys.path.insert(0, project_root)
sys.path.insert(0, src_dir)

try:
    from domain.services.auth_service import AuthService
except ImportError as e:
    print(f"Error en importación: {e}")
    # Intentar importación alternativa
    from src.domain.services.auth_service import AuthService

class LoginWindow:
    def __init__(self, root, on_login_success):
        self.root = root
        self.root.title("Tech Solutions - Login")
        self.root.geometry("400x300")
        self.root.resizable(False, False)
        
        self.auth_service = AuthService()
        self.on_login_success = on_login_success
        
        self._create_widgets()
    
    def _create_widgets(self):
        # Frame principal
        main_frame = tk.Frame(self.root, padx=20, pady=20)
        main_frame.pack(expand=True, fill='both')
        
        # Título
        title_label = tk.Label(
            main_frame, 
            text="TECH SOLUTIONS", 
            font=("Arial", 16, "bold"),
            fg="#2c3e50"
        )
        title_label.pack(pady=(0, 20))
        
        subtitle_label = tk.Label(
            main_frame,
            text="Sistema de Gestión",
            font=("Arial", 12),
            fg="#7f8c8d"
        )
        subtitle_label.pack(pady=(0, 30))
        
        # Formulario de login
        form_frame = tk.Frame(main_frame)
        form_frame.pack(fill='x', pady=10)
        
        # Usuario
        tk.Label(form_frame, text="Usuario:", font=("Arial", 10)).grid(
            row=0, column=0, sticky='w', pady=5
        )
        self.username_entry = tk.Entry(form_frame, font=("Arial", 10), width=25)
        self.username_entry.grid(row=0, column=1, padx=10, pady=5)
        
        # Contraseña
        tk.Label(form_frame, text="Contraseña:", font=("Arial", 10)).grid(
            row=1, column=0, sticky='w', pady=5
        )
        self.password_entry = tk.Entry(
            form_frame, 
            font=("Arial", 10), 
            width=25, 
            show='*'
        )
        self.password_entry.grid(row=1, column=1, padx=10, pady=5)
        
        # Botón de login
        login_button = tk.Button(
            main_frame,
            text="Iniciar Sesión",
            font=("Arial", 10, "bold"),
            bg="#3498db",
            fg="white",
            width=15,
            height=2,
            command=self._login
        )
        login_button.pack(pady=20)
        
        # Bind Enter key
        self.root.bind('<Return>', lambda event: self._login())
        
        # Focus en el primer campo
        self.username_entry.focus()
    
    def _login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        
        if not username or not password:
            messagebox.showerror("Error", "Por favor complete todos los campos")
            return
        
        success, message = self.auth_service.login(username, password)
        
        if success:
            messagebox.showinfo("Éxito", f"Bienvenido {self.auth_service.obtener_usuario_actual().nombre}")
            self.root.destroy()
            self.on_login_success(self.auth_service.obtener_usuario_actual())
        else:
            messagebox.showerror("Error", message)
            self.password_entry.delete(0, tk.END)
            self.username_entry.focus()