import tkinter as tk
import json
import copy
import os
from tkinter import ttk, messagebox
from datetime import datetime, timedelta

from database.order_dao import get_all_non_deliveredorders
from database.order_dao import update_order_status_and_delivery
from database.machine_dao import (
    get_all_cutting_machines,
    get_all_folding_machines,
    get_all_packing_machines,
    get_setup_times_by_machine
)

WORK_START = 6
WORK_END = 18


# ----------------- Helper Functions -----------------
# ----------------- JSON Persistence -----------------

def serialize_schedule(schedule):
    """
    Convert datetime objects to string for JSON storage
    """
    serializable = {}

    for machine_id, jobs in schedule.items():

        serializable[machine_id] = []

        for job in jobs:
            job_copy = job.copy()

            job_copy["start"] = job_copy["start"].isoformat()
            job_copy["end"] = job_copy["end"].isoformat()

            if job_copy["setup_start"]:
                job_copy["setup_start"] = job_copy["setup_start"].isoformat()

            if job_copy["setup_end"]:
                job_copy["setup_end"] = job_copy["setup_end"].isoformat()

            serializable[machine_id].append(job_copy)

    return serializable


def deserialize_schedule(schedule):
    """
    Convert string back to datetime
    """

    converted = {}

    for machine_id, jobs in schedule.items():

        machine_id = int(machine_id)
        converted[machine_id] = []

        for job in jobs:

            job_copy = job.copy()

            job_copy["start"] = datetime.fromisoformat(job_copy["start"])
            job_copy["end"] = datetime.fromisoformat(job_copy["end"])

            if job_copy["setup_start"]:
                job_copy["setup_start"] = datetime.fromisoformat(job_copy["setup_start"])

            if job_copy["setup_end"]:
                job_copy["setup_end"] = datetime.fromisoformat(job_copy["setup_end"])

            converted[machine_id].append(job_copy)

    return converted


def save_schedule_to_json(schedule, filename):

    serializable = serialize_schedule(schedule)

    if not serializable or serializable == {}:
        return

    with open(filename, "w") as f:
        json.dump(serializable, f, indent=4)

    with open("data/final_schedule.json","w") as f:
        json.dump(serializable,f,indent=4)

def load_schedule_from_json(filename):

    try:
        with open(filename, "r") as f:
            data = json.load(f)

        return deserialize_schedule(data)

    except:
        return {}

def get_setup_time_db(machine_id, prev_length, curr_length):

    # First job → no setup
    if prev_length is None:
        return 0

    diff = abs(curr_length - prev_length)

    rules = get_setup_times_by_machine(machine_id)

    for r in rules:
        min_diff = r["min_length_diff"]
        max_diff = r["max_length_diff"]

        if min_diff <= diff <= max_diff:

            duration = r["duration"]

            # Convert duration to seconds properly
            if isinstance(duration, str):
                h, m, s = map(int, duration.split(":"))
                seconds = h*3600 + m*60 + s

            elif isinstance(duration, timedelta):
                seconds = int(duration.total_seconds())

            else:
                seconds = int(duration)

            return seconds

    return 0

def calculate_production_seconds(quantity, speed):
    hours = quantity / speed
    return int(hours*3600)

def adjust_to_working_time(dt):
    while dt.weekday() >= 5:
        dt += timedelta(days=1)
        dt = dt.replace(hour=WORK_START, minute=0, second=0)

    if dt.hour < WORK_START:
        dt = dt.replace(hour=WORK_START, minute=0, second=0)

    if dt.hour >= WORK_END:
        dt += timedelta(days=1)
        dt = dt.replace(hour=WORK_START, minute=0, second=0)

    return dt


def add_working_seconds(start, seconds):

    if isinstance(seconds, timedelta):
        seconds=int(seconds.total_seconds)

    if not isinstance(seconds,int):
        seconds=int(seconds)

    
    current = adjust_to_working_time(start)
    remaining = seconds

    while remaining > 0:

        end_of_day = current.replace(hour=WORK_END, minute=0, second=0)
        available = (end_of_day - current).total_seconds()

        if remaining <= available:
            return current + timedelta(seconds=remaining)
        else:
            remaining -= available
            current += timedelta(days=1)
            current = current.replace(hour=WORK_START, minute=0, second=0)
            current = adjust_to_working_time(current)

    return current

# ----------------- Get Machine by Name -----------------
def get_machine_by_name(operation, machine_name):
    if operation == "Cutting":
        machines = get_all_cutting_machines()
    elif operation == "Folding":
        machines = get_all_folding_machines()
    else:
        machines = get_all_packing_machines()
    
    for m in machines:
        if m["m_name"] == machine_name:
            return m
    return None
    
# ----------------- Dashboard -----------------

class SchedulingDashboard(tk.Frame):

    def update_all_orders_delivery(self):

        order_ids = set()

        for machine_jobs in self.schedules.values():
            for job in machine_jobs:
                order_ids.add(job["order"])

        for order_id in order_ids:
            self.update_order_delivery(order_id)

    def update_order_delivery(self, order_id):

        packing_jobs = []

        # Find all packing operations for this order
        for machine_jobs in self.schedules.values():
            for job in machine_jobs:
                if job["order"] == order_id and job["operation"] == "Packing":
                    packing_jobs.append(job)

        if packing_jobs:
            # Get latest packing end time
            last_packing = max(packing_jobs, key=lambda x: x["end"])

            delivery_date = last_packing["end"] + timedelta(days=1)

            status = "Delivered"   

        else:
            delivery_date = None
            status = "Not Delivered"

        # Update DB
        update_order_status_and_delivery(order_id, status, delivery_date)
    
    # --------- To allow user to edit time-------------------
    def edit_schedule_popup(self):

        selected = self.tree.selection()
        if not selected:
            messagebox.showerror("Error", "Select a row to edit")
            return

        item = self.tree.item(selected[0])
        values = item["values"]

        order_id = values[0]
        operation = values[1]
        machine_name = values[2]

        # Find job
        job_to_edit = None
        machine_id_found = None

        for machine_id, jobs in self.schedules.items():
            for job in jobs:
                if job["order"] == order_id and job["operation"] == operation:
                    job_to_edit = job
                    machine_id_found = machine_id
                    break

        if not job_to_edit:
            return

        popup = tk.Toplevel(self)
        popup.title("Edit Schedule Time")
        popup.geometry("300x200")

        tk.Label(popup, text="Start Time (YYYY-MM-DD HH:MM)").pack(pady=10)

        start_entry = tk.Entry(popup)
        start_entry.insert(0, job_to_edit["start"].strftime("%Y-%m-%d %H:%M"))
        start_entry.pack(pady=5)

        def save_changes():
            try:
                new_start = datetime.strptime(start_entry.get(), "%Y-%m-%d %H:%M")

                if new_start.weekday() >= 5:
                    messagebox.showerror("Error", "Weekend not allowed")
                    return

                if new_start.hour < WORK_START or new_start.hour >= WORK_END:
                    messagebox.showerror("Error", "Time must be between 6 AM to 6 PM")
                    return

                new_start = adjust_to_working_time(new_start)

                machine = get_machine_by_name(operation, machine_name)

                jobs = self.schedules.get(machine_id_found, [])
                prev_length = jobs[-1]["length"] if jobs else None

                setup_time = get_setup_time_db(
                    machine_id_found,
                    prev_length,
                    job_to_edit["length"]
                )

                setup_start = new_start
                production_start = add_working_seconds(setup_start, setup_time)

                order_data = None
                for o in self.orders:
                    if str(o["order_id"]) == str(order_id):
                        order_data = o
                        break

                if not order_data:
                    messagebox.showerror("Error", "Order data not found")
                    return


                duration = calculate_production_seconds(
                    order_data["no_of_quibi"],
                    machine["speed"]
                )

                new_end = add_working_seconds(production_start, duration)

                job_to_edit["start"] = new_start
                job_to_edit["end"] = new_end
                job_to_edit["setup_start"] = setup_start if setup_time > 0 else None
                job_to_edit["setup_end"] = production_start if setup_time > 0 else None

                # Propagate changes
                self.reschedule_next_operations(order_id, operation)
                self.shift_machine_schedule(machine_id_found)
                self.update_order_delivery(order_id)
                self.refresh_table()
                popup.destroy()

            except Exception as e:
                messagebox.showerror("Error", str(e))

        tk.Button(popup, text="Save", bg="#16a34a", fg="white", command=save_changes).pack(pady=15)    # ----------------To Remove the old schedule if replan is done-------------
    
    def delete_selected_task(self):

        selected = self.tree.selection()

        if not selected:
            messagebox.showerror("Error", "Select a row to delete")
            return

        item = self.tree.item(selected[0])
        values = item["values"]

        order_id = values[0]
        operation = values[1]

        confirm = messagebox.askyesno(
            "Confirm Delete",
            f"Delete {operation} and dependent operations for Order {order_id}?"
        )

        if not confirm:
            return

        operation_sequence = ["Cutting", "Folding", "Packing"]
        index = operation_sequence.index(operation)

        operations_to_delete = operation_sequence[index:]

        for machine_id in list(self.schedules.keys()):

            updated_jobs = []

            for job in self.schedules[machine_id]:

                if job["order"] == order_id and job["operation"] in operations_to_delete:
                    continue
                else:
                    updated_jobs.append(job)

            if updated_jobs:
                self.schedules[machine_id] = updated_jobs
            else:
                del self.schedules[machine_id]

        self.refresh_table()
        self.update_order_delivery(order_id)
        messagebox.showinfo("Deleted", "Task(s) deleted successfully")
    
    def remove_existing_schedule(self, order_id, operation):

        removed_end_time = None

        for machine_id in list(self.schedules.keys()):
            jobs = self.schedules[machine_id]

            new_jobs = []
            for job in jobs:
                if job["order"] == order_id and job["operation"] == operation:
                    removed_end_time = job["end"]
                else:
                    new_jobs.append(job)

            self.schedules[machine_id] = new_jobs

            if not new_jobs:
                del self.schedules[machine_id]

    def __init__(self, parent, schedules=None):
        super().__init__(parent)
        self.configure(bg="#f4f4f4")
        self.operation_sequence = ["Cutting", "Folding", "Packing"]
        self.orders = get_all_non_deliveredorders()
        # Use existing schedules if passed, else create a new one
        self.schedules = schedules if schedules is not None else {}

        #snapshots for reports
        self.auto_schedule_snapshot = None
        self.manual_schedule_snapshot = None

        self.order_last_end = {}
        self.order_last_end = {}   # order_id -> last end time
        self.create_ui()

    # ----------------- UI -----------------

    def create_ui(self):

        # ====== MAIN CONTAINER ======
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=0)   # left panel fixed
        self.grid_columnconfigure(1, weight=1)   # right panel expandable

        # ================= LEFT PANEL =================
        left_panel = tk.Frame(self, bg="white", bd=1, relief="solid", width=350)
        left_panel.grid_propagate(False)
        left_panel.grid(row=0, column=0, sticky="ns", padx=10, pady=10)

        left_panel.grid_rowconfigure(1, weight=1)

        tk.Label(
            left_panel,
            text="Orders",
            font=("Segoe UI", 14, "bold"),
            bg="white"
        ).grid(row=0, column=0, pady=10)

        # ---- Orders Table (Better than Listbox) ----
        self.order_tree = ttk.Treeview(
            left_panel,
            columns=("Order ID", "Length", "Width", "Qty"),
            show="headings",
            height=15
        )

        self.order_tree.heading("Order ID", text="Order ID")
        self.order_tree.heading("Length", text="Length")
        self.order_tree.heading("Width", text="Width")
        self.order_tree.heading("Qty", text="Quantity")

        self.order_tree.column("Order ID", width=80, anchor="center")
        self.order_tree.column("Length", width=70, anchor="center")
        self.order_tree.column("Width", width=70, anchor="center")
        self.order_tree.column("Qty", width=90, anchor="center")

        self.order_tree.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")

        scrollbar = ttk.Scrollbar(left_panel, orient="vertical", command=self.order_tree.yview)
        scrollbar.grid(row=1, column=1, sticky="ns")
        self.order_tree.configure(yscrollcommand=scrollbar.set)

        for o in self.orders:
            self.order_tree.insert("", tk.END, values=(
                o["order_id"],
                o["length"],
                o["width"],
                o["no_of_quibi"]
            ))

        self.order_tree.bind("<<TreeviewSelect>>", self.on_order_select_from_tree)

        # ================= RIGHT PANEL =================
        right_panel = tk.Frame(self, bg="#f9fafb")
        right_panel.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        right_panel.grid_rowconfigure(2, weight=1)
        right_panel.grid_columnconfigure(0, weight=1)

        # ---- Header ----
        tk.Label(
            right_panel,
            text="Production Scheduling Dashboard",
            font=("Segoe UI", 18, "bold"),
            bg="#f9fafb"
        ).grid(row=0, column=0, sticky="w", pady=10)

        # ================= CONTROL BAR =================
        control_frame = tk.Frame(right_panel, bg="white", bd=1, relief="solid")
        control_frame.grid(row=1, column=0, sticky="ew", pady=10)
        for i in range(5):
            control_frame.grid_columnconfigure(i, weight=1)
        
        # Operation
        tk.Label(control_frame, text="Operation", bg="white").grid(row=0, column=0, pady=(10,0))
        self.operation_var = tk.StringVar()
        self.operation_combo = ttk.Combobox(
            control_frame,
            textvariable=self.operation_var,
            state="readonly",
            values=["Cutting", "Folding", "Packing"]
        )
        self.operation_combo.grid(row=1, column=0, padx=5, pady = 5, sticky="ew")
        self.operation_combo.bind("<<ComboboxSelected>>", self.load_machines)

        # Machine
        tk.Label(control_frame, text="Machine", bg="white").grid(row=0, column=1, pady=(10,0))
        self.machine_var = tk.StringVar()
        self.machine_combo = ttk.Combobox(
            control_frame,
            textvariable=self.machine_var,
            state="readonly"
        )
        self.machine_combo.grid(row=1, column=1, padx=5,pady=5, sticky="ew")

        # Schedule Button
        tk.Button(
            control_frame,
            text="Schedule",
            bg="#16a34a",
            fg="white",
            font=("Segoe UI", 10, "bold"),
            command=self.schedule_operation
        ).grid(row=1, column=2, padx=5, pady = 5,sticky="ew")
        #Button to add manual schedule
        tk.Button(
            control_frame,
            text="Save Manual Schedule",
            bg="#9333ea",
            fg="white",
            font=("Segoe UI", 10, "bold"),
            command=self.save_manual_schedule
        ).grid(row=2, column=2, columnspan=2, padx=5, pady=5, sticky="ew")
        # Auto Schedule
        tk.Button(
            control_frame,
            text="Auto Schedule",
            bg="#2563eb",
            fg="white",
            font=("Segoe UI", 10, "bold"),
            command=self.auto_schedule
        ).grid(row=1, column=3, padx=5, pady =5,sticky="ew")
        #Adding seperator
        separator = ttk.Separator(control_frame, orient="horizontal")
        separator.grid(row=3, column=0, columnspan=5, sticky="ew", pady=8)

        # Strategy
        tk.Label(
            control_frame,
            text="Strategy: Earliest Completion Time",
            bg="white",
            fg="gray"
        ).grid(row=3, column=0, columnspan=4, pady=(5,10))

        # ================= SCHEDULE TABLE =================
        table_frame = tk.Frame(right_panel, bg="white", bd=1, relief="solid")
        table_frame.grid(row=2, column=0, sticky="nsew")

        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)

        self.tree = ttk.Treeview(
            table_frame,
            columns=("Order", "Operation", "Machine", "Start", "End"),
            show="headings"
        )
        def enable_buttons(event):
            self.edit_btn.config(state="normal")
            self.delete_btn.config(state="normal")

        self.tree.bind("<<TreeviewSelect>>", enable_buttons)
        self.tree.heading("Order", text="Order")
        self.tree.heading("Operation", text="Operation")
        self.tree.heading("Machine", text="Machine")
        self.tree.heading("Start", text="Start Time")
        self.tree.heading("End", text="End Time")

        self.tree.column("Order", width=100, anchor="center")
        self.tree.column("Operation", width=120, anchor="center")
        self.tree.column("Machine", width=120, anchor="center")
        self.tree.column("Start", width=180, anchor="center")
        self.tree.column("End", width=180, anchor="center")

        self.tree.grid(row=0, column=0, sticky="nsew")

        scroll_y = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        scroll_y.grid(row=0, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=scroll_y.set)

        bottom_panel = tk.Frame(right_panel, bg="#f9fafb")
        bottom_panel.grid(row=3, column=0, sticky="ew", pady=10)

        bottom_panel.grid_columnconfigure(0, weight=1)

        # ===== ACTION BUTTONS =====
        action_frame = tk.Frame(bottom_panel, bg="#f9fafb")
        action_frame.pack(fill="x")

        self.edit_btn = tk.Button(
            action_frame,
            text="Edit",
            bg="#f59e0b",
            fg="white",
            font=("Segoe UI", 10, "bold"),
            command=self.edit_schedule_popup,
            state="disabled"
        )
        self.edit_btn.pack(side="left", padx=10)

        self.delete_btn = tk.Button(
            action_frame,
            text="Delete",
            bg="#dc2626",
            fg="white",
            font=("Segoe UI", 10, "bold"),
            command=self.delete_selected_task,
            state="disabled"
        )
        self.delete_btn.pack(side="left", padx=10)

    #------------------ Validate Sequence-------------------

    def validate_operation_sequence(self, order_id, current_operation):

        # If it's the first operation (Cutting), always allow
        if current_operation == "Cutting":
            return True

        # Find index of current operation
        current_index = self.operation_sequence.index(current_operation)

        # Previous required operation
        required_previous = self.operation_sequence[current_index - 1]

        # Check if required previous operation is already scheduled
        for jobs in self.schedules.values():
            for job in jobs:
                if job["order"] == order_id and job["operation"] == required_previous:
                    return True

        return False
    
    #-----------Get previous task end time-------------------------
    def get_previous_operation_end(self, order_id, current_operation):

        operation_sequence = ["Cutting", "Folding", "Packing"]
        current_index = operation_sequence.index(current_operation)

        # Cutting has no dependency
        if current_index == 0:
            return None

        required_previous = operation_sequence[current_index - 1]

        for jobs in self.schedules.values():
            for job in jobs:
                if job["order"] == order_id and job["operation"] == required_previous:
                    return job["end"]

        return None
    
    #------------------ Reshedule next operation--------------------

    def reschedule_next_operations(self, order_id, current_operation):
        
        #  GET ORDER DATA (IMPORTANT FIX)
        order_data = None
        for o in self.orders:
            if str(o["order_id"]) == str(order_id):
                order_data = o
                break

        if not order_data:
            return
        
        operation_sequence = ["Cutting", "Folding", "Packing"]
        current_index = operation_sequence.index(current_operation)

        if current_index == len(operation_sequence) - 1:
            return  # last operation

        next_operation = operation_sequence[current_index + 1]

        # Find the job for next operation
        for machine_id, jobs in self.schedules.items():
            for job in jobs:
                if job["order"] == order_id and job["operation"] == next_operation:

                    # Keep the same machine
                    
                    machine = get_machine_by_name(next_operation, job["machine_name"])
                    if machine is None:
                        continue  # Skip if machine not found (safety check)
                    machine_id = machine["m_id"]

                    # Remove existing job from schedule
                    self.remove_existing_schedule(order_id, next_operation)

                    # Recalculate start/end times based on previous operation
                    previous_end = self.get_previous_operation_end(order_id, next_operation)
                    machine_last = self.get_machine_last_end(machine["m_id"])
                    start_time = max(machine_last, previous_end) if previous_end else machine_last
                    start_time = adjust_to_working_time(start_time)

                    # Setup time
                    jobs_on_machine = self.schedules.get(machine["m_id"], [])
                    prev_length = jobs_on_machine[-1]["length"] if jobs_on_machine else None
                    setup_time = get_setup_time_db(machine["m_id"], prev_length, order_data["length"])

                    setup_start = start_time
                    production_start = add_working_seconds(setup_start, setup_time)

                    # Production duration
                    duration = calculate_production_seconds(order_data["no_of_quibi"], machine["speed"])
                    end_time = add_working_seconds(production_start, duration)

                    # Save back in schedule
                    self.schedules.setdefault(machine["m_id"], []).append({
                        "order": order_id,
                        "operation": next_operation,
                        "machine_name": machine["m_name"],
                        "start": start_time,
                        "end": end_time,
                        "length": order_data["length"],
                        "setup_start": setup_start if setup_time > 0 else None,
                        "setup_end": production_start if setup_time > 0 else None
                    })

                    # Forward propagate
                    self.reschedule_next_operations(order_id, next_operation)
                    return
 
    def shift_machine_schedule(self, machine_id):

        jobs = self.schedules.get(machine_id, [])

        if not jobs:
            return

        # Sort jobs by start time
        jobs.sort(key=lambda x: x["start"])

        for i in range(1, len(jobs)):

            prev_job = jobs[i - 1]
            current_job = jobs[i]

            # If overlap happens → shift
            if current_job["start"] < prev_job["end"]:

                new_start = adjust_to_working_time(prev_job["end"])

                # Setup time
                prev_length = prev_job["length"]
                curr_length = current_job["length"]

                setup_time = get_setup_time_db(
                    machine_id,
                    prev_length,
                    curr_length
                )

                setup_start = new_start
                production_start = add_working_seconds(setup_start, setup_time)

                # Find order data
                order_data = None
                for o in self.orders:
                    if str(o["order_id"]) == str(current_job["order"]):
                        order_data = o
                        break

                if not order_data:
                    continue

                # Machine speed
                machine = get_machine_by_name(
                    current_job["operation"],
                    current_job["machine_name"]
                )

                duration = calculate_production_seconds(
                    order_data["no_of_quibi"],
                    machine["speed"]
                )

                new_end = add_working_seconds(production_start, duration)

                # Update job
                current_job["start"] = new_start
                current_job["end"] = new_end
                current_job["setup_start"] = setup_start if setup_time > 0 else None
                current_job["setup_end"] = production_start if setup_time > 0 else None

                # ALSO propagate for that job’s next operations
                self.reschedule_next_operations(
                    current_job["order"],
                    current_job["operation"]
                )
    
    # ----------------- Order Selection -----------------

    def on_order_select_from_tree(self, event):
        selected = self.order_tree.selection()
        if not selected:
            return

        values = self.order_tree.item(selected[0], "values")
        order_id = values[0]

        for o in self.orders:
            if str(o["order_id"]) == str(order_id):
                self.selected_order = o
                break

        # Refresh machine list if operation already selected
        if self.operation_var.get():
            self.load_machines(None)
 
    # ----------------- Load Machines -----------------

    def load_machines(self, event):

        if not hasattr(self, "selected_order"):
            messagebox.showerror("Error", "Select Order First")
            return

        operation = self.operation_var.get()
        width = self.selected_order["width"]

        if operation == "Cutting":
            machines = get_all_cutting_machines()
        elif operation == "Folding":
            machines = get_all_folding_machines()
        else:
            machines = get_all_packing_machines()

        self.compatible_machines = [
            m for m in machines if width <= m["max_width"]
        ]

        machine_display_list = []

        for m in self.compatible_machines:
            machine_display_list.append(
                f"{m['m_name']}"
            )

        self.machine_combo["values"] = machine_display_list
        self.machine_combo.set("")

    # ----------------- Schedule -----------------

    def schedule_operation(self):

        if not hasattr(self, "selected_order"):
            messagebox.showerror("Error", "Select Order")
            return

        if not self.operation_var.get():
            messagebox.showerror("Error", "Select Operation")
            return

        if not self.machine_combo.get():
            messagebox.showerror("Error", "Select Machine")
            return

        order = self.selected_order
        operation = self.operation_var.get()
        machine_index = self.machine_combo.current()
        machine = self.compatible_machines[machine_index]

        order_id = order["order_id"]
        machine_id = machine["m_id"]
        machine_name = machine["m_name"]

        # ----------------- OPERATION SEQUENCE VALIDATION -----------------
        if not self.validate_operation_sequence(order_id, operation):
            messagebox.showerror(
                "Sequence Error",
                f"{operation} cannot be scheduled before its previous operation."
            )
            return

        self.remove_existing_schedule(order_id,operation)
        # -------------------------------------------------
        # Get Previous Job Length on This Machine
        # -------------------------------------------------
        jobs = self.schedules.get(machine_id, [])
        prev_length = None

        if jobs:
            prev_length = jobs[-1]["length"]   # last scheduled job length

        # -------------------------------------------------
        # Get Setup Time From DB
        # -------------------------------------------------
        setup_time = get_setup_time_db( machine_id, prev_length, order["length"] )

        # -------------------------------------------------
        # Start Time Logic (Machine + Order)
        # -------------------------------------------------
        machine_last = self.get_machine_last_end(machine_id)
        previous_op_end = self.get_previous_operation_end(order_id, operation)

        if previous_op_end:
            start_time = max(machine_last, previous_op_end)
        else:
            start_time = machine_last
        
        #  Add setup time BEFORE production
        start_time = adjust_to_working_time(start_time)

        # ----------------- Apply Setup -----------------
        if setup_time > 0:
            setup_start = start_time
            production_start = add_working_seconds(setup_start, setup_time)
        else:
            production_start = start_time

        # # Apply setup time using working-hours logic
        # start_time = add_working_seconds(start_time, setup_time)
        
        # -------------------------------------------------
        # Production Duration
        # -------------------------------------------------
        duration = calculate_production_seconds(
            order["no_of_quibi"],
            machine["speed"]
        )

        end_time = add_working_seconds(production_start, duration)

        # -------------------------------------------------
        # Save in Memory (IMPORTANT: store length!)
        # -------------------------------------------------
        self.schedules.setdefault(machine_id, []).append({
            "order": order_id,
            "operation": operation,
            "machine_name":machine_name,
            "start": start_time,
            "end": end_time,
            "length": order["length"],   #  needed for next setup calculation
            "setup_start": setup_start if setup_time > 0 else None,
            "setup_end": production_start if setup_time > 0 else None
            
        })

        self.order_last_end[order_id] = end_time

        # Forward propagate changes
        self.reschedule_next_operations(order_id, operation)

        self.refresh_table()
        self.update_order_delivery(order_id)
        messagebox.showinfo("Success", "Operation Scheduled Successfully")

    # ----------------- Machine Last End -----------------

    def get_machine_last_end(self, machine_id):
        jobs = self.schedules.get(machine_id, [])
        if not jobs:
            return datetime.now()
        return max(j["end"] for j in jobs)

    # ----------------- Refresh Table -----------------

    def refresh_table(self):

        for row in self.tree.get_children():
            self.tree.delete(row)

        # Define correct operation sequence
        operation_order = {
            "Cutting": 1,
            "Folding": 2,
            "Packing": 3
        }

        # Flatten all jobs into one list
        all_jobs = []
        for jobs in self.schedules.values():
            all_jobs.extend(jobs)

        # Sort by order first, then operation sequence
        all_jobs.sort(key=lambda x: (
            x["order"],
            operation_order.get(x["operation"], 99)
        ))

        # Insert sorted jobs
        for job in all_jobs:
            self.tree.insert("", tk.END, values=(
                job["order"],
                job["operation"],
                job["machine_name"],
                job["start"].strftime("%Y-%m-%d %H:%M"),
                job["end"].strftime("%Y-%m-%d %H:%M")
            ))
            
    def save_manual_schedule(self):

        if not self.schedules:
            messagebox.showerror("Error", "No schedule available")
            return

        self.manual_schedule_snapshot = copy.deepcopy(self.schedules)
        save_schedule_to_json(self.manual_schedule_snapshot, "data/manual_schedule.json")
        messagebox.showinfo(
            "Saved",
            "Manual schedule saved for comparison reports"
        )
    
    def auto_schedule(self):

        self.schedules = {}
        self.order_last_end = {}

        operations = ["Cutting", "Folding", "Packing"]

        for order in self.orders:

            order_id = order["order_id"]
            previous_end = None

            for operation in operations:

                # 1️ Get machines
                if operation == "Cutting":
                    machines = get_all_cutting_machines()
                elif operation == "Folding":
                    machines = get_all_folding_machines()
                else:
                    machines = get_all_packing_machines()

                # Filter width compatibility
                machines = [m for m in machines if order["width"] <= m["max_width"]]

                best_machine = None
                best_end_time = None
                best_start = None
                best_setup_start = None
                best_prod_start = None

                # 2️ Check each machine
                for machine in machines:

                    machine_id = machine["m_id"]

                    machine_last = self.get_machine_last_end(machine_id)

                    if previous_end:
                        start_time = max(machine_last, previous_end)
                    else:
                        start_time = machine_last

                    start_time = adjust_to_working_time(start_time)

                    # Setup logic
                    jobs = self.schedules.get(machine_id, [])
                    prev_length = jobs[-1]["length"] if jobs else None

                    setup_time = get_setup_time_db(
                        machine_id,
                        prev_length,
                        order["length"]
                    )

                    setup_start = start_time
                    production_start = add_working_seconds(setup_start, setup_time)

                    # Production duration
                    duration = calculate_production_seconds(
                        order["no_of_quibi"],
                        machine["speed"]
                    )

                    end_time = add_working_seconds(production_start, duration)

                    # Choose machine with earliest finish
                    if best_end_time is None or end_time < best_end_time:
                        best_machine = machine
                        best_end_time = end_time
                        best_start = start_time
                        best_setup_start = setup_start
                        best_prod_start = production_start

                # 3️ Assign best machine
                machine_id = best_machine["m_id"]
                machine_name = best_machine["m_name"]
                
                self.schedules.setdefault(machine_id, []).append({
                    "order": order_id,
                    "operation": operation,
                    "machine_name":machine_name,
                    "start": best_start,
                    "end": best_end_time,
                    "length": order["length"],
                    "setup_start": best_setup_start,
                    "setup_end": best_prod_start
                })

                previous_end = best_end_time
                self.order_last_end[order_id] = best_end_time

        self.auto_schedule_snapshot = copy.deepcopy(self.schedules)
        save_schedule_to_json(self.auto_schedule_snapshot, "data/auto_schedule.json")
        self.refresh_table()
        self.update_all_orders_delivery()
        messagebox.showinfo("Auto Schedule", "Auto Scheduling Completed")

