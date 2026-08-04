import tkinter as tk
from tkinter import messagebox
from assets.theme import *
from utils.validation import validate_registration
from utils.security import hash_password
from database.user_dao import insert_user
from mysql.connector import Error


def open_registration():
    window = tk.Tk()
    window.title("Quico | User Registration")
    window.geometry("500x500")
    icon = tk.PhotoImage(file="assets/quico.png")
    window.iconphoto(True, icon)
    window.configure(bg=BG_COLOR)
    window.resizable(False, False)

    # ---------- Header ----------
    header = tk.Label(
        window,
        text="Create Your Quico Account",
        font=("Segoe UI", 20, "bold"),
        fg=PRIMARY_COLOR,
        bg=BG_COLOR
    )
    header.pack(pady=(20, 5))

    subtitle = tk.Label(
        window,
        text="Supply Chain Planning for Quibis Manufacturing",
        font=("Segoe UI", 10),
        fg="#6b7280",
        bg=BG_COLOR
    )
    subtitle.pack(pady=(0, 15))

    # ---------- Card ----------
    card = tk.Frame(
        window,
        bg="white",
        padx=30,
        pady=25,
        highlightbackground="#d6dbe1",
        highlightthickness=1
    )
    card.pack(padx=20,pady=10)

    # Grid layout
    card.columnconfigure(0, weight=0)
    card.columnconfigure(1, weight=1)

    # Username
    tk.Label(card, text="Username", bg="white", font=FONT_LABEL).grid(row=0, column=0, sticky="w", pady=8)
    username_entry = tk.Entry(card, font=FONT_ENTRY, width=28,relief="solid",
    borderwidth=1,highlightthickness=1,highlightbackground="#E8E8E8",highlightcolor=PRIMARY_COLOR)
    username_entry.grid(row=0, column=1, pady=8,padx=(10,0))

    # Email
    tk.Label(card, text="Email", bg="white", font=FONT_LABEL).grid(row=1, column=0, sticky="w", pady=8)
    email_entry = tk.Entry(card, font=FONT_ENTRY, width=28,relief="solid",
    borderwidth=1,highlightthickness=1,highlightbackground="#E8E8E8",highlightcolor=PRIMARY_COLOR)
    email_entry.grid(row=1, column=1, pady=8,padx=(10,0))

    # Password
    tk.Label(card, text="Password", bg="white", font=FONT_LABEL).grid(row=2, column=0, sticky="w", pady=8)
    password_entry = tk.Entry(card, show="*", font=FONT_ENTRY, width=28,relief="solid",
    borderwidth=1,highlightthickness=1,highlightbackground="#E8E8E8",highlightcolor=PRIMARY_COLOR)
    password_entry.grid(row=2, column=1, pady=8,padx=(10,0))

    # Role
    tk.Label(card, text="Role", bg="white", font=FONT_LABEL).grid(row=3, column=0, sticky="nw", pady=(10,5))

    role_var = tk.StringVar(value="customer")
    role_frame = tk.Frame(card, bg="white")
    role_frame.grid(row=3, column=1, sticky="w",pady=(10,5))

    tk.Radiobutton(
        role_frame, text="Customer", variable=role_var,
        value="customer", bg="white",font=("Segoe UI",10),
        selectcolor="white",indicatoron=1,command="selection",
        padx=10,pady=4
    ).pack(side="left", padx=(0,20),anchor="w")

    tk.Radiobutton(
        role_frame, text="Admin", variable=role_var,
        value="admin", bg="white",font=("Segoe UI",10),
        selectcolor="white",indicatoron=1,command="selection",
        padx=10,pady=4
    ).pack(side="left")

    # ---------- Register Logic ----------
    def register_user():
        from auth.login import open_login
        username = username_entry.get()
        email = email_entry.get()
        password = password_entry.get()
        role = role_var.get()

        is_valid, result = validate_registration(username, email, password)
        if not is_valid:
            messagebox.showerror("Validation Error", result)
            return

        try:
            password_hash = hash_password(password)
            insert_user(username, email, password_hash, role)

            messagebox.showinfo(
                "Registration Successful",
                f"Account created successfully!\nRole: {role.capitalize()}"
            )
            window.destroy()
            open_login()

        except Error as e:
            if "Duplicate entry" in str(e):
                messagebox.showerror("Registration Failed", "Email already registered")
            else:
                messagebox.showerror("Database Error", str(e))

    # ---------- Button ----------
    tk.Button(
        window,
        text="Register",
        bg=ACCENT_COLOR,
        fg="white",
        activebackground="#2f855a",
        font=("Segoe UI", 11, "bold"),
        width=26,
        height=1,
        relief="flat",
        command=register_user
    ).pack(pady=25)

    window.mainloop()
