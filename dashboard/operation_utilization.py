import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import timedelta
from utils.load_schedule import load_schedule_from_json
from dashboard.scheduling_dashboard import WORK_START, WORK_END

class OperationUtilisationFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.schedules = load_schedule_from_json("data/final_schedule.json")
        self.configure(bg="#f4f4f4")
        self.create_ui()
        self.populate_table_and_graph()

    def create_ui(self):
        # ===== Header =====
        tk.Label(
            self,
            text="Operation Utilisation Dashboard",
            font=("Segoe UI", 18, "bold"),
            bg="#f4f4f4"
        ).pack(pady=10)

        # ===== Table Frame =====
        self.table_frame = tk.Frame(self, bg="#f4f4f4")
        self.table_frame.pack(fill="x", padx=20, pady=(0,10))

        columns = ("Operation", "Used Time (hrs)", "Idle Time (hrs)", "Utilization (%)")
        self.tree = ttk.Treeview(self.table_frame, columns=columns, show="headings", height=6)
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor="center")
        self.tree.pack(side="left", fill="x", expand=True)

        # Scrollbar for table
        scrollbar = ttk.Scrollbar(self.table_frame, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=scrollbar.set)

        # ===== Graph Frame =====
        self.graph_frame = tk.Frame(self, bg="#f4f4f4")
        self.graph_frame.pack(fill="both", expand=True, padx=20, pady=10)

    def populate_table_and_graph(self):
        # Clear table
        for row in self.tree.get_children():
            self.tree.delete(row)

        operations = ["Cutting", "Folding", "Packing"]
        operation_times = {op: 0 for op in operations}
        total_available_seconds = (WORK_END - WORK_START) * 3600

        # Count number of machines for each operation
        machine_counts = { "Cutting": 0, "Folding": 0, "Packing": 0 }
        for jobs in self.schedules.values():
            for job in jobs:
                op = job["operation"]
                operation_times[op] += (job["end"] - job["start"]).total_seconds()
                machine_counts[op] += 1  # this counts total tasks, not unique machines

        # If you want to normalize by number of machines
        # You could alternatively pass machine info if you want exact available hours
        utilizations = []
        op_names = []
        for op in operations:
            used = operation_times[op]
            # Avoid dividing by zero
            available = total_available_seconds * max(machine_counts[op], 1)
            utilization = (used / available) * 100
            idle = available - used

            self.tree.insert("", tk.END, values=(
                op,
                f"{used/3600:.2f}",
                f"{idle/3600:.2f}",
                f"{utilization:.2f}"
            ))

            op_names.append(op)
            utilizations.append(utilization)

        # Plot graph
        self.plot_graph(op_names, utilizations)

    def plot_graph(self, op_names, utilizations):
        plt.close("all")
        fig, ax = plt.subplots(figsize=(6,4))
        bars = ax.bar(op_names, utilizations, color="#f97316")
        ax.set_ylim(0, 100)
        ax.set_ylabel("Utilization %")
        ax.set_title("Operation Utilisation")
        for i, val in enumerate(utilizations):
            ax.text(i, val + 1, f"{val:.1f}%", ha="center")
        fig.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=self.graph_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)