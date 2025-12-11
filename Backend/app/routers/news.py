from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.deps import get_db, require_role
from app.models.news import NewsArticle
from app.schemas.news import NewsCreate, NewsOut, NewsUpdate

router = APIRouter()
require_any_user = require_role("student", "professor", "superuser", "communications")
require_news_editor = require_role("professor", "superuser", "communications")


@router.get("/", response_model=List[NewsOut])
def list_news(
    category: Optional[str] = None,
    published: Optional[bool] = None,
    limit: int = Query(20, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
) -> List[NewsOut]:
    query = db.query(NewsArticle).order_by(NewsArticle.publish_at.desc().nullslast(), NewsArticle.created_at.desc())
    if category:
        query = query.filter(NewsArticle.category == category)
    if published is not None:
        query = query.filter(NewsArticle.published.is_(published))
    else:
        query = query.filter(NewsArticle.published.is_(True))
    return query.offset(offset).limit(limit).all()


@router.post("/", response_model=NewsOut, status_code=status.HTTP_201_CREATED)
def create_news(
    body: NewsCreate,
    _: dict = Depends(require_news_editor),
    db: Session = Depends(get_db),
) -> NewsOut:
    article = NewsArticle(
        title=body.title,
        subtitle=body.subtitle,
        body=body.body,
        category=body.category,
        tag=body.tag,
        image_url=body.image_url,
        thumbnail_url=body.thumbnail_url,
        hero_image_url=body.hero_image_url,
        cta_url=body.cta_url,
        publish_at=body.publish_at,
        published=False,
    )
    db.add(article)
    db.commit()
    db.refresh(article)
    return article


@router.patch("/{article_id}", response_model=NewsOut)
def update_news(
    article_id: UUID,
    body: NewsUpdate,
    _: dict = Depends(require_news_editor),
    db: Session = Depends(get_db),
) -> NewsOut:
    article = db.get(NewsArticle, article_id)
    if not article:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="article not found")

    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(article, field, value)
    db.commit()
    db.refresh(article)
    return article


@router.post("/{article_id}/publish", response_model=NewsOut)
def publish_news(
    article_id: UUID,
    _: dict = Depends(require_news_editor),
    db: Session = Depends(get_db),
) -> NewsOut:
    article = db.get(NewsArticle, article_id)
    if not article:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="article not found")
    article.published = True
    if article.publish_at is None:
        from datetime import datetime

        article.publish_at = datetime.utcnow()
    db.commit()
    db.refresh(article)
    return article
