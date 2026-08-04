import tkinter as tk
from tkinter import messagebox
from assets.theme import *
from database.user_dao import update_password
from utils.security import hash_password

def open_reset_password(email):
    window = tk.Toplevel()
    window.title("Quico | Reset Password")
    window.geometry("500x380")
    window.configure(bg=BG_COLOR)
    window.resizable(False, False)

    tk.Label(
        window,
        text="Reset Password",
        font=("Segoe UI", 20, "bold"),
        fg=PRIMARY_COLOR,
        bg=BG_COLOR
    ).pack(pady=(30, 5))

    card = tk.Frame(window, bg="white", padx=30, pady=30)
    card.pack(padx=20, pady=20)

    tk.Label(card, text="New Password", bg="white", font=FONT_LABEL)\
        .grid(row=0, column=0, sticky="w", pady=10)

    new_pass = tk.Entry(card, show="*", font=FONT_ENTRY, width=30)
    new_pass.grid(row=0, column=1)

    tk.Label(card, text="Confirm Password", bg="white", font=FONT_LABEL)\
        .grid(row=1, column=0, sticky="w", pady=10)

    confirm_pass = tk.Entry(card, show="*", font=FONT_ENTRY, width=30)
    confirm_pass.grid(row=1, column=1)

    def reset_password():
        if new_pass.get() != confirm_pass.get():
            messagebox.showerror("Error", "Passwords do not match")
            return

        update_password(email["value"], hash_password(new_pass.get()))
        messagebox.showinfo("Success", "Password reset successfully")
        window.destroy()

    tk.Button(
        window,
        text="Reset Password",
        bg=ACCENT_COLOR,
        fg="white",
        font=("Segoe UI", 11, "bold"),
        width=26,
        relief="flat",
        command=reset_password
    ).pack(pady=10)
