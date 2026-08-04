import re

def validate_registration(username, email, password):
    # ---------- Empty Check ----------
    if not username or not email or not password:
        return False, "All fields are required"

    # ---------- Email Validation ----------
    email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    if not re.match(email_pattern, email):
        return False, "Invalid email format"

    # ---------- Password Validation ----------
    if len(password) < 8:
        return False, "Password must be at least 8 characters"

    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_special = any(
        c in "!@#$%^&*()-_=+[{]}\\|;:'\",<.>/?`~"
        for c in password
    )

    if not (has_upper and has_lower and has_digit):
        return False, (
            "Password must contain uppercase, lowercase, "
            "and a number"
        )

    strength = "Medium"
    if has_special:
        strength = "Strong"

    return True, strength
def validate_login(email, password):
    # ---------- Empty Check ----------
    if not email or not password:
        return False, "All fields are required"

    # ---------- Email Validation ----------
    email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    if not re.match(email_pattern, email):
        return False, "Invalid email format"

    return True, None
