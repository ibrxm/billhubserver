import smtplib
import random

def send_otp_email(email):
    otp = str(random.randint(100000, 999999))
    sender_email = "billhubmitechnologies@gmail.com"
    sender_password = "xjex owmd uoph zrwr"
    subject = "Your BillHub OTP"
    message = f"This is your OTP: {otp}"

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(sender_email, sender_password)
    server.sendmail(sender_email, email, f"Subject: {subject}\n\n{message}")
    server.quit()

    return otp
