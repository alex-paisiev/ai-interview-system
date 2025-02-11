import uvicorn
from fastapi import FastAPI
from sqladmin import Admin, ModelView

from app.database import engine
from app.models import InterviewSession

app = FastAPI(title="My Application Admin")

admin = Admin(app, engine, title="Admin Panel")


class InterviewSessionAdmin(ModelView, model=InterviewSession):
    column_list = [
        InterviewSession.id,
        InterviewSession.candidate_id,
        InterviewSession.job_title,
        InterviewSession.timestamp,
    ]


admin.add_view(InterviewSessionAdmin)

if __name__ == "__main__":
    uvicorn.run("app.admin_panel_sqladmin:app", host="0.0.0.0", port=8000, reload=True)
