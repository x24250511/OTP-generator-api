from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import random
import time

app = FastAPI(title="Generic OTP Service")


@app.get("/")
def root():
    return {"status": "OTP Service is running"}


@app.get("/health")
def health():
    return {"status": "healthy"}


OTP_EXPIRY_SECONDS = 300
otp_store = {}


class GenerateOTPRequest(BaseModel):
    key: str


class VerifyOTPRequest(BaseModel):
    key: str
    otp: str


def generate_otp():
    return str(random.randint(100000, 999999))


@app.post("/generate-otp")
def generate_otp_api(request: GenerateOTPRequest):
    otp = generate_otp()
    expires_at = time.time() + OTP_EXPIRY_SECONDS

    otp_store[request.key] = {
        "otp": otp,
        "expires_at": expires_at
    }

    return {
        "otp": otp,
        "expires_in_seconds": OTP_EXPIRY_SECONDS
    }


@app.post("/verify-otp")
def verify_otp_api(request: VerifyOTPRequest):
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
