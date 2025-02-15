from fastapi import FastAPI
from .database import engine, Base
from .routers.company import router as company_router
from .routers.assessments import router as assessments_router
from .routers.tasks import router as task_router
from .routers.scoring import router as scoring_router
from .routers.due_diligence import router as due_diligence_router
from .routers.auth import router as auth_router
# from .monitoring.azure_monitor import setup_monitoring

# Create database tables if they don't exist
Base.metadata.create_all(bind=engine)

app = FastAPI()

# Include API routers
app.include_router(company_router)
app.include_router(assessments_router)
app.include_router(task_router)
app.include_router(scoring_router)
app.include_router(due_diligence_router)
app.include_router(auth_router)

# Setup Azure monitoring (if instrumentation key provided)
# setup_monitoring(app)

@app.get("/")
def read_root():
    return {"message": "Welcome to the TPRM Web API"}