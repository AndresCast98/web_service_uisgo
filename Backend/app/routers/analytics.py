from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.deps import get_db, require_role
from app.models.activity import Activity, ActivityTarget
from app.models.group import Group, GroupMembership
from app.models.submission import Submission
from app.schemas.analytics import AnalyticsSummary, GroupStats

router = APIRouter()

require_prof_or_super = require_role("professor", "superuser")


@router.get("/my", response_model=AnalyticsSummary)
def my_stats(user=Depends(require_prof_or_super), db: Session = Depends(get_db)):
    groups: List[Group] = (
        db.query(Group)
        .filter(Group.created_by == user["sub"])
        .order_by(Group.created_at.asc())
        .all()
    )

    stats: List[GroupStats] = []
    total_students = 0
    total_activities = 0
    total_submissions = 0

    for group in groups:
        students_count = (
            db.query(func.count(func.distinct(GroupMembership.user_id)))
            .filter(GroupMembership.group_id == group.id)
            .scalar()
            or 0
        )
        students_count = max(students_count - 1, 0)

        activities_count = (
            db.query(func.count(func.distinct(Activity.id)))
            .join(ActivityTarget, ActivityTarget.activity_id == Activity.id)
            .filter(ActivityTarget.group_id == group.id)
            .scalar()
            or 0
        )

        submissions_query = (
            db.query(Submission)
            .join(Activity, Activity.id == Submission.activity_id)
            .join(ActivityTarget, ActivityTarget.activity_id == Activity.id)
            .filter(ActivityTarget.group_id == group.id)
        )

        submissions_count = submissions_query.count()
        correct_count = submissions_query.filter(Submission.is_correct.is_(True)).count()
        responded_students = (
            submissions_query.with_entities(func.count(func.distinct(Submission.user_id))).scalar()
            or 0
        )

        response_rate = (responded_students / students_count * 100) if students_count else 0.0
        accuracy = (correct_count / submissions_count * 100) if submissions_count else 0.0

        stats.append(
            GroupStats(
                group_id=group.id,
                group_name=group.name,
                total_students=students_count,
                responded_students=responded_students,
                response_rate=round(response_rate, 2),
                total_activities=activities_count,
                total_submissions=submissions_count,
                accuracy=round(accuracy, 2),
            )
        )

        total_students += students_count
        total_activities += activities_count
        total_submissions += submissions_count

    summary = AnalyticsSummary(
        generated_at=datetime.utcnow(),
        groups=stats,
        total_groups=len(groups),
        total_students=total_students,
        total_activities=total_activities,
        total_submissions=total_submissions,
    )
    return summary
