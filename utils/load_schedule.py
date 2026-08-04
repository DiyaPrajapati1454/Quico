import json
from datetime import datetime

def load_schedule_from_json(filename):

    try:
        with open(filename, "r") as f:
            data = json.load(f)

        schedules = {}

        for machine_id, jobs in data.items():

            schedules[int(machine_id)] = []

            for job in jobs:

                schedules[int(machine_id)].append({
                    "order": job["order"],
                    "operation": job["operation"],
                    "machine_name": job["machine_name"],
                    "start": datetime.fromisoformat(job["start"]),
                    "end": datetime.fromisoformat(job["end"]),
                    "length": job.get("length", 0),
                    "setup_start": datetime.fromisoformat(job["setup_start"]) if job.get("setup_start") else None,
                    "setup_end": datetime.fromisoformat(job["setup_end"]) if job.get("setup_end") else None
                })

        return schedules

    except FileNotFoundError:
        return {}