from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models.job import Job, JobApplication
from ..models.user import User
from ..schemas.job import JobCreate, JobUpdate, JobResponse, JobApplicationCreate, JobApplicationResponse
from ..utils.dependencies import get_current_user

router = APIRouter(prefix="/jobs", tags=["Jobs"])

@router.post("/", response_model=JobResponse)
def create_job(
    job: JobCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    new_job = Job(**job.dict(), owner_id=current_user.id)
    db.add(new_job)
    db.commit()
    db.refresh(new_job)
    new_job.owner_name = current_user.full_name
    return new_job

@router.get("/", response_model=List[JobResponse])
def get_all_jobs(db: Session = Depends(get_db)):
    jobs = db.query(Job).filter(Job.is_open == True).all()
    for job in jobs:
        owner = db.query(User).filter(User.id == job.owner_id).first()
        if owner:
            job.owner_name = owner.full_name
    return jobs

@router.get("/{job_id}", response_model=JobResponse)
def get_job(job_id: int, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    owner = db.query(User).filter(User.id == job.owner_id).first()
    if owner:
        job.owner_name = owner.full_name
    return job

@router.put("/{job_id}", response_model=JobResponse)
def update_job(
    job_id: int,
    job_update: JobUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if job.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this job")
    
    for key, value in job_update.dict(exclude_unset=True).items():
        setattr(job, key, value)
    
    db.commit()
    db.refresh(job)
    job.owner_name = current_user.full_name
    return job

@router.delete("/{job_id}")
def delete_job(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if job.owner_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to delete this job")
    
    db.delete(job)
    db.commit()
    return {"message": "Job deleted successfully"}

@router.post("/{job_id}/apply", response_model=JobApplicationResponse)
def apply_for_job(
    job_id: int,
    application: JobApplicationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if not job.is_open:
        raise HTTPException(status_code=400, detail="Job is no longer open")
    if job.owner_id == current_user.id:
        raise HTTPException(status_code=400, detail="You cannot apply to your own job")
    
    existing_application = db.query(JobApplication).filter(
        JobApplication.job_id == job_id,
        JobApplication.applicant_id == current_user.id
    ).first()
    if existing_application:
        raise HTTPException(status_code=400, detail="You have already applied for this job")
    
    new_application = JobApplication(
        cover_letter=application.cover_letter,
        job_id=job_id,
        applicant_id=current_user.id
    )
    db.add(new_application)
    db.commit()
    db.refresh(new_application)

    # Send notification to job owner
    from ..models.notification import Notification
    notification = Notification(
        message=f"{current_user.full_name} applied for your job: {job.title}",
        notification_type="job_application",
        user_id=job.owner_id
    )
    db.add(notification)
    db.commit()

    return new_application
):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if not job.is_open:
        raise HTTPException(status_code=400, detail="Job is no longer open")
    if job.owner_id == current_user.id:
        raise HTTPException(status_code=400, detail="You cannot apply to your own job")
    
    existing_application = db.query(JobApplication).filter(
        JobApplication.job_id == job_id,
        JobApplication.applicant_id == current_user.id
    ).first()
    if existing_application:
        raise HTTPException(status_code=400, detail="You have already applied for this job")
    
    new_application = JobApplication(
        cover_letter=application.cover_letter,
        job_id=job_id,
        applicant_id=current_user.id
    )
    db.add(new_application)
    db.commit()
    db.refresh(new_application)
    return new_application

@router.get("/{job_id}/applications", response_model=List[JobApplicationResponse])
def get_job_applications(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if job.owner_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to view applications")
    
    return db.query(JobApplication).filter(JobApplication.job_id == job_id).all()