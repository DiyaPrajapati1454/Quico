import tkinter as tk
from tkinter import ttk, messagebox
from collections import defaultdict
import pandas as pd
from datetime import datetime, timedelta

from database.order_dao import get_all_orders


class CustomerReports(tk.Frame):

    def __init__(self, parent, schedule):
        super().__init__(parent)

        self.schedule = schedule
        self.orders_db = get_all_orders()  # FULL DB DATA

        self.configure(bg="#f4f4f4")
        self.build_ui()

# ---------------- UI ----------------

    def build_ui(self):

        header = tk.Frame(self, bg="#f4f4f4")
        header.pack(fill="x", pady=10)

        tk.Label(
            header,
            text="Customer Order Insights",
            font=("Segoe UI", 18, "bold"),
            bg="#f4f4f4"
        ).pack(side="left", padx=15)

        ttk.Button(
            header,
            text="Export Report",
            command=self.export_excel
        ).pack(side="right", padx=15)

        self.tabs = ttk.Notebook(self)
        self.tabs.pack(fill="both", expand=True)

        self.schedule_tab = ttk.Frame(self.tabs)
        self.delivery_tab = ttk.Frame(self.tabs)

        self.tabs.add(self.schedule_tab, text="Live Tracking")
        self.tabs.add(self.delivery_tab, text="Delivery Performance")

        self.create_schedule_view()
        self.create_delivery_view()

# ---------------- HELPERS ----------------

    def flatten(self):
        jobs = []
        for m in self.schedule.values():
            jobs.extend(m)
        return jobs

# ---------------- LIVE TRACKING ----------------

    def get_schedule_status(self, tasks):

        completed = {t["operation"] for t in tasks if t.get("end")}

        if "Packing" in completed:
            return "Completed"

        if "Cutting" not in completed:
            return "Cutting In Progress"
        elif "Folding" not in completed:
            return "Folding In Progress"
        else:
            return "Packing In Progress"

    def create_schedule_view(self):

        columns = ("Order", "Start Time", "Current Stage", "Status")

        tree = ttk.Treeview(self.schedule_tab, columns=columns, show="headings")

        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, anchor="center", width=200)

        tree.pack(fill="both", expand=True, padx=20, pady=20)

        jobs = self.flatten()
        order_map = defaultdict(list)

        for j in jobs:
            order_map[j["order"]].append(j)

        for order, tasks in order_map.items():

            start = min(t["start"] for t in tasks)
            status = self.get_schedule_status(tasks)

            tree.insert("", "end", values=(
                order,
                start.strftime("%Y-%m-%d %H:%M"),
                status,
                "In Progress" if "Progress" in status else "Completed"
            ))

# ---------------- DELIVERY PERFORMANCE ----------------

    def create_delivery_view(self):

        # ---------------- FILTER UI ----------------
        filter_frame = tk.Frame(self.delivery_tab)
        filter_frame.pack(fill="x", padx=20, pady=10)

        tk.Label(filter_frame, text="Status").pack(side="left", padx=5)

        self.status_filter = ttk.Combobox(
            filter_frame,
            values=["All", "On Time", "Late", "Not Delivered"],
            state="readonly",
            width=15
        )
        self.status_filter.set("All")
        self.status_filter.pack(side="left", padx=5)

        tk.Label(filter_frame, text="From").pack(side="left", padx=5)
        self.from_date = ttk.Entry(filter_frame, width=12)
        self.from_date.pack(side="left", padx=5)

        tk.Label(filter_frame, text="To").pack(side="left", padx=5)
        self.to_date = ttk.Entry(filter_frame, width=12)
        self.to_date.pack(side="left", padx=5)

        ttk.Button(
            filter_frame,
            text="Apply Filter",
            command=self.apply_filters
        ).pack(side="left", padx=10)

        # ---------------- TABLE ----------------
        columns = ("Order", "Expected", "Actual", "Status", "Delay(days)")

        self.delivery_tree = ttk.Treeview(self.delivery_tab, columns=columns, show="headings")

        for col in columns:
            self.delivery_tree.heading(col, text=col)
            self.delivery_tree.column(col, anchor="center", width=180)

        self.delivery_tree.pack(fill="both", expand=True, padx=20, pady=20)

        # Load initial data
        self.apply_filters()

# ---------------- FILTER LOGIC ----------------

    def apply_filters(self):

        # Clear table
        for row in self.delivery_tree.get_children():
            self.delivery_tree.delete(row)

        status_filter = self.status_filter.get()

        from_date = self.from_date.get()
        to_date = self.to_date.get()

        # Convert dates
        try:
            from_date = datetime.strptime(from_date, "%Y-%m-%d") if from_date else None
            to_date = datetime.strptime(to_date, "%Y-%m-%d") if to_date else None
        except:
            messagebox.showerror("Error", "Use YYYY-MM-DD format")
            return

        filtered_orders = []

        for order in self.orders_db:

            expected = order["delivery_date"]
            actual = order.get("actual_deliver_date")
            status = order["status"]

            delay = None

            if status == "Delivered" and actual:

                if actual > expected:
                    delay = (actual - expected).days
                    final_status = "Late"
                else:
                    final_status = "On Time"

            else:
                final_status = "Not Delivered"

            # -------- STATUS FILTER --------
            if status_filter != "All" and final_status != status_filter:
                continue

            # -------- DATE FILTER --------
            if actual:

                # Convert actual to datetime if it's date
                if not isinstance(actual, datetime):
                    actual_dt = datetime.combine(actual, datetime.min.time())
                else:
                    actual_dt = actual

            if from_date and actual_dt < from_date:
                continue

            if to_date and actual_dt > to_date:
                continue
            
            filtered_orders.append((
                order["order_id"],
                expected,
                actual if actual else "-",
                final_status,
                delay if delay else "-"
            ))

        # -------- SORT (FIXED) --------
        def sort_key(x):
            actual = x[2]

            if actual == "-":
                return datetime.max

            if isinstance(actual, datetime):
                return actual

            return datetime.combine(actual, datetime.min.time())

        filtered_orders.sort(key=sort_key)

        for row in filtered_orders:
            self.delivery_tree.insert("", "end", values=row)

# ---------------- EXPORT ----------------

    def export_excel(self):

        jobs = self.flatten()
        order_map = defaultdict(list)

        for j in jobs:
            order_map[j["order"]].append(j)

        # ---------------- Schedule Sheet ----------------
        schedule_rows = []

        for order, tasks in order_map.items():

            start = min(t["start"] for t in tasks)
            status = self.get_schedule_status(tasks)

            schedule_rows.append({
                "Order": order,
                "Start Time": start,
                "Stage": status
            })

        df_schedule = pd.DataFrame(schedule_rows)

        # ---------------- Delivered Sheet ----------------
        delivery_rows = []
        summary = {"On Time": 0, "Late": 0, "Not Delivered": 0}

        for order in self.orders_db:

            expected = order["delivery_date"]
            actual = order.get("actual_deliver_date")
            status = order["status"]

            delay = None

            if status == "Delivered" and actual:

                if actual > expected:
                    delay = (actual - expected).days
                    final_status = "Late"
                    summary["Late"] += 1
                else:
                    final_status = "On Time"
                    summary["On Time"] += 1

            else:
                final_status = "Not Delivered"
                summary["Not Delivered"] += 1

            delivery_rows.append({
                "Order": order["order_id"],
                "Expected": expected,
                "Actual": actual,
                "Status": final_status,
                "Delay": delay
            })

        df_delivery = pd.DataFrame(delivery_rows)
        df_summary = pd.DataFrame(list(summary.items()), columns=["Category", "Count"])

        # ---------------- Excel ----------------
        file = "Customer_Report.xlsx"

        with pd.ExcelWriter(file, engine="openpyxl") as writer:

            df_schedule.to_excel(writer, sheet_name="Live_Schedule", index=False)
            df_delivery.to_excel(writer, sheet_name="Delivered_Orders", index=False)
            df_summary.to_excel(writer, sheet_name="Summary", index=False)

            from openpyxl.chart import PieChart, Reference

            sheet = writer.sheets["Summary"]

            pie = PieChart()
            data = Reference(sheet, min_col=2, min_row=1, max_row=4)
            labels = Reference(sheet, min_col=1, min_row=2, max_row=4)

            pie.add_data(data, titles_from_data=True)
            pie.set_categories(labels)
            pie.title = "Order Delivery Performance"

            sheet.add_chart(pie, "E2")

        messagebox.showinfo("Done", f"Report saved as {file}")