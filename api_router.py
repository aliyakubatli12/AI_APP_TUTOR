from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
from tools.topic_extractor import extract_topics

router = APIRouter()

# Data models for API documentation and validation
class TopicRequest(BaseModel):
    raw_text: str

class TopicResponse(BaseModel):
    specific_topics: List[str]
    general_topics: List[str]

@router.post("/extract-topics", response_model=TopicResponse)
async def api_extract_topics(request: TopicRequest):
    """
    Endpoint to receive raw text and return extracted CS topics.
    """
    try:
        # Call the existing extraction logic
        result = extract_topics(request.raw_text)
        return result
    except Exception as e:
        # Return 500 status code in case of server-side errors
        raise HTTPException(status_code=500, detail=str(e))