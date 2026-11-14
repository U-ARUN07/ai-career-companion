"""Text utility functions for cleaning, normalization, and skill extraction."""

import re
from typing import Any, List, Set


def clean_text(text: Any) -> str:
    """Clean and normalize a string safely, handling None or non-string inputs."""
    if text is None:
        return ""
    if not isinstance(text, str):
        text = str(text)
    # Replace multiple whitespaces and tabs with a single space
    cleaned = re.sub(r"[\r\n\t]+", " ", text)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned


def clean_string_list(items: Any) -> List[str]:
    """Clean, strip, and filter a list of strings, removing empty entries."""
    if not items:
        return []
    if isinstance(items, str):
        items = [items]
    if not isinstance(items, (list, tuple, set)):
        items = [str(items)]

    cleaned_list = []
    seen = set()
    for item in items:
        cleaned_item = clean_text(item)
        if cleaned_item and cleaned_item.lower() not in seen:
            seen.add(cleaned_item.lower())
            cleaned_list.append(cleaned_item)
    return cleaned_list


def normalize_skill(skill: str) -> str:
    """Normalize a skill name for robust semantic/lexical comparison."""
    cleaned = clean_text(skill).lower()
    # Normalize common symbols: e.g. c++ -> cpp, .net -> dotnet, node.js -> nodejs
    cleaned = re.sub(r"\.js\b", "js", cleaned)
    cleaned = re.sub(r"\bc\+\+\b", "cpp", cleaned)
    cleaned = re.sub(r"\bc#\b", "csharp", cleaned)
    cleaned = re.sub(r"[^a-z0-9#+]", "", cleaned)
    return cleaned


def find_matching_and_missing_skills(
    candidate_skills: List[str], required_skills: List[str]
) -> tuple[List[str], List[str]]:
    """Compare candidate skills with required skills and return matching and missing subsets."""
    norm_candidate_skills: dict[str, str] = {
        normalize_skill(s): s for s in candidate_skills if clean_text(s)
    }

    matching_skills: List[str] = []
    missing_skills: List[str] = []

    for req in required_skills:
        req_clean = clean_text(req)
        if not req_clean:
            continue
        norm_req = normalize_skill(req_clean)
        # Check direct match or substring match
        matched = False
        for c_norm, original_c in norm_candidate_skills.items():
            if norm_req == c_norm or norm_req in c_norm or c_norm in norm_req:
                matched = True
                matching_skills.append(req_clean)
                break
        if not matched:
            missing_skills.append(req_clean)

    return matching_skills, missing_skills
