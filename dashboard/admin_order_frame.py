import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from database.order_dao import get_all_orders, get_all_delivered_orders


class AdminOrderFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.configure(bg="#f0f0f0")
        self.pack(fill="both", expand=True)

        # ============ Title ============
        tk.Label(
            self,
            text="Order Management",
            font=("Arial", 16, "bold"),
            bg="#f0f0f0"
        ).pack(pady=15)

        # ============ Tabs ============
        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True, padx=20, pady=10)

        self.pending_frame = tk.Frame(notebook, bg="#f0f0f0")
        self.delivered_frame = tk.Frame(notebook, bg="#f0f0f0")

        notebook.add(self.pending_frame, text="Pending / Not Delivered Orders")
        notebook.add(self.delivered_frame, text="Delivered Orders")

        # ============ Filters ============
        self.create_pending_filters()
        self.create_delivered_filters()

        # ============ Tables ============
        self.pending_tree = self.create_table(self.pending_frame)
        self.delivered_tree = self.create_table(self.delivered_frame)

        # Load data
        self.load_pending_orders()
        self.load_delivered_orders()

# ---------------- TABLE ----------------

    def create_table(self, parent):
        style = ttk.Style()
        style.configure("Treeview", rowheight=28, font=("Arial", 10))
        style.configure("Treeview.Heading", font=("Arial", 10, "bold"))

        frame = tk.Frame(parent, bg="#f0f0f0")
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        columns = (
            "Order ID", "User ID", "Article Code",
            "Quantity", "Order Date", "Delivery Date", "Status"
        )

        tree = ttk.Treeview(frame, columns=columns, show="headings")
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)

        for col in columns:
            tree.heading(col, text=col, anchor="w")
            tree.column(col, anchor="w", width=120)

        tree.column("Order ID", width=80)
        tree.column("Quantity", width=90)

        tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        return tree

# ---------------- HELPER ----------------

    def to_datetime(self, val):
        if isinstance(val, datetime):
            return val
        return datetime.combine(val, datetime.min.time())

# ---------------- FILTER UI ----------------

    def create_pending_filters(self):
        frame = tk.Frame(self.pending_frame, bg="#f0f0f0")
        frame.pack(fill="x", padx=10, pady=5)

        tk.Label(frame, text="Filter by Delivery Date:",
                 bg="#f0f0f0", font=("Arial", 10, "bold")).pack(side="left", padx=5)

        tk.Label(frame, text="From", bg="#f0f0f0").pack(side="left", padx=5)
        self.pending_from = ttk.Entry(frame, width=12)
        self.pending_from.pack(side="left", padx=5)

        tk.Label(frame, text="To", bg="#f0f0f0").pack(side="left", padx=5)
        self.pending_to = ttk.Entry(frame, width=12)
        self.pending_to.pack(side="left", padx=5)

        ttk.Button(frame, text="Apply", command=self.filter_pending).pack(side="left", padx=10)

    def create_delivered_filters(self):
        frame = tk.Frame(self.delivered_frame, bg="#f0f0f0")
        frame.pack(fill="x", padx=10, pady=5)

        tk.Label(frame, text="Filter by Delivery Date:",
                 bg="#f0f0f0", font=("Arial", 10, "bold")).pack(side="left", padx=5)

        tk.Label(frame, text="From", bg="#f0f0f0").pack(side="left", padx=5)
        self.delivered_from = ttk.Entry(frame, width=12)
        self.delivered_from.pack(side="left", padx=5)

        tk.Label(frame, text="To", bg="#f0f0f0").pack(side="left", padx=5)
        self.delivered_to = ttk.Entry(frame, width=12)
        self.delivered_to.pack(side="left", padx=5)

        ttk.Button(frame, text="Apply", command=self.filter_delivered).pack(side="left", padx=10)

# ---------------- LOAD METHODS ----------------

    def load_pending_orders(self):
        self.filter_pending()

    def load_delivered_orders(self):
        self.filter_delivered()

# ---------------- FILTER LOGIC ----------------

    def filter_pending(self):

        for row in self.pending_tree.get_children():
            self.pending_tree.delete(row)

        try:
            from_date = datetime.strptime(self.pending_from.get(), "%Y-%m-%d") if self.pending_from.get() else None
            to_date = datetime.strptime(self.pending_to.get(), "%Y-%m-%d") if self.pending_to.get() else None
        except:
            messagebox.showerror("Error", "Use YYYY-MM-DD format")
            return

        data = []

        for order in get_all_orders():
            if order["status"] == "Delivered":
                continue

            delivery_dt = self.to_datetime(order["delivery_date"])

            if from_date and delivery_dt < from_date:
                continue
            if to_date and delivery_dt > to_date:
                continue

            data.append((
                order["order_id"],
                order["user_id"],
                order["article_no"],
                order["no_of_quibi"],
                order["order_date"],
                order["delivery_date"],
                order["status"]
            ))

        data.sort(key=lambda x: self.to_datetime(x[5]))

        for row in data:
            self.pending_tree.insert("", "end", values=row)

    def filter_delivered(self):

        for row in self.delivered_tree.get_children():
            self.delivered_tree.delete(row)

        try:
            from_date = datetime.strptime(self.delivered_from.get(), "%Y-%m-%d") if self.delivered_from.get() else None
            to_date = datetime.strptime(self.delivered_to.get(), "%Y-%m-%d") if self.delivered_to.get() else None
        except:
            messagebox.showerror("Error", "Use YYYY-MM-DD format")
            return

        data = []

        for order in get_all_delivered_orders():

            delivery_dt = self.to_datetime(order["delivery_date"])

            if from_date and delivery_dt < from_date:
                continue
            if to_date and delivery_dt > to_date:
                continue

            data.append((
                order["order_id"],
                order["user_id"],
                order["article_no"],
                order["no_of_quibi"],
                order["order_date"],
                order["delivery_date"],
                "Delivered"
            ))

        data.sort(key=lambda x: self.to_datetime(x[5]))

        for row in data:
            self.delivered_tree.insert("", "end", values=row)