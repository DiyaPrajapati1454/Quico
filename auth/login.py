import tkinter as tk
from tkinter import messagebox
from assets.theme import *
from utils.validation import validate_login
from database.user_dao import authenticate_user
from auth.register import open_registration
from dashboard.admin_dashboard import AdminDashboard
from dashboard.customer_dashboard import CustomerDashboard
from auth.forgot_password import open_forgot_password


def open_login():
    window = tk.Tk()
    window.title("Quico | User Login")
    window.geometry("500x560")
    icon = tk.PhotoImage(file="assets/quico.png")
    window.iconphoto(True, icon)
    window.configure(bg=BG_COLOR)
    window.resizable(True, True)
    window.minsize(420,500)

    # ================= Header =================
    tk.Label(
        window,
        text="Welcome Back to Quico",
        font=("Segoe UI", 20, "bold"),
        fg=PRIMARY_COLOR,
        bg=BG_COLOR
    ).pack(pady=(30, 5))

    tk.Label(
        window,
        text="Supply Chain Planning for Quibis Manufacturing",
        font=("Segoe UI", 10),
        fg="#6b7280",
        bg=BG_COLOR
    ).pack(pady=(0, 25))

    # ================= Card =================
    card = tk.Frame(
        window,
        bg="white",
        padx=30,
        pady=30,
        highlightbackground="#d6dbe1",
        highlightthickness=1
    )
    card.pack(padx=20)

    # -------- Email --------
    tk.Label(card, text="Email", bg="white", font=FONT_LABEL)\
        .grid(row=0, column=0, sticky="w", pady=12)

    email_entry = tk.Entry(
        card,
        font=FONT_ENTRY,
        width=28,
        relief="solid",
        borderwidth=1
    )
    email_entry.grid(row=0, column=1, padx=(15, 0), pady=12)

    # -------- Password --------
    tk.Label(card, text="Password", bg="white", font=FONT_LABEL)\
        .grid(row=1, column=0, sticky="w", pady=12)

    password_entry = tk.Entry(
        card,
        show="*",
        font=FONT_ENTRY,
        width=28,
        relief="solid",
        borderwidth=1
    )
    password_entry.grid(row=1, column=1, padx=(15, 0), pady=12)

    # -------- Role Selection --------
    tk.Label(
        card,
        text="Role",
        bg="white",
        font=FONT_LABEL
    ).grid(row=2, column=0, sticky="w", pady=(18, 8))

    role_var = tk.StringVar(value="customer")

    role_frame = tk.Frame(card, bg="white")
    role_frame.grid(row=2, column=1, sticky="w", padx=(15, 0), pady=(18, 8))

    tk.Radiobutton(
        role_frame,
        text="Customer",
        variable=role_var,
        value="customer",
        bg="white"
    ).pack(side="left", padx=(0, 20))

    tk.Radiobutton(
        role_frame,
        text="Admin",
        variable=role_var,
        value="admin",
        bg="white"
    ).pack(side="left")

    # ================= Login Logic =================
    def handle_login():
        email = email_entry.get().strip()
        password = password_entry.get().strip()
        selected_role = role_var.get()

        # Step 1: Validate inputs
        is_valid, error = validate_login(email, password)
        if not is_valid:
            messagebox.showerror("Validation Error", error)
            return

        # Step 2: Authenticate user
        user = authenticate_user(email, password)
        if not user:
            messagebox.showerror("Login Failed", "Invalid email or password")
            return

        # Step 3: TEMP role validation (UI purpose)
        if user["role"] != selected_role:
            messagebox.showerror(
                "Role Mismatch",
                "You are unauthorised"
            )
            return

        # Step 4: Redirect
        window.destroy()
        if user["role"] == "admin":
            AdminDashboard(user["uid"], user["uname"])
        else:
            CustomerDashboard(user["uid"], user["uname"])

    # ================= Login Button =================
    tk.Button(
        window,
        text="Login",
        bg=ACCENT_COLOR,
        fg="white",
        font=("Segoe UI", 11, "bold"),
        width=26,
        relief="flat",
        command=handle_login
    ).pack(pady=(25, 12))

    # ================= Links =================
    links_frame = tk.Frame(window, bg=BG_COLOR)
    links_frame.pack()

    tk.Label(
        links_frame,
        text="Forgot Password?",
        fg=PRIMARY_COLOR,
        bg=BG_COLOR,
        cursor="hand2",
        font=("Segoe UI", 9, "underline")
    ).pack(pady=(0, 6))
    tk.Label(
        links_frame,
        text="Not registered yet?",
        bg=BG_COLOR,
        font=("Segoe UI", 9)
    ).pack(pady=(0, 4))

    tk.Button(
        links_frame,
        text="Create Account",
        font=("Segoe UI", 9, "underline"),
        fg=PRIMARY_COLOR,
        bg=BG_COLOR,
        relief="flat",
        command=lambda: [window.destroy(), open_registration()]
    ).pack()

    window.mainloop()
