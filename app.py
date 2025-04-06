# app.py (Cleaned FastAPI App Entry Point)

from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from agents.multi_agent_recommendation_system import (
    MemoryAgent,
    CustomerAgent,
    ProductAgent,
    RecommendationEngineAgent,
    FeedbackAgent
)

# Initialize FastAPI and templates directory
app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Initialize memory and all agents
memory = MemoryAgent()
customer_agent = CustomerAgent(memory)
product_agent = ProductAgent(memory)
recommender = RecommendationEngineAgent(memory, product_agent)
feedback_agent = FeedbackAgent(memory)

# Define feedback model
class Feedback(BaseModel):
    customer_id: int
    product_id: int
    clicked: int

# Homepage
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Recommendations view
@app.get("/recommendations/{customer_id}", response_class=HTMLResponse)
async def get_recommendations(customer_id: int, request: Request):
    customer = customer_agent.get_customer_profile(customer_id)

    if not customer:
        return templates.TemplateResponse("error.html", {
            "request": request,
            "message": "Customer not found. Please check the ID."
        })

    recommendations = recommender.recommend(customer_id)
    return templates.TemplateResponse("recommendations.html", {
        "request": request,
        "customer": customer,
        "recommendations": recommendations
    })

# Feedback endpoint
@app.post("/feedback")
async def submit_feedback(
    customer_id: int = Form(...),
    product_id: int = Form(...),
    clicked: int = Form(...)
):
    feedback_agent.record_feedback(customer_id, product_id, clicked)
    return {"status": "feedback recorded"}
