from main import app as application

# AWS Elastic Beanstalk expects 'application' variable
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(application, host="0.0.0.0", port=8000)
