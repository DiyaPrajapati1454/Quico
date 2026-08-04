import tkinter as tk
from tkinter import messagebox, ttk
from database.machine_dao import get_all_machines, delete_machine, update_machine, insert_machine, insert_machine_setup_time
from datetime import datetime

class MachineFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.configure(bg="#f4f4f4")
        
        # ---------- Title ----------
        tk.Label(self, text="Machine Management",
                 font=("Arial", 16, "bold"),
                 bg="#f4f4f4").pack(pady=10)

        # ---------- Add Machine ----------
        add_frame = tk.LabelFrame(self, text="Add New Machine", padx=10, pady=10, bg="#f4f4f4")
        add_frame.pack(fill="x", padx=20, pady=10)

        tk.Label(add_frame, text="Name", bg="#f4f4f4").grid(row=0, column=0, padx=5)
        tk.Label(add_frame, text="Max Width", bg="#f4f4f4").grid(row=0, column=2, padx=5)
        tk.Label(add_frame, text="Speed", bg="#f4f4f4").grid(row=0, column=4, padx=5)
        tk.Label(add_frame, text="Operations", bg="#f4f4f4").grid(row=1, column=0, padx=5, pady=5)
        tk.Label(add_frame, text="Status", bg="#f4f4f4").grid(row=0, column=6, padx=5)

        self.name_entry = tk.Entry(add_frame, width=12)
        self.width_entry = tk.Entry(add_frame, width=10)
        self.speed_entry = tk.Entry(add_frame, width=10)
        self.status_var = tk.StringVar(value="ACTIVE")
        self.status_combo = ttk.Combobox(add_frame, textvariable=self.status_var,
                                         values=["ACTIVE", "INACTIVE"], state="readonly", width=10)

        self.cut_var = tk.IntVar()
        self.fold_var = tk.IntVar()
        self.pack_var = tk.IntVar()

        self.name_entry.grid(row=0, column=1, padx=5)
        self.width_entry.grid(row=0, column=3, padx=5)
        self.speed_entry.grid(row=0, column=5, padx=5)
        self.status_combo.grid(row=0, column=7, padx=5)

        ops_frame = tk.Frame(add_frame, bg="#f4f4f4")
        ops_frame.grid(row=1, column=1, columnspan=5, sticky="w")
        tk.Checkbutton(ops_frame, text="Cutting", variable=self.cut_var, bg="#f4f4f4").pack(side="left", padx=5)
        tk.Checkbutton(ops_frame, text="Folding", variable=self.fold_var, bg="#f4f4f4").pack(side="left", padx=5)
        tk.Checkbutton(ops_frame, text="Packing", variable=self.pack_var, bg="#f4f4f4").pack(side="left", padx=5)

        tk.Button(add_frame, text="Add Machine", bg="#4CAF50", fg="white", command=self.add_machine).grid(row=2, column=1, pady=10)

        # ---------- Machine List ----------
        self.list_frame = tk.Frame(self, bg="#f4f4f4")
        self.list_frame.pack(fill="both", padx=20, pady=10)
        self.refresh_machine_list()

    # ---------- Helpers ----------
    def get_operations(self):
        ops = []
        if self.cut_var.get(): ops.append("Cutting")
        if self.fold_var.get(): ops.append("Folding")
        if self.pack_var.get(): ops.append("Packing")
        return ",".join(ops)

    def reset_form(self):
        self.name_entry.delete(0, tk.END)
        self.width_entry.delete(0, tk.END)
        self.speed_entry.delete(0, tk.END)
        self.cut_var.set(0)
        self.fold_var.set(0)
        self.pack_var.set(0)
        self.status_var.set("ACTIVE")

    # ---------- Add Machine ----------
    def add_machine(self):
        name = self.name_entry.get().strip()
        width = self.width_entry.get().strip()
        speed = self.speed_entry.get().strip()
        ops = self.get_operations()
        status = self.status_var.get()

        if not name or not width or not speed or not ops:
            messagebox.showerror("Error", "All fields are required")
            return

        try:
            width = float(width)
            speed = float(speed)
        except ValueError:
            messagebox.showerror("Error", "Width and Speed must be numeric")
            return

        # Insert machine and get the new machine ID
        m_id = insert_machine(name, width, speed, ops, status)

        self.reset_form()
        self.refresh_machine_list()

        # Open setup time window after adding
        self.open_setup_time_window(m_id)

    # ---------- Update Machine ----------
    def open_update_window(self, machine):
        win = tk.Toplevel(self)
        win.title("Update Machine")
        win.geometry("450x350")
        win.resizable(False, False)
        win.transient(self)
        win.grab_set()  # modal

        tk.Label(win, text="Machine Name").grid(row=0, column=0, padx=10, pady=8, sticky="w")
        name_entry = tk.Entry(win, width=25)
        name_entry.grid(row=0, column=1)
        name_entry.insert(0, machine["m_name"])

        tk.Label(win, text="Max Width").grid(row=1, column=0, padx=10, pady=8, sticky="w")
        width_entry = tk.Entry(win, width=25)
        width_entry.grid(row=1, column=1)
        width_entry.insert(0, machine["max_width"])

        tk.Label(win, text="Speed").grid(row=2, column=0, padx=10, pady=8, sticky="w")
        speed_entry = tk.Entry(win, width=25)
        speed_entry.grid(row=2, column=1)
        speed_entry.insert(0, machine["speed"])

        tk.Label(win, text="Operations").grid(row=3, column=0, padx=10, pady=8, sticky="w")
        cut_var = tk.IntVar(value=1 if "Cutting" in machine["m_type"] else 0)
        fold_var = tk.IntVar(value=1 if "Folding" in machine["m_type"] else 0)
        pack_var = tk.IntVar(value=1 if "Packing" in machine["m_type"] else 0)
        ops_frame = tk.Frame(win)
        ops_frame.grid(row=3, column=1, sticky="w")
        tk.Checkbutton(ops_frame, text="Cutting", variable=cut_var).pack(side="left")
        tk.Checkbutton(ops_frame, text="Folding", variable=fold_var).pack(side="left")
        tk.Checkbutton(ops_frame, text="Packing", variable=pack_var).pack(side="left")

        tk.Label(win, text="Status").grid(row=4, column=0, padx=10, pady=8, sticky="w")
        status_var = tk.StringVar(value=machine["status"])
        ttk.Combobox(win, textvariable=status_var, values=["ACTIVE", "INACTIVE"], state="readonly", width=22).grid(row=4, column=1)

        def save_changes():
            ops = []
            if cut_var.get(): ops.append("Cutting")
            if fold_var.get(): ops.append("Folding")
            if pack_var.get(): ops.append("Packing")
            if not ops:
                messagebox.showerror("Error", "Select at least one operation")
                return

            try:
                update_machine(
                    machine["m_id"],
                    name_entry.get().strip(),
                    float(width_entry.get()),
                    float(speed_entry.get()),
                    ",".join(ops),
                    status_var.get()
                )
                messagebox.showinfo("Success", "Machine updated successfully")
                win.destroy()
                self.refresh_machine_list()
            except Exception as e:
                messagebox.showerror("Error", str(e))

        tk.Button(win, text="Save", bg="#4CAF50", fg="white", width=12, command=save_changes).grid(row=5, column=1, pady=15)

    # ---------- Setup Time Window ----------
    def open_setup_time_window(self, m_id):
        win = tk.Toplevel(self)
        win.title("Setup Time")
        win.geometry("350x200")
        win.transient(self)
        win.grab_set()

        tk.Label(win, text="Min Length").grid(row=0, column=0, padx=10, pady=8, sticky="w")
        tk.Label(win, text="Max Length").grid(row=1, column=0, padx=10, pady=8, sticky="w")
        tk.Label(win, text="Duration (HH:MM:SS)").grid(row=2, column=0, padx=10, pady=8, sticky="w")

        min_entry = tk.Entry(win, width=20)
        max_entry = tk.Entry(win, width=20)
        duration_entry = tk.Entry(win, width=20)
        min_entry.grid(row=0, column=1, padx=10, pady=5)
        max_entry.grid(row=1, column=1, padx=10, pady=5)
        duration_entry.grid(row=2, column=1, padx=10, pady=5)

        def save_setup():
            try:
                min_len_str = min_entry.get().strip()
                max_len_str = max_entry.get().strip()
                dur_str = duration_entry.get().strip()

                # Validate required fields
                if not min_len_str or not max_len_str or not dur_str:
                    raise ValueError("All fields are required")

                # Convert min & max length
                min_len = float(min_len_str)
                max_len = float(max_len_str)

                # Validate HH:MM:SS format
                parts = dur_str.split(":")
                if len(parts) != 3:
                    raise ValueError("Enter duration in HH:MM:SS format")

                h_str, m_str, s_str = parts

                if not (h_str.isdigit() and m_str.isdigit() and s_str.isdigit()):
                    raise ValueError("Hours, minutes and seconds must be numeric")

                h = int(h_str)
                m = int(m_str)
                s = int(s_str)

                if m >= 60 or s >= 60:
                    raise ValueError("Minutes and seconds must be less than 60")

                # Properly format to ensure leading zeros
                formatted_time = f"{h:02d}:{m:02d}:{s:02d}"

                # Insert directly as TIME (NO conversion to minutes)
                insert_machine_setup_time(
                    m_id,
                    min_len,
                    max_len,
                    formatted_time
                )

                messagebox.showinfo("Success", "Setup time saved successfully")
                win.destroy()

            except ValueError as e:
                messagebox.showerror("Error", str(e))
            except Exception as e:
                messagebox.showerror("Error", str(e))

        tk.Button(win, text="Save", bg="#4CAF50", fg="white", command=save_setup).grid(row=3, column=1, pady=15)

    # ---------- Delete Machine ----------
    def delete_machine(self, m_id):
        if messagebox.askyesno("Confirm", "Are you sure you want to delete this machine?"):
            delete_machine(m_id)
            self.refresh_machine_list()

    # ---------- Refresh List ----------
    def refresh_machine_list(self):
        for widget in self.list_frame.winfo_children():
            widget.destroy()

        # Header
        headers = ["Name", "Max Width", "Speed", "Operations", "Status", "Actions"]
        for col, h in enumerate(headers):
            tk.Label(self.list_frame, text=h, bg="#e0e0e0", width=15,
                     borderwidth=1, relief="solid").grid(row=0, column=col)

        machines = get_all_machines()
        for i, m in enumerate(machines):
            tk.Label(self.list_frame, text=m["m_name"], bg="#f4f4f4", width=15, borderwidth=1, relief="solid").grid(row=i+1, column=0)
            tk.Label(self.list_frame, text=m["max_width"], bg="#f4f4f4", width=15, borderwidth=1, relief="solid").grid(row=i+1, column=1)
            tk.Label(self.list_frame, text=m["speed"], bg="#f4f4f4", width=15, borderwidth=1, relief="solid").grid(row=i+1, column=2)
            tk.Label(self.list_frame, text=m["m_type"], bg="#f4f4f4", width=15, borderwidth=1, relief="solid").grid(row=i+1, column=3)
            tk.Label(self.list_frame, text=m["status"], bg="#f4f4f4", width=15, borderwidth=1, relief="solid").grid(row=i+1, column=4)

            action_frame = tk.Frame(self.list_frame, bg="#f4f4f4")
            action_frame.grid(row=i+1, column=5, sticky="new", padx=4, pady=2)

            update_btn = tk.Button(action_frame, text="Update", bg="#2196F3", fg="white",
                                   command=lambda machine=m: self.open_update_window(machine), width=6)
            delete_btn = tk.Button(action_frame, text="Delete", bg="#F44336", fg="white",
                                   command=lambda idx=m["m_id"]: self.delete_machine(idx), width=6)
            setup_btn = tk.Button(action_frame, text="Setup Time", bg="#FF9800", fg="white",
                                  command=lambda mid=m["m_id"]: self.open_setup_time_window(mid), width=10)

            update_btn.grid(row=0, column=0, padx=2, pady=2, sticky="ew")
            delete_btn.grid(row=0, column=1, padx=2, pady=2, sticky="ew")
            setup_btn.grid(row=0, column=2, padx=2, pady=2, sticky="ew")

            action_frame.columnconfigure(0, weight=1)
            action_frame.columnconfigure(1, weight=1)
            action_frame.columnconfigure(2, weight=1)
