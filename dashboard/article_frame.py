import tkinter as tk
from tkinter import ttk, messagebox
from database.article_dao import (
    get_all_articles,
    insert_article,
    update_article,
    delete_article
)

class ArticleFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.configure(bg="#f4f4f4")

        self.selected_code = None  # 🔑 Track selected article

        title = tk.Label(
            self,
            text="Article Management",
            font=("Arial", 16, "bold"),
            bg="#f4f4f4"
        )
        title.pack(pady=10)

        # ---------- Table ----------
        columns = ("code", "length", "width", "status")
        self.tree = ttk.Treeview(self, columns=columns, show="headings")

        for col, text in zip(columns, ["Article Code", "Length", "Width", "Status"]):
            self.tree.heading(col, text=text)
            self.tree.column(col, width=120, anchor="center")

        self.tree.pack(fill="x", padx=20, pady=10)
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

        # ---------- Form ----------
        form = tk.Frame(self, bg="#f4f4f4")
        form.pack(pady=10)

        tk.Label(form, text="Code", bg="#f4f4f4").grid(row=0, column=0, padx=5)
        tk.Label(form, text="Length", bg="#f4f4f4").grid(row=0, column=2, padx=5)
        tk.Label(form, text="Width", bg="#f4f4f4").grid(row=0, column=4, padx=5)
        tk.Label(form, text="Status", bg="#f4f4f4").grid(row=0, column=6, padx=5)

        self.code_entry = tk.Entry(form, width=10)
        self.length_entry = tk.Entry(form, width=10)
        self.width_entry = tk.Entry(form, width=10)

        self.code_entry.grid(row=0, column=1, padx=5)
        self.length_entry.grid(row=0, column=3, padx=5)
        self.width_entry.grid(row=0, column=5, padx=5)

        self.status_var = tk.StringVar(value="ACTIVE")
        self.status_combo = ttk.Combobox(
            form,
            textvariable=self.status_var,
            values=["ACTIVE", "INACTIVE"],
            state="readonly",
            width=10
        )
        self.status_combo.grid(row=0, column=7, padx=5)

        # ---------- Buttons ----------
        btn_frame = tk.Frame(self, bg="#f4f4f4")
        btn_frame.pack(pady=10)

        self.add_btn = tk.Button(
            btn_frame, text="Add",
            bg="#4CAF50", fg="white",
            command=self.add_article
        )
        self.add_btn.pack(side="left", padx=5)

        self.update_btn = tk.Button(
            btn_frame, text="Update",
            bg="#2196F3", fg="white",
            command=self.update_article,
            state="disabled"
        )
        self.update_btn.pack(side="left", padx=5)

        self.delete_btn = tk.Button(
            btn_frame, text="Delete",
            bg="#f44336", fg="white",
            command=self.delete_article,
            state="disabled"
        )
        self.delete_btn.pack(side="left", padx=5)

        self.load_articles()

    # ---------- Load ----------
    def load_articles(self):
        self.tree.delete(*self.tree.get_children())
        for a in get_all_articles():
            self.tree.insert("", "end", values=(
                a["code"], a["length"], a["width"], a["status"]
            ))
        self.reset_form()

    # ---------- Select ----------
    def on_select(self, event):
        selected = self.tree.focus()
        if not selected:
            return

        code, length, width, status = self.tree.item(selected)["values"]
        self.selected_code = code

        self.code_entry.delete(0, tk.END)
        self.length_entry.delete(0, tk.END)
        self.width_entry.delete(0, tk.END)

        self.code_entry.insert(0, code)
        self.length_entry.insert(0, length)
        self.width_entry.insert(0, width)
        self.status_var.set(status)

        self.add_btn.config(state="disabled")
        self.update_btn.config(state="normal")
        self.delete_btn.config(state="normal")

    # ---------- Add ----------
    def add_article(self):
        code = self.code_entry.get().strip()
        length = self.length_entry.get().strip()
        width = self.width_entry.get().strip()
        status = self.status_var.get()

        if not code or not length or not width:
            messagebox.showerror("Error", "All fields are required")
            return

        try:
            insert_article(code, float(length), float(width), status)
            messagebox.showinfo("Success", "Article added")
            self.load_articles()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    # ---------- Update ----------
    def update_article(self):
        if not self.selected_code:
            return

        try:
            update_article(
                self.selected_code,
                self.code_entry.get().strip(),
                float(self.length_entry.get()),
                float(self.width_entry.get()),
                self.status_var.get()
            )
            messagebox.showinfo("Success", "Article updated")
            self.load_articles()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    # ---------- Delete ----------
    def delete_article(self):
        if not self.selected_code:
            return

        if not messagebox.askyesno(
            "Confirm", f"Delete article {self.selected_code}?"
        ):
            return

        try:
            delete_article(self.selected_code)
            messagebox.showinfo("Deleted", "Article removed")
            self.load_articles()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    # ---------- Reset ----------
    def reset_form(self):
        self.selected_code = None
        self.code_entry.delete(0, tk.END)
        self.length_entry.delete(0, tk.END)
        self.width_entry.delete(0, tk.END)
        self.status_var.set("ACTIVE")
        self.add_btn.config(state="normal")
        self.update_btn.config(state="disabled")
        self.delete_btn.config(state="disabled")

class UpdateArticleWindow(tk.Toplevel):
    def __init__(self, parent, old_code, length, width, status, refresh_callback):
        super().__init__(parent)
        self.title("Update Article")
        self.geometry("350x250")
        self.resizable(False, False)

        self.old_code = old_code
        self.refresh_callback = refresh_callback

        self.configure(bg="#f4f4f4")

        # Make window modal
        self.transient(parent)
        self.grab_set()

        tk.Label(self, text="Update Article",
                 font=("Arial", 14, "bold"),
                 bg="#f4f4f4").pack(pady=10)

        form = tk.Frame(self, bg="#f4f4f4")
        form.pack(pady=10)

        # -------- Fields --------
        tk.Label(form, text="Code", bg="#f4f4f4").grid(row=0, column=0, pady=5, sticky="e")
        tk.Label(form, text="Length", bg="#f4f4f4").grid(row=1, column=0, pady=5, sticky="e")
        tk.Label(form, text="Width", bg="#f4f4f4").grid(row=2, column=0, pady=5, sticky="e")
        tk.Label(form, text="Status", bg="#f4f4f4").grid(row=3, column=0, pady=5, sticky="e")

        self.code_entry = tk.Entry(form)
        self.length_entry = tk.Entry(form)
        self.width_entry = tk.Entry(form)

        self.code_entry.grid(row=0, column=1, padx=10)
        self.length_entry.grid(row=1, column=1, padx=10)
        self.width_entry.grid(row=2, column=1, padx=10)

        self.status_var = tk.StringVar(value=status)
        self.status_combo = ttk.Combobox(
            form,
            textvariable=self.status_var,
            values=["ACTIVE", "INACTIVE"],
            state="readonly"
        )
        self.status_combo.grid(row=3, column=1, padx=10)

        # -------- Pre-fill --------
        self.code_entry.insert(0, old_code)
        self.length_entry.insert(0, length)
        self.width_entry.insert(0, width)

        # -------- Buttons --------
        btn_frame = tk.Frame(self, bg="#f4f4f4")
        btn_frame.pack(pady=15)

        tk.Button(
            btn_frame, text="Save",
            bg="#2196F3", fg="white",
            width=10,
            command=self.save
        ).pack(side="left", padx=5)

        tk.Button(
            btn_frame, text="Cancel",
            width=10,
            command=self.destroy
        ).pack(side="left", padx=5)

    def save(self):
        try:
            from database.article_dao import update_article

            new_code = self.code_entry.get().strip()
            length = float(self.length_entry.get())
            width = float(self.width_entry.get())
            status = self.status_var.get()

            if not new_code:
                messagebox.showerror("Error", "Code is required", parent=self)
                return

            update_article(
                self.old_code,
                new_code,
                length,
                width,
                status
            )

            messagebox.showinfo("Success", "Article updated", parent=self)
            self.refresh_callback()
            self.destroy()

        except ValueError:
            messagebox.showerror(
                "Error",
                "Length and Width must be numeric",
                parent=self
            )
        except Exception as e:
            messagebox.showerror("Error", str(e), parent=self)
