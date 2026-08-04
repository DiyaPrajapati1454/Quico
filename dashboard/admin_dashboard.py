import tkinter as tk
from tkinter import messagebox
from dashboard.profile import ProfileFrame
from dashboard.article_frame import ArticleFrame 
from dashboard.machine_frame import MachineFrame
from dashboard.admin_order_frame import AdminOrderFrame
from dashboard.time_calculation import TimeCalculationUI
from dashboard.decision_plan import DecisionModuleUI
from dashboard.scheduling_dashboard import SchedulingDashboard
from dashboard.machine_utilization import MachineUtilisationFrame
from dashboard.operation_utilization import OperationUtilisationFrame
from dashboard.what_if_planning import WhatIfPlanningFrame
from dashboard.reports_analysis import ReportsDashboard

class AdminDashboard:
    def __init__(self, admin_id, admin_name):
        self.admin_id = admin_id
        self.admin_name = admin_name
        
        self.schedules = {}  # Centralized schedule dictionary shared across frames
        self.scheduling_frame = None  # Keep reference to scheduling dashboard
        
        # ----------------------------------------------------------
        self.root = tk.Tk()
        self.root.title("QuiCo | Admin Dashboard")
        self.root.state("zoomed")  # Opens maximized (Windows)
        self.root.minsize(1100, 650)
        self.root.configure(bg="#ecf0f1")
        icon = tk.PhotoImage(file="assets/Quico.png")
        self.root.iconphoto(True, icon)
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        self.create_header()
        self.create_sidebar()
        self.create_content()

        # self.root.mainloop()

    # ================= HEADER =================
    def create_header(self):
        header = tk.Frame(self.root, bg="#2c3e50", height=60)
        header.pack(fill="x", side="top")

        tk.Label(
            header,
            text="Quico | Admin Panel",
            bg="#2c3e50",
            fg="white",
            font=("Segoe UI", 18, "bold")
        ).pack(side="left",padx=20)

        tk.Label(
            header,
            text=f"Admin: {self.admin_name}",
            bg="#2c3e50",
            fg="#ecf0f1",
            font=("Segoe UI", 11)
        ).pack(side="right", padx=20)

    # ================= SIDEBAR =================
    def create_sidebar(self):
        sidebar = tk.Frame(self.root, bg="#34495e", width=280)
        sidebar.pack(fill="y", side="left")

        menu_items = [
            ("Profile", self.show_profile),
            ("Order Management", self.show_orders),
            ("Article & Specification", self.show_articles),
            ("Machine Management", self.show_machines),
            ("Time & Cost Calculation", self.show_cost_time),
            ("Production Scheduling", self.show_scheduling),
            ("Decision Support", self.show_decision),
            ("Machine Utilization", self.show_machine_utilization),
            ("Operation Utilization", self.show_operation_utilization),
            ("What-If Analysis", self.show_what_if),
            ("Reports & Analysis", self.show_reports),
            ("Logout", self.logout)
        ]

        for text, cmd in menu_items:
            btn = tk.Button(
                sidebar,
                text=text,
                command=cmd,
                anchor="w",
                padx=20,
                height=2,
                bg="#34495e",
                fg="white",
                font=("Segoe UI", 11),
                relief="flat",
                activebackground="#1abc9c",
                cursor="hand2"
            )
            btn.pack(fill="x")

    # ================= CONTENT =================
    def create_content(self):
        self.content = tk.Frame(self.root, bg="#ecf0f1")
        self.content.pack(fill="both", expand=True)
        self.show_home()

    def clear(self):
        for w in self.content.winfo_children():
            w.destroy()

    # ================= SCREENS =================
    def show_home(self):
        self.clear()
        tk.Label(
            self.content,
            text="Production Planning & Decision Dashboard",
            font=("Segoe UI", 20, "bold"),
            bg="#ecf0f1"
        ).pack(pady=30)

        tk.Label(
            self.content,
            text="Manage orders, machines, scheduling and optimization decisions.",
            font=("Segoe UI", 12),
            bg="#ecf0f1",
            fg="#7f8c8d"
        ).pack()

    def show_profile(self):
        self.clear()
        profile_frame=ProfileFrame(self.content,self.admin_id)
        profile_frame.pack(fill="both",expand=True)

    def show_orders(self):
        self.clear()
        order_frame=AdminOrderFrame(self.content)
        order_frame.pack(fill="both",expand=True)

    def show_articles(self):
        self.clear()
        article_frame=ArticleFrame(self.content)
        article_frame.pack(fill="both",expand=True)

    def show_machines(self):
        self.clear()
        machine_frame=MachineFrame(self.content)
        machine_frame.pack(fill="both",expand=True)

    def show_cost_time(self):
        self.clear()
        cost_frame=TimeCalculationUI(self.content)
        cost_frame.pack(fill="both",expand=True)

    def show_scheduling(self):
        self.clear()
        self.scheduling_frame = SchedulingDashboard(self.content, self.schedules)
        self.scheduling_frame.pack(fill="both", expand=True)
    
    def show_decision(self):
        self.clear()
        decision_frame=DecisionModuleUI(self.content)
        decision_frame.pack(fill="both",expand=True)

    def show_machine_utilization(self):
        self.clear()
        
        if self.scheduling_frame and self.scheduling_frame.schedules:
            util_frame = MachineUtilisationFrame(self.content)
            util_frame.pack(fill="both", expand=True)
        else:
            tk.Label(self.content, text="No scheduling data available.").pack()    
    
    def show_operation_utilization(self):
        self.clear()
        
        if self.scheduling_frame and self.scheduling_frame.schedules:
            operation_frame = OperationUtilisationFrame(self.content)
            operation_frame.pack(fill="both", expand=True)
        else:
            tk.Label(self.content, text="No scheduling data available.").pack()    
    
    def show_what_if(self):
        self.clear()
        planning_frame=WhatIfPlanningFrame(self.content)
        planning_frame.pack(fill="both",expand=True)

    def show_reports(self):

        self.clear()

        report_frame = ReportsDashboard(
            self.content,
        )

        report_frame.pack(fill="both", expand=True)

    def simple_page(self, title, desc):
        self.clear()
        tk.Label(self.content, text=title, font=("Segoe UI", 18, "bold"), bg="#ecf0f1").pack(pady=20)
        tk.Label(self.content, text=desc, font=("Segoe UI", 11), bg="#ecf0f1").pack()

    # ================= LOGOUT =================
    def logout(self):
        if messagebox.askyesno("Logout", "Do you want to logout?"):
            from auth.login import open_login
            self.root.destroy()
            open_login()