import tkinter as tk
from tkinter import ttk
from database.order_dao import get_user_orders

class CustomerOrderFrame(tk.Frame):

    def __init__(self, parent, user_id):
        super().__init__(parent, bg="white")
        self.user_id = user_id
        self.pack(fill="both", expand=True)

        title = tk.Label(
            self,
            text="My Orders",
            font=("Arial", 16, "bold"),
            bg="white"
        )
        title.pack(pady=10)

        self.create_table()
        self.load_orders()

    def create_table(self):
        columns = (
            "order_id",
            "article_no",
            "no_of_quibi",
            "order_date",
            "delivery_date",
            "status"
        )

        self.tree = ttk.Treeview(
            self,
            columns=columns,
            show="headings"
        )
        self.tree.pack(fill="both", expand=True, padx=15, pady=10)

        headings = [
            "Order ID",
            "Article No",
            "Quantity",
            "Order Date",
            "Delivery Date",
            "Status"
        ]

        for col, head in zip(columns, headings):
            self.tree.heading(col, text=head)
            self.tree.column(col, anchor="center", width=130)

    def load_orders(self):
        orders = get_user_orders(self.user_id)

        if not orders:
            self.tree.insert(
                "",
                "end",
                values=("", "", "", "", "", "No Orders Found")
            )
            return

        for order in orders:
            self.tree.insert("", "end", values=(
                order["order_id"],
                order["article_no"],
                order["no_of_quibi"],
                order["order_date"],
                order["delivery_date"],
                order["status"]
            ))
