from typing import List, Tuple

from profiles.models import JobSeekerProfile


def _tokenize_skills(raw: str) -> List[str]:
    if not raw:
        return []
    tokens: List[str] = []
    for part in raw.replace(',', ' ').split():
        token = part.strip().lower()
        if token:
            tokens.append(token)
    return tokens


def score_candidate_for_job(job, profile: JobSeekerProfile) -> float:
    job_skills = set(_tokenize_skills(getattr(job, 'skills', '')))
    candidate_skills = set(_tokenize_skills(profile.skills))

    if not job_skills or not candidate_skills:
        return 0.0

    overlap = job_skills.intersection(candidate_skills)
    base = len(overlap) / max(len(job_skills), 1)

    # Light remote bonus if job supports remote/hybrid
    remote_type = getattr(job, 'remote_type', None)
    remote_bonus = 0.05 if remote_type in ('RE', 'HY') else 0.0

    return round(base + remote_bonus, 4)


def recommend_candidates_for_job(job, limit: int = 5) -> List[Tuple[JobSeekerProfile, float]]:
    candidates = JobSeekerProfile.objects.filter(is_public=True).select_related('user')
    scored: List[Tuple[JobSeekerProfile, float]] = []
    for profile in candidates:
        score = score_candidate_for_job(job, profile)
        if score > 0:
            scored.append((profile, score))

    scored.sort(key=lambda x: x[1], reverse=True)
    return scored[:limit]


