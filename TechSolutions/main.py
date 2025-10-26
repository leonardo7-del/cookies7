import tkinter as tk
import sys
import os

# Configurar el path para encontrar los módulos
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)
sys.path.insert(0, os.path.join(current_dir, 'src'))

print("Python path configurado:")
for path in sys.path:
    print(f"  - {path}")

try:
    from src.presentation.login_window import LoginWindow
    from src.presentation.main_window import MainWindow
    print("✓ Importaciones exitosas")
except ImportError as e:
    print(f"✗ Error en importaciones: {e}")
    # Intentar importaciones alternativas
    try:
        from presentation.login_window import LoginWindow
        from presentation.main_window import MainWindow
        print("✓ Importaciones alternativas exitosas")
    except ImportError as e2:
        print(f"✗ Error en importaciones alternativas: {e2}")
        raise

def main():
    print("Iniciando aplicación Tech Solutions...")
    
    # Primero mostrar login
    root = tk.Tk()
    
    def on_login_success(usuario):
        print(f"Login exitoso para: {usuario.nombre}")
        # Cuando el login es exitoso, mostrar la ventana principal
        app = MainWindow(usuario)
        app.run()
    
    login_window = LoginWindow(root, on_login_success)
    print("Ventana de login creada")
    root.mainloop()

if __name__ == "__main__":
    main()