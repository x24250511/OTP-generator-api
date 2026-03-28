from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import random
import time
import os
import smtplib
from email.message import EmailMessage

SMTP_SERVER = "smtp.office365.com"
SMTP_PORT = 587
SMTP_USER = os.environ.get("SMTP_USER", "ad.sapphire@outlook.com")
SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD", "")

def send_email_otp(recipient_email: str, otp: str):
    if not SMTP_PASSWORD:
        print(f"DEV WARNING: SMTP_PASSWORD missing. OTP for {recipient_email} is {otp}")
        return
        
    msg = EmailMessage()
    msg.set_content(f"Your Sapphire Villas OTP verification code is: {otp}\n\nThis code will expire in 5 minutes.")
    msg['Subject'] = 'Sapphire Villas - Your Verification Code'
    msg['From'] = SMTP_USER
    msg['To'] = recipient_email

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.send_message(msg)
        print(f"OTP successfully sent to {recipient_email}")
    except Exception as e:
        print(f"Failed to send email to {recipient_email}: {e}")
app = FastAPI(title="Generic OTP Service")
@app.get("/")
def root():
    return {"status": "OTP API running"}
@app.head("/")
def head_root():
    return {"status": "ok"}
@app.get("/health")
def health():
    return {"status": "ok"}
@app.head("/health")
def head_health():
    return {"status": "ok"}
OTP_EXPIRY_SECONDS = 300        #OTP Expire in 5 min
otp_store = {}
class GenerateOTPRequest(BaseModel):
    key: str
class VerifyOTPRequest(BaseModel):
    key: str
    otp: str
def generate_otp():         #OTP Generation
    return str(random.randint(100000, 999999))
@app.post("/generate-otp")
def generate_otp_api(request: GenerateOTPRequest):
    otp = generate_otp()
    expires_at = time.time() + OTP_EXPIRY_SECONDS
    otp_store[request.key] = {
        "otp": otp,
        "expires_at": expires_at
    }
    
    if "@" in request.key:
        send_email_otp(request.key, otp)
    return {
        "otp": otp,
        "expires_in_seconds": OTP_EXPIRY_SECONDS
    }
@app.post("/verify-otp")
def verify_otp_api(request: VerifyOTPRequest):  #OTP Verfication
    record = otp_store.get(request.key)
    if not record:
        raise HTTPException(status_code=400, detail="OTP not found")
    if time.time() > record["expires_at"]:
        del otp_store[request.key]
        raise HTTPException(status_code=400, detail="OTP expired")
    if record["otp"] != request.otp:
        raise HTTPException(status_code=400, detail="Invalid OTP")
    del otp_store[request.key]
    return {"message": "OTP verified successfully"}
