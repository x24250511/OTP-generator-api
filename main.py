from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr
import random
import time
import os
import smtplib
from email.mime.text import MIMEText

app = FastAPI("OTP authentication API")
otp_store = {}
OTP_EXPIRY_SECONDS = 300  # OTP validity duration

# Email configuration
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

if not EMAIL_ADDRESS or not EMAIL_PASSWORD:
    raise EnvironmentError("EMAIL credentials not configured.")


class OTPRequest(BaseModel):
    identifier: EmailStr  # email / phone number


class OTPVerifyRequest(BaseModel):
    identifier: EmailStr
    otp: str


def genrerate_otp(length=6):
    return "".join(str(random.randint(0, 9)) for _ in range(length))


@app.get("/")
def home():
    return {"message": "OTP API is running"}


def send_otp_email(to_email: str, otp: str):
    subject = "Your One Time Password (OTP) is:"
    body = f"Your OTP code is: {otp}. It is valid for {OTP_EXPIRY_SECONDS // 60} minutes."
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = to_email

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.send_message(msg)


@app.post("/generate-otp")
def generate_otp_api(request: OTPRequest):
    otp = genrerate_otp()
    expires_at = time.time() + OTP_EXPIRY_SECONDS
    otp_store[request.identifier] = {
        "otp": otp,
        "expires_at": expires_at
    }
    try:
        send_otp_email(request.identifier, otp)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail="Failed to send OTP email") from e
    return {
        "message": "OTP generated successfully",
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
