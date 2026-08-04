import tkinter as tk
from tkinter import ttk
import matplotlib
matplotlib.use("TkAgg")  # Important to prevent hanging issue
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from utils.load_schedule import load_schedule_from_json
from dashboard.scheduling_dashboard import WORK_START, WORK_END
from database.machine_dao import get_all_machines  # 🔹 Adjust if different


class MachineUtilisationFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.schedules = load_schedule_from_json("data/final_schedule.json")
        self.configure(bg="#f4f4f4")

        self.create_ui()
        self.populate_table_and_graph()

    # ================= UI =================
    def create_ui(self):

        tk.Label(
            self,
            text="Machine Utilisation Dashboard",
            font=("Segoe UI", 18, "bold"),
            bg="#f4f4f4"
        ).pack(pady=10)

        # ===== Table Frame =====
        self.table_frame = tk.Frame(self, bg="#f4f4f4")
        self.table_frame.pack(fill="x", padx=20, pady=(0, 10))

        columns = (
            "Machine",
            "Available (hrs)",
            "Used (hrs)",
            "Idle (hrs)",
            "Utilisation (%)",
            "Status"
        )

        self.tree = ttk.Treeview(
            self.table_frame,
            columns=columns,
            show="headings",
            height=6
        )

        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor="center")

        self.tree.pack(side="left", fill="x", expand=True)

        scrollbar = ttk.Scrollbar(
            self.table_frame,
            orient="vertical",
            command=self.tree.yview
        )
        scrollbar.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=scrollbar.set)

        # ===== Graph Frame =====
        self.graph_frame = tk.Frame(self, bg="#f4f4f4")
        self.graph_frame.pack(fill="both", expand=True, padx=20, pady=10)

    # ================= Core Logic =================
    def populate_table_and_graph(self):

        # Clear old rows
        for row in self.tree.get_children():
            self.tree.delete(row)

        plt.close('all')  # Prevent lingering figures

        total_available_seconds = (WORK_END - WORK_START) * 3600

        machine_names = []
        utilizations = []

        # 🔹 Fetch ALL machines
        all_machines = get_all_machines()

        for machine in all_machines:
            machine_id = machine["m_id"]
            machine_name = machine["m_name"]

            jobs = self.schedules.get(machine_id, [])

            if jobs:
                used_seconds = sum(
                    (job["end"] - job["start"]).total_seconds()
                    for job in jobs
                )
                status = "Tasks Planned"
            else:
                used_seconds = 0
                status = "No Task Planned"

            idle_seconds = total_available_seconds - used_seconds

            utilization = (
                (used_seconds / total_available_seconds) * 100
                if total_available_seconds > 0 else 0
            )

            # Insert into table
            self.tree.insert("", tk.END, values=(
                machine_name,
                f"{total_available_seconds / 3600:.2f}",
                f"{used_seconds / 3600:.2f}",
                f"{idle_seconds / 3600:.2f}",
                f"{utilization:.2f}",
                status
            ))

            machine_names.append(machine_name)
            utilizations.append(utilization)

        # Plot Graph
        self.plot_graph(machine_names, utilizations)

    # ================= Graph =================
    def plot_graph(self, machine_names, utilizations):

        plt.close('all')

        fig, ax = plt.subplots(figsize=(7, 4))  # 🔹 Reduced width

        bars = ax.barh(machine_names, utilizations)  # 🔹 Horizontal bars

        ax.set_xlim(0, 100)
        ax.set_xlabel("Utilisation %")
        ax.set_title("Machine Utilisation Overview")

        # Add grid for better readability
        ax.grid(axis='x', linestyle='--', alpha=0.4)

        # Add percentage labels
        for i, val in enumerate(utilizations):
            ax.text(val + 1, i, f"{val:.1f}%", va='center', fontsize=9)

        fig.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=self.graph_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
    
    # ================= Safe Destroy =================
    def destroy(self):
        plt.close('all')  # Prevent background matplotlib thread
        super().destroy()