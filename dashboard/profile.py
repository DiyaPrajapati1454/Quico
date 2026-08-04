import tkinter as tk
from tkinter import messagebox
from database.user_dao import get_user_by_id, update_user_profile


class ProfileFrame(tk.Frame):
    def __init__(self, parent, user_id):
        super().__init__(parent, bg="#ecf0f1")
        self.user_id = user_id

        self.create_layout()
        self.load_profile()

    def create_layout(self):
        # ===== Title =====
        tk.Label(
            self,
            text="My Profile",
            font=("Segoe UI", 20, "bold"),
            bg="#ecf0f1",
            fg="#2c3e50"
        ).pack(pady=(30, 20))

        # ===== Card Container =====
        card = tk.Frame(
            self,
            bg="white",
            bd=0,
            highlightthickness=1,
            highlightbackground="#dcdcdc"
        )
        card.pack(pady=10, ipadx=40, ipady=30)

        # ===== Form =====
        form = tk.Frame(card, bg="white")
        form.pack()

        # Username
        tk.Label(
            form,
            text="Username",
            font=("Segoe UI", 10, "bold"),
            bg="white",
            fg="#34495e"
        ).grid(row=0, column=0, sticky="w", pady=(0, 5))

        self.username_entry = tk.Entry(
            form,
            width=35,
            font=("Segoe UI", 10),
            relief="solid",
            bd=1
        )
        self.username_entry.grid(row=1, column=0, pady=(0, 15))

        # Email
        tk.Label(
            form,
            text="Email",
            font=("Segoe UI", 10, "bold"),
            bg="white",
            fg="#34495e"
        ).grid(row=2, column=0, sticky="w", pady=(0, 5))

        self.email_entry = tk.Entry(
            form,
            width=35,
            font=("Segoe UI", 10),
            relief="solid",
            bd=1
        )
        self.email_entry.grid(row=3, column=0, pady=(0, 25))

        # ===== Update Button =====
        self.update_btn=tk.Button(
            card,
            text="Update Profile",
            command=self.update_profile,
            font=("Segoe UI", 11, "bold"),
            bg="#1abc9c",
            fg="white",
            activebackground="#16a085",
            relief="flat",
            width=20,
            cursor="hand2"
        )
        self.update_btn.pack()

    def load_profile(self):
        user = get_user_by_id(self.user_id)
        if user:
            self.username_entry.insert(0, user["uname"])
            self.email_entry.insert(0, user["email"])

    def update_profile(self):
        username = self.username_entry.get().strip()
        email = self.email_entry.get().strip()

        if not username or not email:
            messagebox.showerror("Error", "All fields are required")
            return

        update_user_profile(self.user_id, username, email)
        self.update_btn.config(text="Updated",state="disabled")
        messagebox.showinfo("Success", "Profile updated successfully")
        self.after(300,self.refresh_profile)

    def refresh_profile(self):
        self.username_entry.delete(0, tk.END)
        self.email_entry.delete(0, tk.END)
        self.load_profile()

        # Re-enable button
        self.update_btn.config(text="Update Profile", state="normal")
