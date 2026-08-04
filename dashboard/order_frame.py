import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
from database.article_dao import get_all_articles
from datetime import date
from database.order_dao import insert_orders


class OrderFrame(tk.Frame):
    def clear_form(self):
        # Clear form fields only
        self.article_code_var.set("")
        self.quantity_var.set(0)
        self.selected_article = None

        # Reset delivery date to today
        self.delivery_date.set_date(date.today())

        # Remove row selection highlight (table remains visible)
        for item in self.tree.selection():
            self.tree.selection_remove(item)

    def __init__(self, parent, customer_id):
        super().__init__(parent)
        self.customer_id = customer_id
        self.selected_article = None
        
        self.configure(bg="#f0f0f0")
        self.pack(fill="both", expand=True)

        # ================= Title =================
        tk.Label(
            self,
            text="Create Order",
            font=("Arial", 16, "bold"),
            bg="#f0f0f0"
        ).pack(pady=15)

        # ================= Table Styling =================
        style = ttk.Style()
        style.configure(
            "Treeview",
            rowheight=28,
            font=("Arial", 10)
        )
        style.configure(
            "Treeview.Heading",
            font=("Arial", 10, "bold")
        )

        # ================= Article Table =================
        table_frame = tk.Frame(self, bg="#f0f0f0")
        table_frame.pack(padx=20, pady=10, fill="x")

        self.tree = ttk.Treeview(
            table_frame,
            columns=("Code", "Length", "Width"),
            show="headings",
            height=8
        )

        # Columns (LEFT aligned)
        self.tree.column("Code", width=180, anchor="w")
        self.tree.column("Length", width=120, anchor="w")
        self.tree.column("Width", width=120, anchor="w")

        # Headings (LEFT aligned)
        self.tree.heading("Code", text="Article Code", anchor="w")
        self.tree.heading("Length", text="Length", anchor="w")
        self.tree.heading("Width", text="Width", anchor="w")

        self.tree.pack(fill="x")

        self.tree.bind("<ButtonRelease-1>", self.on_article_select)

        self.load_articles()

        # ================= Order Form =================
        form_frame = tk.LabelFrame(
            self,
            text="Order Details",
            font=("Arial", 10, "bold"),
            bg="#f0f0f0",
            padx=15,
            pady=10
        )
        form_frame.pack(padx=20, pady=15, fill="x")

        # Article Code
        tk.Label(
            form_frame,
            text="Selected Article Code:",
            bg="#f0f0f0"
        ).grid(row=0, column=0, sticky="e", padx=8, pady=6)

        self.article_code_var = tk.StringVar()
        tk.Entry(
            form_frame,
            textvariable=self.article_code_var,
            state="readonly",
            width=25
        ).grid(row=0, column=1, padx=8, pady=6)

        # Quantity
        tk.Label(
            form_frame,
            text="Quantity (Cubis):",
            bg="#f0f0f0"
        ).grid(row=1, column=0, sticky="e", padx=8, pady=6)

        self.quantity_var = tk.IntVar()
        tk.Entry(
            form_frame,
            textvariable=self.quantity_var,
            width=25
        ).grid(row=1, column=1, padx=8, pady=6)

        # Delivery Date
        tk.Label(
            form_frame,
            text="Agreed Delivery Date:",
            bg="#f0f0f0"
        ).grid(row=2, column=0, sticky="e", padx=8, pady=6)

        self.delivery_date = DateEntry(
            form_frame,
            mindate=date.today(),
            date_pattern="yyyy-mm-dd",
            width=22
        )
        self.delivery_date.grid(row=2, column=1, padx=8, pady=6)

        # ================= Buttons =================
        button_frame = tk.Frame(self, bg="#f0f0f0")
        button_frame.pack(pady=15)

        tk.Button(
            button_frame,
            text="Place Order",
            width=15,
            bg="#4CAF50",
            fg="white",
            font=("Arial", 10, "bold"),
            command=self.place_order
        ).pack()

    # ================= Load Articles =================
    def load_articles(self):
        for article in get_all_articles():
            self.tree.insert(
                "",
                "end",
                values=(article["code"], article["length"], article["width"])
            )

    # ================= Select Article =================
    def on_article_select(self, event):
        selected = self.tree.focus()
        if selected:
            values = self.tree.item(selected, "values")
            self.article_code_var.set(values[0])
            self.selected_article = values[0]

    # ================= Place Order (LOGIC LATER) =================
    def place_order(self):
        if not self.selected_article:
            messagebox.showwarning("Warning", "Please select an article!")
            return

        quantity = self.quantity_var.get()
        if quantity <= 0:
            messagebox.showwarning("Warning", "Quantity must be greater than zero!")
            return

        delivery = self.delivery_date.get_date()

        # INSERT LOGIC WILL BE ADDED LATER
        try:
            insert_orders(self.customer_id,quantity,self.selected_article,delivery)
            messagebox.showinfo("Success", "Order added")
            self.clear_form()
            
        except Exception as e:
            messagebox.showwarning("Error",str(e))
            return
