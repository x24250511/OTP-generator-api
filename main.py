from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr
import random
import time
import uuid
import os
import smtplib
from email.mime.text import MIMEText

app = FastAPI(title="OTP authentication API")
otp_store = {}
OTP_EXPIRY_SECONDS = 300  # OTP validity duration


class OTPGenerateRequest(BaseModel):
    user_id: str


class OTPVerifyRequest(BaseModel):
    user_id: str
    otp: str


def generate_otp(length: int = 6) -> str:
    return "".join(str(random.randint(0, 9)) for _ in range(length))


@app.post("/generate-otp")
def generate_otp_api(request: OTPGenerateRequest):
    otp = generate_otp()
    otp_id = str(uuid.uuid4())
    expires_at = time.time() + OTP_EXPIRY_SECONDS

    otp_store[request.user_id] = {
        "otp": otp,
        "expires_at": expires_at
    }
    return {
        "otp_id": otp,
        "expires_in_seconds": OTP_EXPIRY_SECONDS
    }


@app.post("/verify-otp")
def verify_otp_api(request: OTPVerifyRequest):
    record = otp_store.get(request.user_id)

    if not record:
        raise HTTPException(status_code=400, detail="OTP not found")

    if time.time() > record["expires_at"]:
        del otp_store[request.user_id]
        raise HTTPException(status_code=400, detail="OTP expired")

    if request.otp != record["otp"]:
        raise HTTPException(status_code=400, detail="Invalid OTP")

    del otp_store[request.user_id]

    return {"message": "OTP verified successfully"}
