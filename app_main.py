import uvicorn
from fastapi import FastAPI
from api_router import router as topic_router

app = FastAPI(
    title="AI App Tutor Backend",
    description="API layer for extracting topics from course syllabi and generating questions.",
    version="1.0.0"
)

# Include API routes in the application
app.include_router(topic_router, prefix="/api/v1", tags=["Extraction"])

@app.get("/", tags=["Health"])
async def health_check():
    """
    Basic health check endpoint to verify the service status.
    """
    return {"status": "running", "service": "AI_APP_TUTOR"}

if __name__ == "__main__":
    # host="0.0.0.0" yapılması Docker erişimi için zorunludur
    uvicorn.run("app_main:app", host="0.0.0.0", port=8000, reload=True)