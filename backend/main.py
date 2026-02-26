from fastapi import FastAPI
from admin.panel import router
app = FastAPI()
app.include_router(router)
