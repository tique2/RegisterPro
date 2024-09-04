import tkinter as tk
from tkinter import ttk
import sqlite3

class GestionProductos:
    def __init__(self, root, user_type):
        self.root = root
        self.root.title("Gestión de Productos")
        self.root.geometry("800x600+400+100")
        self.root.configure(bg="#f0f0f0")
        self.root.resizable(True, True)

        self.user_type = user_type
        self.conn = sqlite3.connect('cash_register.db')
        self.create_tables()

        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure("TFrame", background="#f0f0f0")
        self.style.configure("TLabel", background="#f0f0f0", font=("Helvetica", 12))
        self.style.configure("TEntry", fieldbackground="#ffffff")
        self.style.configure("TButton", background="#2196F3", foreground="#ffffff", font=("Helvetica", 12))
        self.style.map("TButton", background=[("active", "#1e88e5")])

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        self.product_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.product_frame, text="Productos")
        self.setup_product_frame()

    def setup_product_frame(self):
        self.product_frame.grid_columnconfigure(0, weight=1)
        self.product_frame.grid_columnconfigure(1, weight=3)
        for i in range(10):
            self.product_frame.grid_rowconfigure(i, weight=1)

        ttk.Label(self.product_frame, text="Código de Barras:", font=("Helvetica", 14)).grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.barcode_entry = ttk.Entry(self.product_frame, font=("Helvetica", 14))
        self.barcode_entry.grid(row=0, column=1, padx=10, pady=5, sticky="we")
        self.barcode_entry.bind("<Return>", self.leer_codigo_barras)

        ttk.Label(self.product_frame, text="Producto:", font=("Helvetica", 14)).grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.product_entry = ttk.Entry(self.product_frame, font=("Helvetica", 14))
        self.product_entry.grid(row=1, column=1, padx=10, pady=5, sticky="we")

        ttk.Label(self.product_frame, text="Cantidad:", font=("Helvetica", 14)).grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self.quantity_entry = ttk.Entry(self.product_frame, font=("Helvetica", 14))
        self.quantity_entry.grid(row=2, column=1, padx=10, pady=5, sticky="we")

        ttk.Label(self.product_frame, text="Precio:", font=("Helvetica", 14)).grid(row=3, column=0, padx=10, pady=5, sticky="w")
        self.price_entry = ttk.Entry(self.product_frame, font=("Helvetica", 14))
        self.price_entry.grid(row=3, column=1, padx=10, pady=5, sticky="we")

        self.add_button = ttk.Button(self.product_frame, text="Agregar Producto", command=self.agregar_producto, style="TButton")
        self.add_button.grid(row=4, column=0, columnspan=2, pady=10, sticky="we")

        if self.user_type == "admin":
            self.update_button = ttk.Button(self.product_frame, text="Actualizar Producto", command=self.actualizar_producto, style="TButton")
            self.update_button.grid(row=5, column=0, columnspan=2, pady=10, sticky="we")

            self.delete_button = ttk.Button(self.product_frame, text="Eliminar Producto", command=self.eliminar_producto, style="TButton")
            self.delete_button.grid(row=6, column=0, columnspan=2, pady=10, sticky="we")

            self.config_button = ttk.Button(self.product_frame, text="Ir a Configuración", command=self.ir_a_configuracion, style="TButton")
            self.config_button.grid(row=9, column=0, columnspan=2, pady=10, sticky="we")

        self.tree = ttk.Treeview(self.product_frame, columns=("Producto", "Cantidad", "Precio"), show="headings")
        self.tree.heading("Producto", text="Producto")
        self.tree.heading("Cantidad", text="Cantidad")
        self.tree.heading("Precio", text="Precio")
        self.tree.grid(row=7, column=0, columnspan=2, padx=10, pady=10, sticky="we")

        self.tree.bind("<<TreeviewSelect>>", self.on_select)

        if self.user_type != "admin":
            self.register_button = ttk.Button(self.product_frame, text="Ir a Caja Registradora", command=self.ir_a_caja_registradora, style="TButton")
            self.register_button.grid(row=8, column=0, columnspan=2, pady=10, sticky="we")

        self.cargar_productos()

        self.status_label = ttk.Label(self.product_frame, text="", font=("Helvetica", 12), background="#f0f0f0")
        self.status_label.grid(row=10, column=0, columnspan=2, pady=10, sticky="we")

    def create_tables(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS productos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                codigo_barras TEXT UNIQUE,
                nombre TEXT NOT NULL,
                cantidad INTEGER NOT NULL,
                precio REAL NOT NULL
            )
        ''')
        self.conn.commit()

    def cargar_productos(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM productos")
        productos = cursor.fetchall()
        for producto in productos:
            self.tree.insert("", tk.END, values=(producto[2], producto[3], producto[4]))

    def agregar_producto(self):
        codigo_barras = self.barcode_entry.get()
        producto = self.product_entry.get()
        cantidad = self.quantity_entry.get()
        precio = self.price_entry.get()

        if producto and cantidad and precio:
            try:
                cantidad = int(cantidad)
                precio = float(precio)
                cursor = self.conn.cursor()
                cursor.execute("INSERT INTO productos (codigo_barras, nombre, cantidad, precio) VALUES (?, ?, ?, ?)", (codigo_barras, producto, cantidad, precio))
                self.conn.commit()
                self.tree.insert("", tk.END, values=(producto, cantidad, precio))
                self.limpiar_entradas()
                self.status_label.config(text="Producto agregado exitosamente", foreground="green")
            except ValueError:
                self.status_label.config(text="Cantidad y precio deben ser números", foreground="red")
            except sqlite3.IntegrityError:
                self.status_label.config(text="Código de barras ya existe", foreground="red")
        else:
            self.status_label.config(text="Todos los campos son obligatorios", foreground="red")

    def actualizar_producto(self):
        if self.user_type != "admin":
            self.status_label.config(text="No tienes permisos para actualizar productos", foreground="red")
            return

        selected_item = self.tree.selection()
        if not selected_item:
            self.status_label.config(text="Selecciona un producto para actualizar", foreground="red")
            return

        producto = self.product_entry.get()
        cantidad = self.quantity_entry.get()
        precio = self.price_entry.get()

        if producto and cantidad and precio:
            try:
                cantidad = int(cantidad)
                precio = float(precio)
                index = self.tree.index(selected_item)
                cursor = self.conn.cursor()
                cursor.execute("UPDATE productos SET nombre=?, cantidad=?, precio=? WHERE id=?", (producto, cantidad, precio, index + 1))
                self.conn.commit()
                self.tree.item(selected_item, values=(producto, cantidad, precio))
                self.limpiar_entradas()
                self.status_label.config(text="Producto actualizado exitosamente", foreground="green")
            except ValueError:
                self.status_label.config(text="Cantidad y precio deben ser números", foreground="red")
        else:
            self.status_label.config(text="Todos los campos son obligatorios", foreground="red")

    def eliminar_producto(self):
        if self.user_type != "admin":
            self.status_label.config(text="No tienes permisos para eliminar productos", foreground="red")
            return

        selected_item = self.tree.selection()
        if not selected_item:
            self.status_label.config(text="Selecciona un producto para eliminar", foreground="red")
            return

        index = self.tree.index(selected_item)
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM productos WHERE id=?", (index + 1,))
        self.conn.commit()
        self.tree.delete(selected_item)
        self.limpiar_entradas()
        self.status_label.config(text="Producto eliminado exitosamente", foreground="green")

    def limpiar_entradas(self):
        self.barcode_entry.delete(0, tk.END)
        self.product_entry.delete(0, tk.END)
        self.quantity_entry.delete(0, tk.END)
        self.price_entry.delete(0, tk.END)

    def on_select(self, event):
        selected_items = self.tree.selection()
        if selected_items:
            selected_item = selected_items[0]
            values = self.tree.item(selected_item, 'values')
            self.product_entry.delete(0, tk.END)
            self.product_entry.insert(0, values[0])
            self.quantity_entry.delete(0, tk.END)
            self.quantity_entry.insert(0, values[1])
            self.price_entry.delete(0, tk.END)
            self.price_entry.insert(0, values[2])

    def leer_codigo_barras(self, event):
        codigo_barras = self.barcode_entry.get()
        if codigo_barras:
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM productos WHERE codigo_barras=?", (codigo_barras,))
            producto = cursor.fetchone()
            if producto:
                self.product_entry.delete(0, tk.END)
                self.product_entry.insert(0, producto[2])
                self.quantity_entry.delete(0, tk.END)
                self.quantity_entry.insert(0, producto[3])
                self.price_entry.delete(0, tk.END)
                self.price_entry.insert(0, producto[4])
                self.status_label.config(text="Producto encontrado", foreground="green")
            else:
                self.status_label.config(text="Producto no encontrado", foreground="red")
        else:
            self.status_label.config(text="Ingrese un código de barras", foreground="red")

    def ir_a_caja_registradora(self):
        self.root.destroy()
        from caja_registradora import CajaRegistradora
        cash_register_root = tk.Tk()
        CajaRegistradora(cash_register_root, self.conn, self.user_type)  # Añadir self.user_type aquí
        cash_register_root.mainloop()

    def ir_a_configuracion(self):
        if self.user_type != "admin":
            self.status_label.config(text="No tienes permisos para acceder a la configuración", foreground="red")
            return

        self.root.destroy()
        from configuracion import ConfiguracionEmpresa
        config_root = tk.Tk()
        ConfiguracionEmpresa(config_root)
        config_root.mainloop()

if __name__ == "__main__":
    root = tk.Tk()
    app = GestionProductos(root, "admin")  # Puedes cambiar "admin" por "usuario" para probar ambos casos
    root.mainloop()