from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import Base, engine
from .routers import auth, users, listings, messages, jobs, reviews, payments, analytics, admin

Base.metadata.create_all(bind=engine)

app = FastAPI(title="CampusLink API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(listings.router)
app.include_router(messages.router)
app.include_router(jobs.router)
app.include_router(reviews.router)
app.include_router(payments.router)
app.include_router(analytics.router)
app.include_router(admin.router)

@app.get("/")
def root():
    return {"message": "Welcome to CampusLink API"}