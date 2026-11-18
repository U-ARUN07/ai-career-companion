"""Application Tracking and Management Service.

Stores, retrieves, and manages submitted student internship applications
with cover letter records and status tracking.
"""

import uuid
from datetime import datetime
from typing import List, Optional
from app.schemas.cover_letter import ApplicationRecord, ApplicationSubmissionRequest
from app.services.cover_letter_service import cover_letter_service
from app.services.internship_loader import InternshipLoader


class ApplicationService:
    """Manages student internship applications."""

    def __init__(self):
        self._applications: List[ApplicationRecord] = []
        self.loader = InternshipLoader()

    def submit_application(self, req: ApplicationSubmissionRequest) -> ApplicationRecord:
        """Submit and record an internship application with generated cover letter."""
        internship = self.loader.get_by_id(req.internship_id)
        if not internship:
            raise ValueError(f"Internship '{req.internship_id}' does not exist.")

        # Compute ATS score
        cl_resp = cover_letter_service.generate(req.candidate, req.internship_id)

        app_id = f"APP-{uuid.uuid4().hex[:8].upper()}"
        record = ApplicationRecord(
            application_id=app_id,
            internship_id=internship.internship_id,
            internship_title=internship.title,
            company_name=internship.company,
            candidate_name=req.candidate.name,
            submitted_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            status="Submitted",
            ats_score=cl_resp.ats_score,
            cover_letter=req.cover_letter or cl_resp.tailored_cover_letter,
        )

        self._applications.insert(0, record)
        return record

    def list_applications(self) -> List[ApplicationRecord]:
        """Return all submitted applications."""
        return self._applications

    def update_status(self, app_id: str, new_status: str, notes: Optional[str] = None) -> Optional[ApplicationRecord]:
        """Update status of a tracked application."""
        for app in self._applications:
            if app.application_id == app_id:
                app.status = new_status
                return app
        return None


application_service = ApplicationService()
