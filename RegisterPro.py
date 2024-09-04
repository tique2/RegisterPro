import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import hashlib
import re

class LoginRegistro:
    def __init__(self, root):
        self.root = root
        self.root.title("Login y Registro")
        self.root.geometry("400x400+500+150")
        self.root.configure(bg="#f0f0f0")
        self.root.resizable(True, True)

        self.conn = sqlite3.connect('cash_register.db')
        self.create_tables()

        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure("TFrame", background="#f0f0f0")
        self.style.configure("TLabel", background="#f0f0f0", font=("Helvetica", 12))
        self.style.configure("TEntry", fieldbackground="#ffffff")
        self.style.configure("TButton", background="#FF5722", foreground="#ffffff", font=("Helvetica", 12))
        self.style.map("TButton", background=[("active", "#e64a19")])

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        self.login_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.login_frame, text="Login")
        self.setup_login_frame()

        self.register_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.register_frame, text="Registro")
        self.setup_register_frame()

        self.recovery_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.recovery_frame, text="Recuperar Cuenta")
        self.setup_recovery_frame()

    def setup_login_frame(self):
        self.login_frame.grid_columnconfigure(0, weight=1)
        self.login_frame.grid_columnconfigure(1, weight=3)
        self.login_frame.grid_rowconfigure(0, weight=1)
        self.login_frame.grid_rowconfigure(1, weight=1)
        self.login_frame.grid_rowconfigure(2, weight=1)

        ttk.Label(self.login_frame, text="Usuario:", font=("Helvetica", 14)).grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.login_user_entry = ttk.Entry(self.login_frame, font=("Helvetica", 14))
        self.login_user_entry.grid(row=0, column=1, padx=10, pady=5, sticky="we")

        ttk.Label(self.login_frame, text="Contraseña:", font=("Helvetica", 14)).grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.login_pass_entry = ttk.Entry(self.login_frame, show="*", font=("Helvetica", 14))
        self.login_pass_entry.grid(row=1, column=1, padx=10, pady=5, sticky="we")

        self.login_button = ttk.Button(self.login_frame, text="Login", command=self.login, style="TButton")
        self.login_button.grid(row=2, column=0, columnspan=2, pady=10, sticky="we")

    def setup_register_frame(self):
        self.register_frame.grid_columnconfigure(0, weight=1)
        self.register_frame.grid_columnconfigure(1, weight=3)
        self.register_frame.grid_rowconfigure(0, weight=1)
        self.register_frame.grid_rowconfigure(1, weight=1)
        self.register_frame.grid_rowconfigure(2, weight=1)
        self.register_frame.grid_rowconfigure(3, weight=1)

        ttk.Label(self.register_frame, text="Usuario:", font=("Helvetica", 14)).grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.register_user_entry = ttk.Entry(self.register_frame, font=("Helvetica", 14))
        self.register_user_entry.grid(row=0, column=1, padx=10, pady=5, sticky="we")

        ttk.Label(self.register_frame, text="Contraseña:", font=("Helvetica", 14)).grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.register_pass_entry = ttk.Entry(self.register_frame, show="*", font=("Helvetica", 14))
        self.register_pass_entry.grid(row=1, column=1, padx=10, pady=5, sticky="we")

        ttk.Label(self.register_frame, text="Tipo de Usuario:", font=("Helvetica", 14)).grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self.user_type_var = tk.StringVar()
        self.user_type_var.set("usuario")
        ttk.Radiobutton(self.register_frame, text="Usuario", variable=self.user_type_var, value="usuario").grid(row=2, column=1, padx=10, pady=5, sticky="w")
        ttk.Radiobutton(self.register_frame, text="Admin", variable=self.user_type_var, value="admin").grid(row=2, column=1, padx=10, pady=5, sticky="e")

        self.register_button = ttk.Button(self.register_frame, text="Registrar", command=self.register, style="TButton")
        self.register_button.grid(row=3, column=0, columnspan=2, pady=10, sticky="we")

    def setup_recovery_frame(self):
        self.recovery_frame.grid_columnconfigure(0, weight=1)
        self.recovery_frame.grid_columnconfigure(1, weight=3)
        self.recovery_frame.grid_rowconfigure(0, weight=1)
        self.recovery_frame.grid_rowconfigure(1, weight=1)
        self.recovery_frame.grid_rowconfigure(2, weight=1)

        ttk.Label(self.recovery_frame, text="Usuario:", font=("Helvetica", 14)).grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.recovery_user_entry = ttk.Entry(self.recovery_frame, font=("Helvetica", 14))
        self.recovery_user_entry.grid(row=0, column=1, padx=10, pady=5, sticky="we")

        ttk.Label(self.recovery_frame, text="Nueva Contraseña:", font=("Helvetica", 14)).grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.recovery_pass_entry = ttk.Entry(self.recovery_frame, show="*", font=("Helvetica", 14))
        self.recovery_pass_entry.grid(row=1, column=1, padx=10, pady=5, sticky="we")

        self.recovery_button = ttk.Button(self.recovery_frame, text="Recuperar", command=self.recover_account, style="TButton")
        self.recovery_button.grid(row=2, column=0, columnspan=2, pady=10, sticky="we")

    def create_tables(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario TEXT NOT NULL UNIQUE,
                contrasena TEXT NOT NULL,
                tipo TEXT NOT NULL CHECK(tipo IN ('admin', 'usuario'))
            )
        ''')
        self.conn.commit()

    def login(self):
        usuario = self.login_user_entry.get()
        contrasena = self.login_pass_entry.get()

        if usuario and contrasena:
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM usuarios WHERE usuario=?", (usuario,))
            user = cursor.fetchone()
            if user:
                hashed_password = hashlib.sha256(contrasena.encode()).hexdigest()
                if hashed_password == user[2]:
                    self.open_product_manager(user[3])
                else:
                    messagebox.showerror("Error", "Contraseña incorrecta.")
            else:
                messagebox.showerror("Error", "Usuario no encontrado.")
        else:
            messagebox.showwarning("Advertencia", "Todos los campos son obligatorios.")

    def register(self):
        usuario = self.register_user_entry.get()
        contrasena = self.register_pass_entry.get()
        tipo = self.user_type_var.get()

        if usuario and contrasena and tipo:
            if not re.match(r'^[a-zA-Z0-9_]+$', usuario):
                messagebox.showerror("Error", "El usuario solo puede contener letras, números y guiones bajos.")
                return
            if len(contrasena) < 8:
                messagebox.showerror("Error", "La contraseña debe tener al menos 8 caracteres.")
                return

            hashed_password = hashlib.sha256(contrasena.encode()).hexdigest()
            cursor = self.conn.cursor()
            try:
                cursor.execute("INSERT INTO usuarios (usuario, contrasena, tipo) VALUES (?, ?, ?)", (usuario, hashed_password, tipo))
                self.conn.commit()
                messagebox.showinfo("Éxito", "Registro exitoso.")
                self.open_product_manager(tipo)
            except sqlite3.IntegrityError:
                messagebox.showerror("Error", "El usuario ya existe.")
        else:
            messagebox.showwarning("Advertencia", "Todos los campos son obligatorios.")

    def recover_account(self):
        usuario = self.recovery_user_entry.get()
        nueva_contrasena = self.recovery_pass_entry.get()

        if usuario and nueva_contrasena:
            if len(nueva_contrasena) < 8:
                messagebox.showerror("Error", "La contraseña debe tener al menos 8 caracteres.")
                return

            hashed_password = hashlib.sha256(nueva_contrasena.encode()).hexdigest()
            cursor = self.conn.cursor()
            try:
                cursor.execute("UPDATE usuarios SET contrasena=? WHERE usuario=?", (hashed_password, usuario))
                self.conn.commit()
                if cursor.rowcount > 0:
                    messagebox.showinfo("Éxito", "Contraseña actualizada exitosamente.")
                else:
                    messagebox.showerror("Error", "Usuario no encontrado.")
            except sqlite3.Error as e:
                messagebox.showerror("Error", f"Error al actualizar la contraseña: {e}")
        else:
            messagebox.showwarning("Advertencia", "Todos los campos son obligatorios.")

    def open_product_manager(self, user_type):
        self.root.destroy()
        if user_type == "admin":
            from productos import GestionProductos
            product_manager_root = tk.Tk()
            GestionProductos(product_manager_root, user_type)
            product_manager_root.mainloop()
        elif user_type == "usuario":
            from caja_registradora import CajaRegistradora
            cash_register_root = tk.Tk()
            CajaRegistradora(cash_register_root, self.conn, user_type)
            cash_register_root.mainloop()

if __name__ == "__main__":
    root = tk.Tk()
    app = LoginRegistro(root)
    root.mainloop()