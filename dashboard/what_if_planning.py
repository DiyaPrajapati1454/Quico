import os
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from google import genai
from google.genai import types

class WhatIfPlanningFrame(ttk.Frame):
    def __init__(self, parent, api_key=None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.configure(padding=15, style="Card.TFrame")

        # ----------------- API Setup -----------------
        self.api_key = "AIzaSyBQtXms_QgoFLsg8diBqVK9U2-zn6xH1J0" # Replace with your GEMINI API key or pass via parameter
        self.client = genai.Client(api_key=self.api_key)

        # ----------------- Base Machine Data -----------------
        self.base_machines = [
            {"name": "CM1", "type": "Cutting", "speed": 250},
            {"name": "FM-IV", "type": "Folding", "speed": 250},
            {"name": "FM-IX", "type": "Folding", "speed": 480},
            {"name": "CM2", "type": "Cutting", "speed": 340},
            {"name": "FM-X", "type": "Folding", "speed": 300},
            {"name": "PM1", "type": "Packing", "speed": 550},
        ]
        self.base_machine_str = "\n".join(
            [f"{m['name']} - {m['type']}, Speed: {m['speed']} units/hr" for m in self.base_machines]
        )

        # ----------------- Style -----------------
        style = ttk.Style()
        style.configure("Card.TFrame", background="#FDFEFE")
        style.configure("TLabel", background="#ECF0F1")
        style.configure("Header.TLabel", font=("Helvetica", 18, "bold"), foreground="#2C3E50", background="#ECF0F1")
        style.configure("TButton", font=("Helvetica", 13, "bold"))

        # ----------------- Title -----------------
        title_label = ttk.Label(self, text="🚀 What-If Planning", style="Header.TLabel")
        title_label.pack(pady=(0, 20))

        # ----------------- Input Frame -----------------
        input_frame = tk.Frame(self, bg="#D6DBDF", bd=2, relief=tk.GROOVE)
        input_frame.pack(fill="x", padx=10, pady=10)

        input_label = tk.Label(input_frame, text="Enter Your Scenario:", font=("Helvetica", 14, "bold"), bg="#D6DBDF")
        input_label.pack(anchor="w", padx=10, pady=(10, 5))

        self.scenario_input = scrolledtext.ScrolledText(
            input_frame, height=6, font=("Helvetica", 13), wrap=tk.WORD, bd=0, relief=tk.FLAT
        )
        self.scenario_input.pack(fill="x", padx=10, pady=(0, 10))

        # ----------------- Buttons -----------------
        btn_frame = tk.Frame(input_frame, bg="#D6DBDF")
        btn_frame.pack(pady=(0, 10))
        self.generate_button = tk.Button(
            btn_frame,
            text="Generate Analysis",
            command=self.generate_response,
            font=("Helvetica", 13, "bold"),
            bg="#3498DB",
            fg="white",
            activebackground="#2980B9",
            activeforeground="white",
            relief=tk.RAISED,
            bd=3,
            padx=15,
            pady=5
        )
        self.generate_button.pack(side="left", padx=5)

        self.clear_button = tk.Button(
            btn_frame,
            text="Clear Input",
            command=lambda: self.scenario_input.delete("1.0", tk.END),
            font=("Helvetica", 13, "bold"),
            bg="#E74C3C",
            fg="white",
            activebackground="#C0392B",
            activeforeground="white",
            relief=tk.RAISED,
            bd=3,
            padx=15,
            pady=5
        )
        self.clear_button.pack(side="left", padx=5)

        # ----------------- Output Frame -----------------
        output_frame = tk.Frame(self, bg="#FDFEFE", bd=2, relief=tk.RIDGE)
        output_frame.pack(fill="both", expand=True, padx=10, pady=10)

        output_label = tk.Label(output_frame, text="AI Response:", font=("Helvetica", 14, "bold"), bg="#FDFEFE")
        output_label.pack(anchor="w", padx=10, pady=(10, 5))

        self.response_output = scrolledtext.ScrolledText(
            output_frame, height=15, font=("Helvetica", 13), wrap=tk.WORD, bd=0, relief=tk.FLAT, bg="#F7F9F9"
        )
        self.response_output.pack(fill="both", expand=True, padx=10, pady=(0, 10))

    # ----------------- Generate AI Response -----------------
    def generate_response(self):
        user_scenario = self.scenario_input.get("1.0", tk.END).strip()
        if not user_scenario:
            messagebox.showwarning("Input Required", "Please enter a scenario to analyze.")
            return

        prompt_text = f"""
        Current machines in the plant:
        {self.base_machine_str}

        Scenario to analyze:
        {user_scenario}

        Based on the above, provide insights on how this change may affect operational utilization, 
        including cutting, folding, and packing operations in general.
        Do not consider specific orders, focus on overall utilization.
        """

        try:
            response = self.client.models.generate_content(
                model="gemini-2.5-flash-lite",
                contents=prompt_text,
                config={'temperature': 0.3}
            )
            self.response_output.delete("1.0", tk.END)
            self.response_output.insert(tk.END, response.text)
        except Exception as e:
            messagebox.showerror("Error", f"Error during AI request:\n{e}")