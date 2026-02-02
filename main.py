from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr
import random
import time
import os
import smtplib
from email.mime.text import MIMEText

app = FastAPI(title="OTP authentication API")
otp_store = {}
OTP_EXPIRY_SECONDS = 300  # OTP validity duration

# Email configuration
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587


class OTPRequest(BaseModel):
    identifier: EmailStr  # email / phone number


class OTPVerifyRequest(BaseModel):
    identifier: EmailStr
    otp: str


def generate_otp(length: int = 6) -> str:
    return "".join(str(random.randint(0, 9)) for _ in range(length))


def send_otp_email(to_email: str, otp: str):
    if not EMAIL_ADDRESS or not EMAIL_PASSWORD:
        raise EnvironmentError("EMAIL credentials not configured.")
    subject = "Your One-Time Password (OTP)"
    body = (
        f"Your OTP is: {otp}\n\n"
        f"This code is valid for 5 minutes.\n\n"
        f"If you did not request this, please ignore this email."
    )

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = to_email

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=10) as server:
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.send_message(msg)


@app.post("/generate-otp")
def generate_otp_api(request: OTPRequest):
    otp = generate_otp()
    expires_at = time.time() + OTP_EXPIRY_SECONDS
    otp_store[request.identifier] = {
        "otp": otp,
        "expires_at": expires_at
    }
    try:
        send_otp_email(request.identifier, otp)
    except Exception as e:
        print(f"Error sending email: {e}")
        raise HTTPException(
            status_code=502, detail="Failed to send OTP email")

    return {
        "message": "OTP sent to email",
        "expires_in_seconds": OTP_EXPIRY_SECONDS
    }


@app.post("/verify-otp")
def verify_otp_api(request: OTPVerifyRequest):
    record = otp_store.get(request.identifier)
    if not record:
        raise HTTPException(status_code=400, detail="OTP not found!!")
    if time.time() > record["expires_at"]:
        del otp_store[request.identifier]
        raise HTTPException(status_code=400, detail="OTP has expired!!")
    if request.otp != record["otp"]:
        raise HTTPException(status_code=400, detail="Invalid OTP!!")

    del otp_store[request.identifier]
    return {"message": "OTP verified successfully"}
