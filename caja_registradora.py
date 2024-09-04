import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import subprocess
import sqlite3

class CajaRegistradora:
    def __init__(self, root, conn, user_type):
        self.root = root
        self.root.title("Caja Registradora")
        self.root.geometry("800x600+400+100")
        self.root.configure(bg="#f0f0f0")
        self.root.resizable(True, True)

        self.conn = conn
        self.user_type = user_type
        self.create_tables()

        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure("TFrame", background="#f0f0f0")
        self.style.configure("TLabel", background="#f0f0f0", font=("Helvetica", 12))
        self.style.configure("TEntry", fieldbackground="#ffffff")
        self.style.configure("TButton", background="#9C27B0", foreground="#ffffff", font=("Helvetica", 12))
        self.style.map("TButton", background=[("active", "#8e24aa")])

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        self.register_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.register_frame, text="Caja Registradora")
        self.setup_register_frame()

    def setup_register_frame(self):
        self.register_frame.grid_columnconfigure(0, weight=1)
        self.register_frame.grid_columnconfigure(1, weight=3)
        for i in range(10):
            self.register_frame.grid_rowconfigure(i, weight=1)

        ttk.Label(self.register_frame, text="Código de Barras:", font=("Helvetica", 14)).grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.barcode_entry = ttk.Entry(self.register_frame, font=("Helvetica", 14))
        self.barcode_entry.grid(row=0, column=1, padx=10, pady=5, sticky="we")
        self.barcode_entry.bind("<Return>", self.leer_codigo_barras)

        ttk.Label(self.register_frame, text="Producto:", font=("Helvetica", 14)).grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.product_entry = ttk.Entry(self.register_frame, font=("Helvetica", 14))
        self.product_entry.grid(row=1, column=1, padx=10, pady=5, sticky="we")

        ttk.Label(self.register_frame, text="Cantidad:", font=("Helvetica", 14)).grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self.quantity_entry = ttk.Entry(self.register_frame, font=("Helvetica", 14))
        self.quantity_entry.grid(row=2, column=1, padx=10, pady=5, sticky="we")

        self.add_button = ttk.Button(self.register_frame, text="Agregar Producto", command=self.agregar_producto, style="TButton")
        self.add_button.grid(row=3, column=0, columnspan=2, pady=10, sticky="we")

        self.tree = ttk.Treeview(self.register_frame, columns=("Producto", "Cantidad", "Precio", "Total"), show="headings")
        self.tree.heading("Producto", text="Producto")
        self.tree.heading("Cantidad", text="Cantidad")
        self.tree.heading("Precio", text="Precio")
        self.tree.heading("Total", text="Total")
        self.tree.grid(row=4, column=0, columnspan=2, padx=10, pady=10, sticky="we")

        self.total_label = ttk.Label(self.register_frame, text="Total General: $0.00", font=("Helvetica", 14, "bold"))
        self.total_label.grid(row=5, column=0, columnspan=2, pady=10, sticky="we")

        ttk.Label(self.register_frame, text="Pago del Cliente:", font=("Helvetica", 14)).grid(row=6, column=0, padx=10, pady=5, sticky="w")
        self.payment_entry = ttk.Entry(self.register_frame, font=("Helvetica", 14))
        self.payment_entry.grid(row=6, column=1, padx=10, pady=5, sticky="we")

        self.bill_button = ttk.Button(self.register_frame, text="Generar Factura", command=self.generar_factura, style="TButton")
        self.bill_button.grid(row=7, column=0, columnspan=2, pady=10, sticky="we")

        self.print_button = ttk.Button(self.register_frame, text="Imprimir Factura", command=self.imprimir_factura, style="TButton")
        self.print_button.grid(row=8, column=0, columnspan=2, pady=10, sticky="we")

        if self.user_type == "admin":
            self.config_button = ttk.Button(self.register_frame, text="Ir a Configuración", command=self.ir_a_configuracion, style="TButton")
            self.config_button.grid(row=9, column=0, columnspan=2, pady=10, sticky="we")

    def create_tables(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transacciones (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                producto_id INTEGER NOT NULL,
                cantidad INTEGER NOT NULL,
                total REAL NOT NULL,
                fecha TEXT NOT NULL,
                FOREIGN KEY (producto_id) REFERENCES productos (id)
            )
        ''')
        self.conn.commit()

    def agregar_producto(self):
        producto = self.product_entry.get()
        cantidad = self.quantity_entry.get()

        if producto and cantidad:
            try:
                cantidad = int(cantidad)
                cursor = self.conn.cursor()
                cursor.execute("SELECT * FROM productos WHERE nombre=?", (producto,))
                producto_data = cursor.fetchone()
                if producto_data:
                    precio = producto_data[3]
                    total = cantidad * precio
                    self.tree.insert("", tk.END, values=(producto, cantidad, precio, total))
                    self.limpiar_entradas()
                    self.actualizar_total()
                else:
                    messagebox.showwarning("Advertencia", "Producto no encontrado.")
            except ValueError:
                messagebox.showerror("Error", "Cantidad debe ser un número.")
        else:
            messagebox.showwarning("Advertencia", "Todos los campos son obligatorios.")

    def limpiar_entradas(self):
        self.barcode_entry.delete(0, tk.END)
        self.product_entry.delete(0, tk.END)
        self.quantity_entry.delete(0, tk.END)

    def actualizar_total(self):
        total = 0.0
        for item in self.tree.get_children():
            total += float(self.tree.item(item, 'values')[3])
        self.total_label.config(text=f"Total General: ${total:.2f}")

    def generar_factura(self):
        total = 0.0
        for item in self.tree.get_children():
            total += float(self.tree.item(item, 'values')[3])

        pago = self.payment_entry.get()

        if not pago:
            messagebox.showwarning("Advertencia", "Ingresa el pago del cliente.")
            return

        try:
            pago = float(pago)
            if pago < total:
                messagebox.showwarning("Advertencia", "El pago es insuficiente.")
                return

            cambio = pago - total
            factura_text = self.crear_texto_factura(total, pago, cambio)
            messagebox.showinfo("Factura", factura_text)
            self.factura_text = factura_text

            cursor = self.conn.cursor()
            for item in self.tree.get_children():
                values = self.tree.item(item, 'values')
                cursor.execute("SELECT id FROM productos WHERE nombre=?", (values[0],))
                producto_id = cursor.fetchone()[0]
                cursor.execute("INSERT INTO transacciones (producto_id, cantidad, total, fecha) VALUES (?, ?, ?, ?)",
                               (producto_id, values[1], values[3], datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
            self.conn.commit()
        except ValueError:
            messagebox.showerror("Error", "El pago debe ser un número.")

    def crear_texto_factura(self, total, pago, cambio):
        factura_text = f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        factura_text += "Productos:\n"
        factura_text += "{:<20} {:<10} {:<10} {:<10}\n".format("Producto", "Cantidad", "Precio", "Total")
        for item in self.tree.get_children():
            values = self.tree.item(item, 'values')
            factura_text += "{:<20} {:<10} {:<10} {:<10}\n".format(values[0], values[1], values[2], values[3])
        factura_text += f"Total a Pagar: ${total:.2f}\n"
        factura_text += f"Pago del Cliente: ${pago:.2f}\n"
        factura_text += f"Cambio: ${cambio:.2f}\n"
        return factura_text

    def imprimir_factura(self):
        if not hasattr(self, 'factura_text'):
            messagebox.showwarning("Advertencia", "Primero genera la factura.")
            return

        company_info = self.get_company_info()
        factura_text = company_info + self.factura_text

        with open("factura.txt", "w") as file:
            file.write(factura_text)

        try:
            subprocess.run(["xdg-open", "factura.txt"], check=True)
        except FileNotFoundError:
            messagebox.showerror("Error", "No se pudo abrir el archivo. Asegúrate de tener xdg-open instalado.")

        self.limpiar_todo()

    def get_company_info(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM configuracion_empresa LIMIT 1")
        config = cursor.fetchone()
        if config:
            return f"{config[1]}\n{config[2]}\n{config[3]}\n{config[4]}\n"
        return "Nombre de la Empresa\nDirección\nTeléfono\nEmail\n"

    def limpiar_todo(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.limpiar_entradas()
        self.payment_entry.delete(0, tk.END)
        self.actualizar_total()

    def volver_a_gestion_productos(self):
        self.root.destroy()
        from productos import GestionProductos
        product_manager_root = tk.Tk()
        GestionProductos(product_manager_root, self.user_type)
        product_manager_root.mainloop()

    def ir_a_configuracion(self):
        if self.user_type != "admin":
            messagebox.showwarning("Advertencia", "No tienes permisos para acceder a la configuración.")
            return

        self.root.destroy()
        from configuracion import ConfiguracionEmpresa
        config_root = tk.Tk()
        ConfiguracionEmpresa(config_root)
        config_root.mainloop()

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
                self.quantity_entry.insert(0, "1")  # Asumimos que se agrega una unidad por defecto
                self.status_label.config(text="Producto encontrado", foreground="green")
            else:
                self.status_label.config(text="Producto no encontrado", foreground="red")
        else:
            self.status_label.config(text="Ingrese un código de barras", foreground="red")

if __name__ == "__main__":
    root = tk.Tk()
    conn = sqlite3.connect('cash_register.db')
    app = CajaRegistradora(root, conn, "admin")  # Puedes cambiar "admin" por "usuario" para probar ambos casos
    root.mainloop()