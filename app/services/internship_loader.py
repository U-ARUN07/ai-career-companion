"""Internship dataset loader and text representation formatter."""

import json
from pathlib import Path
from typing import Dict, List, Optional
from app.config import settings
from app.schemas.internship import Internship
from app.utils.text_utils import clean_string_list, clean_text


class InternshipLoader:
    """Loads, validates, and serializes internships into embedding-ready text."""

    def __init__(self, data_path: Optional[Path] = None):
        self.data_path = data_path or settings.internships_file
        self.internships: List[Internship] = []
        self._id_map: Dict[str, Internship] = {}

    def load_dataset(self) -> List[Internship]:
        """Load internship opportunities from JSON, validating uniqueness and schema."""
        if not self.data_path.exists():
            raise FileNotFoundError(f"Internship dataset not found at {self.data_path}")

        with open(self.data_path, "r", encoding="utf-8") as f:
            raw_data = json.load(f)

        if not isinstance(raw_data, list):
            raise ValueError(f"Internship data at {self.data_path} must be a JSON array")

        self.internships = []
        self._id_map = {}
        seen_ids = set()

        for item in raw_data:
            internship = Internship(**item)
            if internship.internship_id in seen_ids:
                raise ValueError(f"Duplicate internship ID detected: '{internship.internship_id}'")
            seen_ids.add(internship.internship_id)
            self.internships.append(internship)
            self._id_map[internship.internship_id] = internship

        return self.internships

    def get_by_id(self, internship_id: str) -> Optional[Internship]:
        """Retrieve single internship by ID."""
        if not self._id_map:
            self.load_dataset()
        return self._id_map.get(internship_id)

    @classmethod
    def format_internship_to_text(cls, item: Internship) -> str:
        """Compose comprehensive textual representation of an internship for embedding generation."""
        parts = []

        title = clean_text(item.title)
        company = clean_text(item.company)
        description = clean_text(item.description)
        req_skills = clean_string_list(item.required_skills)
        pref_skills = clean_string_list(item.preferred_skills)
        edu = clean_string_list(item.education_requirements)
        exp = clean_text(item.experience_requirements)
        work_mode = clean_text(item.work_mode)
        location = clean_text(item.location)

        parts.append(f"Internship Opportunity: {title} at {company}")
        if description:
            parts.append(f"Role Overview: {description}")
        if req_skills:
            parts.append(f"Required Mandatory Skills: {', '.join(req_skills)}")
        if pref_skills:
            parts.append(f"Preferred Skills: {', '.join(pref_skills)}")
        if edu:
            parts.append(f"Eligible Education: {', '.join(edu)}")
        if exp:
            parts.append(f"Experience Level: {exp}")
        if work_mode or location:
            mode_loc = []
            if work_mode:
                mode_loc.append(f"Work Mode: {work_mode}")
            if location:
                mode_loc.append(f"Location: {location}")
            parts.append(". ".join(mode_loc))

        full_text = ". ".join(parts)
        if not full_text.endswith("."):
            full_text += "."
        return full_text


internship_loader = InternshipLoader()
