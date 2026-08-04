import smtplib
from email.message import EmailMessage

EMAIL_ADDRESS = "prajapatidiya547@gmail.com"
EMAIL_PASSWORD = "iarw lije ljul fzod"

def send_otp_email(to_email, otp):
    msg = EmailMessage()
    msg["Subject"] = "Quico Password Reset OTP"
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = to_email

    msg.set_content(f"""
Hello,

Your OTP for resetting Quico password is:

    {otp}

This OTP is valid for one session only.

Regards,
Quico Support Team
""")

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.send_message(msg)
