from __future__ import annotations

from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Dict, Optional
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field


class LeaseStatus(str, Enum):
    PAYMENT_REQUIRED = "PAYMENT_REQUIRED"
    PAID = "PAID"
    PROVISIONING = "PROVISIONING"
    READY = "READY"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    PAYMENT_DENIED = "PAYMENT_DENIED"
    PAYMENT_EXPIRED = "PAYMENT_EXPIRED"
    PROVISION_FAILED = "PROVISION_FAILED"
    RUN_FAILED = "RUN_FAILED"
    TIMEOUT_TERMINATED = "TIMEOUT_TERMINATED"


class LeaseRequest(BaseModel):
    agent_id: str = Field(min_length=1, max_length=128)
    profile: str = Field(default="cpu-small", min_length=1, max_length=64)
    max_minutes: int = Field(default=60, ge=5, le=240)
    job_summary: str = Field(min_length=1, max_length=500)


class JobRequest(BaseModel):
    command: str = Field(min_length=1, max_length=1000)
    env: Dict[str, str] = Field(default_factory=dict)


class LeaseRecord(BaseModel):
    lease_id: str
    agent_id: str
    profile: str
    max_minutes: int
    job_summary: str
    status: LeaseStatus
    created_at: str
    expires_at: str
    spend_request_id: Optional[str] = None
    compute_endpoint: Optional[str] = None


app = FastAPI(title="Agent EC2 Lease API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

LEASES: Dict[str, LeaseRecord] = {}
JOBS: Dict[str, dict] = {}


@app.get("/healthz")
def healthz() -> dict:
    return {"ok": True, "service": "agent-ec2-api", "version": "0.1.0"}


@app.post("/v1/leases")
def create_lease(req: LeaseRequest, response: Response) -> dict:
    lease_id = f"lease_{uuid4().hex[:12]}"
    spend_request_id = f"lsrq_{uuid4().hex[:10]}"
    now = datetime.now(timezone.utc)
    expires = now + timedelta(minutes=15)

    lease = LeaseRecord(
        lease_id=lease_id,
        agent_id=req.agent_id,
        profile=req.profile,
        max_minutes=req.max_minutes,
        job_summary=req.job_summary,
        status=LeaseStatus.PAYMENT_REQUIRED,
        created_at=now.isoformat(),
        expires_at=expires.isoformat(),
        spend_request_id=spend_request_id,
    )
    LEASES[lease_id] = lease

    response.status_code = 402
    return {
        "error": "PAYMENT_REQUIRED",
        "lease_id": lease_id,
        "status": lease.status,
        "payment": {
            "provider": "stripe_link_cli",
            "mode": "mpp_http_402",
            "spend_request_id": spend_request_id,
            "credential_type": "shared_payment_token",
            "mpp_endpoint": f"/v1/pay/{lease_id}",
            "poll_url": f"/v1/leases/{lease_id}",
        },
        "expires_at": lease.expires_at,
    }


@app.get("/v1/leases/{lease_id}")
def get_lease(lease_id: str, response: Response) -> dict:
    lease = LEASES.get(lease_id)
    if not lease:
        raise HTTPException(status_code=404, detail="Lease not found")

    if lease.status == LeaseStatus.PAYMENT_REQUIRED:
        response.status_code = 402
        return {
            "error": "PAYMENT_REQUIRED",
            "lease_id": lease_id,
            "status": lease.status,
            "payment": {
                "provider": "stripe_link_cli",
                "mode": "mpp_http_402",
                "spend_request_id": lease.spend_request_id,
                "credential_type": "shared_payment_token",
                "mpp_endpoint": f"/v1/pay/{lease_id}",
                "poll_url": f"/v1/leases/{lease_id}",
            },
            "expires_at": lease.expires_at,
        }

    return lease.model_dump()


@app.post("/v1/pay/{lease_id}")
def pay_lease(lease_id: str) -> dict:
    lease = LEASES.get(lease_id)
    if not lease:
        raise HTTPException(status_code=404, detail="Lease not found")

    if lease.status != LeaseStatus.PAYMENT_REQUIRED:
        return {"ok": True, "lease_id": lease_id, "status": lease.status}

    lease.status = LeaseStatus.PROVISIONING
    lease.compute_endpoint = None

    # MVP stub: instant provisioning simulation.
    lease.status = LeaseStatus.READY
    lease.compute_endpoint = f"https://compute.local/{lease_id}"
    LEASES[lease_id] = lease

    return {
        "ok": True,
        "lease_id": lease_id,
        "status": lease.status,
        "compute_endpoint": lease.compute_endpoint,
    }


@app.post("/v1/leases/{lease_id}/jobs")
def submit_job(lease_id: str, job: JobRequest) -> dict:
    lease = LEASES.get(lease_id)
    if not lease:
        raise HTTPException(status_code=404, detail="Lease not found")
    if lease.status != LeaseStatus.READY:
        raise HTTPException(status_code=409, detail=f"Lease not ready (status={lease.status})")

    job_id = f"job_{uuid4().hex[:12]}"
    lease.status = LeaseStatus.RUNNING

    JOBS[job_id] = {
        "job_id": job_id,
        "lease_id": lease_id,
        "status": "RUNNING",
        "command": job.command,
        "env": job.env,
        "started_at": datetime.now(timezone.utc).isoformat(),
        "logs": [
            "[mvp] executing command",
            f"[mvp] {job.command}",
            "[mvp] completed successfully",
        ],
    }

    JOBS[job_id]["status"] = "COMPLETED"
    JOBS[job_id]["finished_at"] = datetime.now(timezone.utc).isoformat()
    lease.status = LeaseStatus.COMPLETED
    LEASES[lease_id] = lease

    return {"job_id": job_id, "status": "COMPLETED"}


@app.get("/v1/jobs/{job_id}")
def get_job(job_id: str) -> dict:
    job = JOBS.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@app.get("/v1/jobs/{job_id}/logs")
def get_job_logs(job_id: str) -> dict:
    job = JOBS.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return {"job_id": job_id, "logs": job["logs"]}
