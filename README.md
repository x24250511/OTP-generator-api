OTP Microservice (FastAPI)
This is a simple OTP (One-Time Password) API built using FastAPI.
Its only job is to:

Generate OTPs

Validate OTPs

Handle expiry

It does not send emails or SMS.

The application that uses this API is responsible for sending the OTP to users.
What This API Does
The API works with a generic key.
That key can be: Email,Phone number, Username, Any identifier

The API doesn’t care what it represents. It just associates an OTP with it.

How It Works:
The client sends a request to generate an OTP for a given key.
The API creates a 6-digit OTP.
The OTP is valid for 5 minutes.
The consuming application sends the OTP to the user (via email, SMS, etc.).
The user submits the OTP.
The client calls the verify endpoint.
The API checks:
Is the OTP correct?
Has it expired?
If valid, verification succeeds.

Running Locally
1. Create virtual environment
python -m venv venv
source venv/bin/activate

2. Install dependencies
pip install -r requirements.txt

3. Start the server
"uvicorn main:app --reload"

Server will run at:

http://127.0.0.1:8000

API Endpoints
Generate OTP

POST /generate-otp

Request body:
{
  "key": "user@example.com"
}

Response:
{
  "otp": "684606",
  "expires_in_seconds": 300
}

Verify OTP

POST /verify-otp

Request body:
{
  "key": "user@example.com",
  "otp": "684606"
}

Success response:
{
  "message": "OTP verified successfully"
}

Failure response:
{
  "detail": "Invalid or expired OTP"
}
Purpose

This project demonstrates separation of concerns:

OTP logic is isolated.

Delivery logic is handled elsewhere.

The service is reusable in different systems.