def hours_to_hhmm(hours):
    total_minutes = round(hours * 60)
    hrs = total_minutes // 60
    mins = total_minutes % 60
    return f"{hrs:02d}:{mins:02d}"
