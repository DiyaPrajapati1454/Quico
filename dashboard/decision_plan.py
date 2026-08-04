import tkinter as tk
from tkinter import ttk, messagebox
from database.order_dao import get_all_non_deliveredorders
from database.machine_dao import (
    get_all_cutting_machines,
    get_all_folding_machines,
    get_all_packing_machines
)
from utils.time_convert import hours_to_hhmm


class DecisionModuleUI(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, padding=20)

        # ---------------- Title ----------------
        ttk.Label(
            self,
            text="Machine Decision Module",
            font=("Arial", 14, "bold")
        ).pack(pady=10)

        # ---------------- FILTERS ----------------
        filter_frame = ttk.LabelFrame(self, text="Filter Orders", padding=10)
        filter_frame.pack(fill="x", pady=5)

        ttk.Label(filter_frame, text="Min Width").pack(side="left", padx=5)
        self.min_width = ttk.Entry(filter_frame, width=8)
        self.min_width.pack(side="left", padx=5)

        ttk.Label(filter_frame, text="Max Width").pack(side="left", padx=5)
        self.max_width = ttk.Entry(filter_frame, width=8)
        self.max_width.pack(side="left", padx=5)

        ttk.Label(filter_frame, text="Min Qty").pack(side="left", padx=5)
        self.min_qty = ttk.Entry(filter_frame, width=8)
        self.min_qty.pack(side="left", padx=5)

        ttk.Label(filter_frame, text="Max Qty").pack(side="left", padx=5)
        self.max_qty = ttk.Entry(filter_frame, width=8)
        self.max_qty.pack(side="left", padx=5)

        ttk.Button(
            filter_frame,
            text="Apply",
            command=self.apply_filters
        ).pack(side="left", padx=10)

        ttk.Button(
            filter_frame,
            text="Reset",
            command=self.load_orders
        ).pack(side="left", padx=5)

        # ---------------- Order Table ----------------
        order_frame = ttk.LabelFrame(self, text="Available Orders", padding=10)
        order_frame.pack(fill="both", expand=True, pady=10)

        columns = ("order_id", "length", "width", "quantity")

        self.order_table = ttk.Treeview(
            order_frame,
            columns=columns,
            show="headings",
            height=6
        )

        for col in columns:
            self.order_table.heading(col, text=col.capitalize())
            self.order_table.column(col, anchor="center")

        self.order_table.pack(fill="both", expand=True)

        self.load_orders()

        # ---------------- Operation Selection ----------------
        operation_frame = ttk.LabelFrame(self, text="Select Operation", padding=10)
        operation_frame.pack(fill="x", pady=10)

        self.operation_var = tk.StringVar(value="Cutting")

        for op in ("Cutting", "Folding", "Packing"):
            ttk.Radiobutton(
                operation_frame,
                text=op,
                variable=self.operation_var,
                value=op
            ).pack(side="left", padx=15)

        # ---------------- Decision Button ----------------
        ttk.Button(
            self,
            text="Find Best Machine",
            command=self.find_best_machine
        ).pack(pady=10)

        # ---------------- Result ----------------
        self.result_var = tk.StringVar(value="")
        ttk.Label(
            self,
            textvariable=self.result_var,
            font=("Arial", 11, "bold"),
            foreground="blue"
        ).pack(pady=10)

# ---------------- LOAD ORDERS ----------------

    def load_orders(self):
        for row in self.order_table.get_children():
            self.order_table.delete(row)

        self.orders = get_all_non_deliveredorders()

        for order in self.orders:
            self.order_table.insert("", "end", values=(
                order["order_id"],
                order["length"],
                order["width"],
                order["no_of_quibi"]
            ))

# ---------------- FILTER LOGIC ----------------

    def apply_filters(self):

        for row in self.order_table.get_children():
            self.order_table.delete(row)

        try:
            min_w = int(self.min_width.get()) if self.min_width.get() else None
            max_w = int(self.max_width.get()) if self.max_width.get() else None
            min_q = int(self.min_qty.get()) if self.min_qty.get() else None
            max_q = int(self.max_qty.get()) if self.max_qty.get() else None
        except:
            messagebox.showerror("Error", "Enter valid numbers")
            return

        for order in get_all_non_deliveredorders():

            width = int(order["width"])
            qty = int(order["no_of_quibi"])

            if min_w and width < min_w:
                continue
            if max_w and width > max_w:
                continue
            if min_q and qty < min_q:
                continue
            if max_q and qty > max_q:
                continue

            self.order_table.insert("", "end", values=(
                order["order_id"],
                order["length"],
                order["width"],
                order["no_of_quibi"]
            ))

# ---------------- DECISION LOGIC ----------------

    def find_best_machine(self):

        if not self.order_table.selection():
            messagebox.showwarning("Warning", "Please select an order first.")
            return

        values = self.order_table.item(
            self.order_table.selection()[0],
            "values"
        )

        quantity = int(values[3])
        width = int(values[2])
        operation = self.operation_var.get()

        if operation == "Cutting":
            machines = get_all_cutting_machines()
        elif operation == "Folding":
            machines = get_all_folding_machines()
        elif operation == "Packing":
            machines = get_all_packing_machines()
        else:
            self.result_var.set("Invalid Operation Selected")
            return

        if not machines:
            self.result_var.set("No machines available.")
            return

        best_machine = None
        best_time = None

        for m in machines:
            speed = m["speed"]
            max_width = m["max_width"]

            if max_width < width:
                continue

            time = quantity / speed

            if best_time is None or time < best_time:
                best_time = time
                best_machine = m

        if best_machine is None:
            self.result_var.set("No compatible machines found.")
            return

        duration = hours_to_hhmm(best_time)

        result_text = (
            f"Best Machine: {best_machine['m_name']}\n"
            f"Time Required: {duration}\n"
            f"Reason: Highest speed among compatible machines"
        )

        self.result_var.set(result_text)