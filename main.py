from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import random
import time

app = FastAPI()
otp_store = {}
OTP_EXPIRY_SECONDS = 300  # OTP validity duration


class OTPRequest(BaseModel):
    identifier: str  # email / phone number


class OTPVerifyRequest(BaseModel):
    identifier: str
    otp: str


def genrerate_otp(length=6):
    return "".join(str(random.randint(0, 9)) for _ in range(length))


@app.get("/")
def home():
    return {"message": "OTP API is running"}


@app.post("/generate-otp")
def generate_otp_api(request: OTPRequest):
    otp = genrerate_otp()
    expires_at = time.time() + OTP_EXPIRY_SECONDS
    otp_store[request.identifier] = {
        "otp": otp,
        "expires_at": expires_at
    }
    return {
        "message": "OTP generated successfully",
        "otp": otp,
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
