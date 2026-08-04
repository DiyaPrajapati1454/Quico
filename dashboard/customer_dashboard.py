import tkinter as tk
from tkinter import messagebox
from dashboard.profile import ProfileFrame
from dashboard.order_frame import OrderFrame
from dashboard.customer_order_frame import CustomerOrderFrame
from dashboard.customer_reports_analysis import CustomerReports
from utils.load_schedule import load_schedule_from_json

class CustomerDashboard:
    def __init__(self, user_id, username):
        self.user_id = user_id
        self.username = username

        self.root = tk.Tk()
        self.root.title("QuiCo - Customer Dashboard")
        self.root.geometry("1100x600")
        self.root.configure(bg="#ecf0f1")
        icon = tk.PhotoImage(file="assets/Quico.png")
        self.root.iconphoto(True, icon)
        self.create_header()
        self.create_sidebar()
        self.create_content_area()

        self.root.mainloop()

    # ===== HEADER =====
    def create_header(self):
        header = tk.Frame(self.root, bg="#2c3e50", height=60)
        header.pack(fill="x", side="top")

        tk.Label(
            header,
            text="QuiCo",
            bg="#2c3e50",
            fg="white",
            font=("Segoe UI", 18, "bold")
        ).pack(side="left", padx=20)

        tk.Label(
            header,
            text=f"Welcome, {self.username}",
            bg="#2c3e50",
            fg="#ecf0f1",
            font=("Segoe UI", 11)
        ).pack(side="right", padx=20)

    # ===== SIDEBAR =====
    def create_sidebar(self):
        sidebar = tk.Frame(self.root, bg="#34495e", width=220)
        sidebar.pack(fill="y", side="left")

        menu_items = [
            ("Profile", self.show_profile),
            ("Place Order", self.show_place_order),
            ("My Orders", self.show_orders),
            ("Reports & Analysis", self.show_reports),
            ("Logout", self.logout)
        ]

        for text, command in menu_items:
            btn = tk.Button(
                sidebar,
                text=text,
                command=command,
                anchor="w",
                padx=20,
                height=2,
                bg="#34495e",
                fg="white",
                font=("Segoe UI", 11),
                relief="flat",
                activebackground="#1abc9c",
                activeforeground="white",
                cursor="hand2"
            )
            btn.pack(fill="x")

    # ===== CONTENT AREA =====
    def create_content_area(self):
        self.content = tk.Frame(self.root, bg="#ecf0f1")
        self.content.pack(fill="both", expand=True)

        self.show_dashboard_home()

    def clear_content(self):
        for widget in self.content.winfo_children():
            widget.destroy()

    # ===== PAGES =====
    def show_dashboard_home(self):
        self.clear_content()
        tk.Label(
            self.content,
            text="Customer Dashboard",
            bg="#ecf0f1",
            fg="#2c3e50",
            font=("Segoe UI", 20, "bold")
        ).pack(pady=30)

        tk.Label(
            self.content,
            text="Manage your orders, track deliveries, and view reports.",
            bg="#ecf0f1",
            fg="#7f8c8d",
            font=("Segoe UI", 12)
        ).pack()

    def show_profile(self):
        self.clear_content()
        profile_frame=ProfileFrame(self.content,self.user_id)
        profile_frame.pack(fill="both",expand=True)

    def show_place_order(self):
        self.clear_content()
        order_frame=OrderFrame(self.content,self.user_id)
        order_frame.pack(fill="both",expand=True)

    def show_orders(self):
        self.clear_content()
        cust_order_frame=CustomerOrderFrame(self.content,self.user_id)
        cust_order_frame.pack(fill="both",expand=True)

    def show_reports(self):
        self.clear_content()
        current_schedule = load_schedule_from_json("data/final_schedule.json")
        cust_reports = CustomerReports(self.content, current_schedule)
        cust_reports.pack(fill="both",expand=True)

    def logout(self):
        if messagebox.askyesno("Logout", "Do you want to logout?"):
            from auth.login import open_login
            self.root.destroy()
            open_login()
