import tkinter as tk
from tkinter import messagebox
import random

from assets.theme import *
from database.user_dao import get_user_by_email
from utils.mailer import send_otp_email
from auth.reset_password import open_reset_password 

def open_forgot_password():
    window = tk.Toplevel()
    window.title("Quico | Forgot Password")
    window.geometry("500x420")
    window.configure(bg=BG_COLOR)
    window.resizable(False, False)

    otp_generated = {"value": None}
    verified_email={"value":None}

    # ---------- Header ----------
    title_label = tk.Label(
        window,
        text="Forgot Password",
        font=("Segoe UI", 20, "bold"),
        fg=PRIMARY_COLOR,
        bg=BG_COLOR
    )
    title_label.pack(pady=(30, 5))

    subtitle_label = tk.Label(
        window,
        text="Verify your registered email",
        font=("Segoe UI", 10),
        fg="#6b7280",
        bg=BG_COLOR
    )
    subtitle_label.pack(pady=(0, 20))

    # ---------- Card ----------
    card = tk.Frame(
        window,
        bg="white",
        padx=30,
        pady=30,
        highlightbackground="#d6dbe1",
        highlightthickness=1
    )
    card.pack(padx=20, pady=10)

    # ---------- EMAIL UI ----------
    tk.Label(card, text="Registered Email", bg="white", font=FONT_LABEL)\
        .grid(row=0, column=0, sticky="w", pady=(0, 8))

    email_entry = tk.Entry(
        card, font=FONT_ENTRY, width=30,
        relief="solid", borderwidth=1,
        highlightthickness=1,
        highlightbackground="#E8E8E8",
        highlightcolor=PRIMARY_COLOR
    )
    email_entry.grid(row=1, column=0, pady=(0, 20))

    # ---------- OTP UI (Hidden Initially) ----------
    otp_label = tk.Label(card, text="Enter OTP", bg="white", font=FONT_LABEL)
    otp_entry = tk.Entry(
        card, font=FONT_ENTRY, width=30,
        relief="solid", borderwidth=1,
        highlightthickness=1,
        highlightbackground="#E8E8E8",
        highlightcolor=PRIMARY_COLOR
    )

    # ---------- VERIFY EMAIL ----------
    def verify_email():
        email = email_entry.get().strip()

        if not email:
            messagebox.showerror("Error", "Please enter your registered email")
            return

        user = get_user_by_email(email)
        if not user:
            messagebox.showerror("Invalid Email", "Email not found in system")
            return
        verified_email["value"]=email
        # Generate OTP
        otp = random.randint(100000, 999999)
        otp_generated["value"] = str(otp)

        try:
            send_otp_email(email, otp)
        except Exception as e:
            messagebox.showerror("Mail Error", str(e))
            return

        messagebox.showinfo(
            "OTP Sent",
            "An OTP has been sent to your email"
        )

        # Show OTP UI
        otp_label.grid(row=3, column=0, sticky="w", pady=(10, 8))
        otp_entry.grid(row=4, column=0, pady=(0, 20))

        verify_btn.config(text="Verify OTP", command=verify_otp)
        email_entry.config(state="disabled")

    # ---------- VERIFY OTP ----------
    def verify_otp():
        entered_otp = otp_entry.get().strip()

        if not entered_otp:
            messagebox.showerror("Error", "Please enter OTP")
            return

        if entered_otp != otp_generated["value"]:
            messagebox.showerror("Invalid OTP", "Incorrect OTP")
            return

        window.destroy()
        open_reset_password(verified_email)  

    # ---------- BUTTON ----------
    verify_btn = tk.Button(
        card,
        text="Verify Email",
        bg=ACCENT_COLOR,
        fg="white",
        activebackground="#2f855a",
        font=("Segoe UI", 11, "bold"),
        width=28,
        relief="flat",
        command=verify_email
    )
    verify_btn.grid(row=2, column=0, pady=(5, 10))

    # ---------- Footer ----------
    tk.Label(
        window,
        text="If issues persist, contact administrator",
        font=("Segoe UI", 9),
        fg="#6b7280",
        bg=BG_COLOR
    ).pack(pady=(10, 0))

    window.transient()
    window.grab_set()
