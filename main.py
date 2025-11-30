from fastapi import FastAPI, Request
from app.routes import login, data, profile, anomalies
from app.logger import log_request

app = FastAPI(title="Cloud Security Prototype")

# Include API routers
app.include_router(login.router, prefix="/login")
app.include_router(data.router, prefix="/data")
app.include_router(profile.router, prefix="/profile")
app.include_router(anomalies.router, prefix="/anomalies")

# Middleware for logging
@app.middleware("http")
async def log_middleware(request: Request, call_next):
    # Record time immediately before forwarding the request
    from datetime import datetime
    start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")

    # Call the actual route handler
    response = await call_next(request)

    # Manually pass the timestamp into the logger
    try:
        from app.logger import log_request
        await log_request(request, response.status_code, timestamp=start_time)
        print(f"[LOGGED] {start_time} | {request.url.path} | {response.status_code}")
    except Exception as e:
        print(f"[ERROR logging] {e}")

    return response


@app.get("/")
def root():
    return {"message": "Cloud Security Prototype API running"}
