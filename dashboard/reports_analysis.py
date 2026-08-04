import tkinter as tk
from tkinter import ttk, messagebox
from collections import defaultdict
from utils.load_schedule import load_schedule_from_json
import pandas as pd
from openpyxl.chart import BarChart, Reference

class ReportsDashboard(tk.Frame):

    def __init__(self, parent):
        super().__init__(parent)

        self.auto_schedule = load_schedule_from_json("data/auto_schedule.json")
        self.manual_schedule = load_schedule_from_json("data/manual_schedule.json")
        self.current_schedule = load_schedule_from_json("data/final_schedule.json")
        self.configure(bg="#f4f4f4")

        self.build_ui()


# ---------------- UI ----------------

    def build_ui(self):

        header = tk.Frame(self, bg="#f4f4f4")
        header.pack(fill="x", pady=10)

        title = tk.Label(
            header,
            text="Scheduling Analysis Dashboard",
            font=("Segoe UI", 18, "bold"),
            bg="#f4f4f4"
        )
        title.pack(side="left", padx=15)

        export_btn = ttk.Button(
            header,
            text="Generate Analysis Report",
            command=self.export_excel
        )
        export_btn.pack(side="right", padx=15)

        self.tabs = ttk.Notebook(self)
        self.tabs.pack(fill="both", expand=True, padx=10, pady=10)

        self.summary_tab = ttk.Frame(self.tabs)
        self.machine_tab = ttk.Frame(self.tabs)
        self.order_tab = ttk.Frame(self.tabs)

        self.tabs.add(self.summary_tab, text="Schedule Summary")
        self.tabs.add(self.machine_tab, text="Machine Workload")
        self.tabs.add(self.order_tab, text="Order Processing")

        self.create_summary_report()
        self.create_machine_report()
        self.create_order_report()


# ---------------- Helpers ----------------

    def flatten_schedule(self, schedule):

        jobs = []

        if not schedule:
            return jobs

        for machine_jobs in schedule.values():
            jobs.extend(machine_jobs)

        return jobs


# ---------------- Schedule Summary ----------------

    def create_summary_report(self):

        columns = ("Description", "Auto Schedule", "Manual Schedule")

        tree = ttk.Treeview(
            self.summary_tab,
            columns=columns,
            show="headings"
        )

        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, anchor="center", width=220)

        tree.pack(fill="both", expand=True, padx=20, pady=20)

        auto_jobs = self.flatten_schedule(self.auto_schedule)
        manual_jobs = self.flatten_schedule(self.manual_schedule)

        auto_orders = len(set(j["order"] for j in auto_jobs))
        manual_orders = len(set(j["order"] for j in manual_jobs))

        auto_total_time = self.total_time(auto_jobs)
        manual_total_time = self.total_time(manual_jobs)

        auto_machines = len(set(j["machine_name"] for j in auto_jobs))
        manual_machines = len(set(j["machine_name"] for j in manual_jobs))

        tree.insert("", "end", values=("Total Orders Processed", auto_orders, manual_orders))
        tree.insert("", "end", values=("Total Machines Used", auto_machines, manual_machines))
        tree.insert("", "end", values=("Total Production Time (hours)", auto_total_time, manual_total_time))


# ---------------- Machine Workload ----------------

    def create_machine_report(self):

        columns = ("Machine", "Working Hours", "Utilization (%)", "Observation")

        tree = ttk.Treeview(
            self.machine_tab,
            columns=columns,
            show="headings"
        )

        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, anchor="center", width=200)

        tree.pack(fill="both", expand=True, padx=20, pady=20)

        machine_hours = defaultdict(float)

        jobs = self.flatten_schedule(self.current_schedule)

        for j in jobs:

            duration = (j["end"] - j["start"]).total_seconds() / 3600

            machine_hours[j["machine_name"]] += duration

        total_time = self.total_time(jobs)

        for machine, hours in machine_hours.items():

            if total_time == 0:
                utilization = 0
            else:
                utilization = (hours / total_time) * 100

            if utilization > 75:
                note = "High usage - possible bottleneck"
            elif utilization < 40:
                note = "Low usage - machine underutilized"
            else:
                note = "Balanced usage"

            tree.insert(
                "",
                "end",
                values=(
                    machine,
                    round(hours,2),
                    round(utilization,2),
                    note
                )
            )


# ---------------- Order Processing ----------------

    def create_order_report(self):

        columns = ("Order", "Start Time", "Completion Time", "Total Time (hours)")

        tree = ttk.Treeview(
            self.order_tab,
            columns=columns,
            show="headings"
        )

        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, anchor="center", width=200)

        tree.pack(fill="both", expand=True, padx=20, pady=20)

        jobs = self.flatten_schedule(self.auto_schedule)

        order_map = defaultdict(list)

        for j in jobs:
            order_map[j["order"]].append(j)

        for order, tasks in order_map.items():

            start = min(t["start"] for t in tasks)
            end = max(t["end"] for t in tasks)

            total = (end - start).total_seconds() / 3600

            tree.insert(
                "",
                "end",
                values=(
                    order,
                    start.strftime("%Y-%m-%d %H:%M"),
                    end.strftime("%Y-%m-%d %H:%M"),
                    round(total,2)
                )
            )


# ---------------- Total Time Helper ----------------

    def total_time(self, jobs):

        if not jobs:
            return 0

        start = min(j["start"] for j in jobs)
        end = max(j["end"] for j in jobs)

        return round((end - start).total_seconds() / 3600,2)


# ---------------- Excel Export ----------------

    def export_excel(self):

    # ===============================
    # 1️ PREPARE DATA
    # ===============================

        auto_jobs = self.flatten_schedule(self.auto_schedule)
        manual_jobs = self.flatten_schedule(self.manual_schedule)
        current_jobs = self.flatten_schedule(self.current_schedule)

        file_name = "Scheduling_Analysis_Report.xlsx"

        with pd.ExcelWriter(file_name, engine="openpyxl") as writer:

            # ===============================
            # 2️ SCHEDULE DETAILS
            # ===============================

            schedule_rows = []

            for job in current_jobs:

                # --- Setup Hours ---
                setup_hours = 0
                if job.get("setup_start") and job.get("setup_end"):
                    setup_hours = (
                        job["setup_end"] - job["setup_start"]
                    ).total_seconds() / 3600

                # --- Production Hours ---
                production_hours = (
                    job["end"] - job["start"]
                ).total_seconds() / 3600

                schedule_rows.append({
                    "Order": job["order"],
                    "Operation": job["operation"],
                    "Machine": job["machine_name"],
                    "Start": job["start"],
                    "End": job["end"],
                    "Setup Hours": round(setup_hours, 2),
                    "Production Hours": round(production_hours, 2)
                })

            df_schedule = pd.DataFrame(schedule_rows)

            df_schedule.to_excel(
                writer,
                sheet_name="Schedule_Details",
                index=False
            )

            # ===============================
            # 3️ MACHINE UTILISATION
            # ===============================

            machine_stats = defaultdict(lambda: {
                "production": 0,
                "setup": 0,
                "start": None,
                "end": None
            })

            for job in current_jobs:

                machine = job["machine_name"]

                production = (
                    job["end"] - job["start"]
                ).total_seconds() / 3600

                machine_stats[machine]["production"] += production

                if job.get("setup_start") and job.get("setup_end"):
                    setup = (
                        job["setup_end"] - job["setup_start"]
                    ).total_seconds() / 3600

                    machine_stats[machine]["setup"] += setup

                # Track earliest start
                if machine_stats[machine]["start"] is None or job["start"] < machine_stats[machine]["start"]:
                    machine_stats[machine]["start"] = job["start"]

                # Track latest end
                if machine_stats[machine]["end"] is None or job["end"] > machine_stats[machine]["end"]:
                    machine_stats[machine]["end"] = job["end"]

            machine_rows = []
            machine_jobs = defaultdict(list)

            for job in current_jobs:
                machine_jobs[job["machine_name"]].append(job)
            
            for machine, data in machine_stats.items():

                jobs = sorted(machine_jobs[machine], key=lambda x: x["start"])

                idle_hours = 0

                for i in range(len(jobs) - 1):

                    gap = abs(
                        jobs[i+1]["start"] - jobs[i]["end"]
                    ).total_seconds() / 3600

                    if gap > 0:
                        idle_hours += gap

                available_hours = (
                    data["end"] - data["start"]
                ).total_seconds() / 3600

                utilisation = (
                    (available_hours - idle_hours) / available_hours * 100
                    if available_hours > 0 else 0
                )

                machine_rows.append({
                    "Machine": machine,
                    "Available Hours": round(available_hours, 2),
                    "Production Hours": round(data["production"], 2),
                    "Setup Hours": round(data["setup"], 2),
                    "Idle Hours": round(idle_hours, 2),
                    "Utilisation %": round(utilisation, 2)
                })
            df_machine = pd.DataFrame(machine_rows)

            df_machine.to_excel(
                writer,
                sheet_name="Machine_Utilisation",
                index=False
            )

            # ===============================
            # 4️ IDLE TIME ANALYSIS
            # ===============================

            idle_rows = []

            for machine, data in machine_stats.items():

                available = (
                    data["end"] - data["start"]
                ).total_seconds() / 3600

                working = data["production"] + data["setup"]

                idle = abs( available - working )

                idle_rows.append({
                    "Machine": machine,
                    "Idle Hours": round(idle, 2),
                    "Idle Percentage": round(
                        (idle / available) * 100 if available > 0 else 0,
                        2
                    )
                })

            df_idle = pd.DataFrame(idle_rows)

            df_idle.to_excel(
                writer,
                sheet_name="Idle_Time_Analysis",
                index=False
            )

            # ===============================
            # 5️ ORDER COMPLETION
            # ===============================

            order_map = defaultdict(list)

            for job in current_jobs:
                order_map[job["order"]].append(job)

            order_rows = []

            for order, tasks in order_map.items():

                start_time = min(t["start"] for t in tasks)
                end_time = max(t["end"] for t in tasks)

                lead_time = (
                    end_time - start_time
                ).total_seconds() / 3600

                order_rows.append({
                    "Order": order,
                    "Start Time": start_time,
                    "Completion Time": end_time,
                    "Lead Time Hours": round(lead_time, 2)
                })

            df_order = pd.DataFrame(order_rows)

            df_order.to_excel(
                writer,
                sheet_name="Order_Completion",
                index=False
            )

            # ===============================
            # 6️ AUTO vs MANUAL COMPARISON
            # ===============================

            auto_time = self.total_time(auto_jobs)
            manual_time = self.total_time(manual_jobs)

            auto_orders = len(set(j["order"] for j in auto_jobs))
            manual_orders = len(set(j["order"] for j in manual_jobs))

            auto_machines = len(set(j["machine_name"] for j in auto_jobs))
            manual_machines = len(set(j["machine_name"] for j in manual_jobs))

            comparison = [
                ["Total Orders", auto_orders, manual_orders],
                ["Machines Used", auto_machines, manual_machines],
                ["Total Production Time (hours)", auto_time, manual_time]
            ]

            df_compare = pd.DataFrame(
                comparison,
                columns=["Metric", "Auto Schedule", "Manual Schedule"]
            )

            df_compare.to_excel(
                writer,
                sheet_name="Auto_vs_Manual",
                index=False
            )

            # ===============================
            # 7️ CHARTS
            # ===============================

            workbook = writer.book
            sheet = writer.sheets["Machine_Utilisation"]

            # ---- Production vs Setup Chart ----
            chart1 = BarChart()
            chart1.title = "Machine Production vs Setup Hours"
            chart1.y_axis.title = "Hours"
            chart1.x_axis.title = "Machine"
            chart1.x_axis.position = "b"
            chart1.x_axis.tickLblPos = "low"
            chart1.x_axis.majorTickMark = "out"
            data = Reference(
                sheet,
                min_col=3,
                max_col=4,
                min_row=1,
                max_row=len(machine_rows) + 1
            )

            categories = Reference(
                sheet,
                min_col=1,
                min_row=2,
                max_row=len(machine_rows) + 1
            )

            chart1.add_data(data, titles_from_data=True)
            chart1.set_categories(categories)
            chart1.legend.position = "tr"
            sheet.add_chart(chart1, "H2")

            # ---- Utilisation Chart ----
            chart2 = BarChart()
            chart2.title = "Machine Utilisation %"

            data2 = Reference(
                sheet,
                min_col=6,
                min_row=1,
                max_row=len(machine_rows) + 1
            )

            chart2.add_data(data2, titles_from_data=True)
            chart2.set_categories(categories)

            sheet.add_chart(chart2, "H20")

        # ===============================
        # REPORT COMPLETION MESSAGE
        # ===============================

        messagebox.showinfo(
            "Report Generated",
            f"Excel report saved as {file_name}"
        )