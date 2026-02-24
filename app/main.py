from fastapi import FastAPI
from app.api.routes import router as api_router

app = FastAPI(title="ESG Portfolio Engine")

# Wire up the router
app.include_router(api_router)
