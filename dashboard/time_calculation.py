import tkinter as tk
from tkinter import ttk, messagebox
from database.order_dao import get_all_non_deliveredorders
from database.machine_dao import get_all_cutting_machines
from database.machine_dao import get_all_folding_machines
from database.machine_dao import get_all_packing_machines
from utils.time_convert import hours_to_hhmm


class TimeCalculationUI(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, padding=20)

        ttk.Label(
            self,
            text="Time Calculation for Selected Operation",
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
            self.order_table.column(col, anchor="center", width=120)

        y_scroll = ttk.Scrollbar(order_frame, orient="vertical", command=self.order_table.yview)
        x_scroll = ttk.Scrollbar(order_frame, orient="horizontal", command=self.order_table.xview)

        self.order_table.configure(
            yscrollcommand=y_scroll.set,
            xscrollcommand=x_scroll.set
        )

        self.order_table.grid(row=0, column=0, sticky="nsew")
        y_scroll.grid(row=0, column=1, sticky="ns")
        x_scroll.grid(row=1, column=0, sticky="ew")

        order_frame.grid_rowconfigure(0, weight=1)
        order_frame.grid_columnconfigure(0, weight=1)

        self.order_table.bind("<<TreeviewSelect>>", self.on_order_select)

        # Load data
        self.load_orders()

        # ---------------- Selected Order ----------------
        details_frame = ttk.LabelFrame(self, text="Selected Order Details", padding=10)
        details_frame.pack(fill="x", pady=10)

        self.selected_order_var = tk.StringVar(value="No order selected")

        ttk.Label(details_frame, textvariable=self.selected_order_var).pack(anchor="w")

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

        ttk.Button(self, text="Calculate Time", command=self.calculate_time).pack(pady=10)

        self.result_var = tk.StringVar(value="")
        ttk.Label(
            self,
            textvariable=self.result_var,
            font=("Arial", 11, "bold"),
            foreground="green"
        ).pack(pady=5)

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

# ---------------- EXISTING LOGIC ----------------

    def calculate_time_machine(self, machine, quantity, width):
        result_txt = ""

        if not machine:
            result_txt += "Currently no machines are available\n"

        for m in machine:
            speed = m['speed']
            max_width = m['max_width']

            if max_width < width:
                result_txt += f"{m['m_name']} → Not Compatible\n"
            else:
                time = quantity / speed
                duration = hours_to_hhmm(time)
                result_txt += f"{m['m_name']} → {duration}\n"

        result_txt += "\nNote:\n"
        result_txt += "• Time based on machine speed\n"

        self.result_var.set(result_txt)

    def on_order_select(self, event):
        selected = self.order_table.selection()
        if selected:
            values = self.order_table.item(selected[0], "values")
            self.selected_order_var.set(
                f"Order ID: {values[0]} | Length: {values[1]} | "
                f"Width: {values[2]} | Quantity: {values[3]}"
            )

    def calculate_time(self):
        if not self.order_table.selection():
            messagebox.showwarning("Warning", "Please select an order first.")
            return

        values = self.order_table.item(self.order_table.selection()[0], "values")
        operation = self.operation_var.get()

        quantity = int(values[3])
        width = int(values[2])

        if operation == 'Cutting':
            self.calculate_time_machine(get_all_cutting_machines(), quantity, width)

        elif operation == 'Folding':
            self.calculate_time_machine(get_all_folding_machines(), quantity, width)

        elif operation == 'Packing':
            self.calculate_time_machine(get_all_packing_machines(), quantity, width)