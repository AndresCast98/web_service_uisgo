from datetime import datetime
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.deps import get_db, require_role
from app.models.places import MapEvent, Place, PlaceProduct
from app.schemas.places import (
    PlaceCreate,
    PlaceOut,
    PlaceUpdate,
    PlaceProductCreate,
    PlaceProductOut,
    MapEventCreate,
    MapEventUpdate,
    MapEventOut,
)

router = APIRouter()
require_any_user = require_role("student", "professor", "superuser", "communications", "market_manager")

PLACE_TYPES = ["store", "service", "spot"]
PLACE_CATEGORIES = ["Comida", "Accesorios", "Hogar", "Papelería", "Café", "Tecnología", "Bienestar"]
EVENT_CATEGORIES = ["Cultural", "Académico", "Deportivo", "Wellness", "Promoción"]


def _ensure_owner(place: Place, user_payload: dict) -> None:
    if user_payload.get("role") in {"superuser", "market_manager"}:
        return
    if str(place.owner_id) != user_payload.get("sub"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="forbidden")


def _ensure_event_owner(event: MapEvent, user_payload: dict) -> None:
    if user_payload.get("role") in {"superuser", "market_manager"}:
        return
    if str(event.owner_id) != user_payload.get("sub"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="forbidden")


@router.get("/catalog")
def map_catalog():
    return {
        "place_types": PLACE_TYPES,
        "place_categories": PLACE_CATEGORIES,
        "event_categories": EVENT_CATEGORIES,
    }


@router.get("/", response_model=List[PlaceOut])
def list_places(
    category: Optional[str] = None,
    kind: Optional[str] = None,
    include_inactive: bool = Query(False),
    db: Session = Depends(get_db),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
) -> List[PlaceOut]:
    query = db.query(Place).filter(Place.is_public.is_(True)).order_by(Place.created_at.desc())
    if not include_inactive:
        query = query.filter(Place.status == "active")
    if category:
        query = query.filter(Place.category == category)
    if kind:
        query = query.filter(Place.kind == kind)
    return query.offset(offset).limit(limit).all()


@router.post("/", response_model=PlaceOut, status_code=status.HTTP_201_CREATED)
def create_place(
    body: PlaceCreate,
    user=Depends(require_any_user),
    db: Session = Depends(get_db),
) -> PlaceOut:
    place = Place(owner_id=user["sub"], **body.model_dump())
    db.add(place)
    db.commit()
    db.refresh(place)
    return place


@router.patch("/{place_id}", response_model=PlaceOut)
def update_place(
    place_id: UUID,
    body: PlaceUpdate,
    user=Depends(require_any_user),
    db: Session = Depends(get_db),
) -> PlaceOut:
    place = db.get(Place, place_id)
    if not place:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="place not found")
    _ensure_owner(place, user)
    update_data = body.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(place, key, value)
    db.commit()
    db.refresh(place)
    return place


@router.delete("/{place_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_place(
    place_id: UUID,
    user=Depends(require_any_user),
    db: Session = Depends(get_db),
) -> None:
    place = db.get(Place, place_id)
    if not place:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="place not found")
    _ensure_owner(place, user)
    db.delete(place)
    db.commit()
    return None


@router.post("/{place_id}/products", response_model=PlaceProductOut, status_code=status.HTTP_201_CREATED)
def add_product(
    place_id: UUID,
    body: PlaceProductCreate,
    user=Depends(require_any_user),
    db: Session = Depends(get_db),
) -> PlaceProductOut:
    place = db.get(Place, place_id)
    if not place:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="place not found")
    _ensure_owner(place, user)
    product = PlaceProduct(place_id=place_id, **body.model_dump())
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


@router.delete("/{place_id}/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(
    place_id: UUID,
    product_id: UUID,
    user=Depends(require_any_user),
    db: Session = Depends(get_db),
) -> None:
    place = db.get(Place, place_id)
    if not place:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="place not found")
    _ensure_owner(place, user)
    product = db.get(PlaceProduct, product_id)
    if not product or str(product.place_id) != str(place_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="product not found")
    db.delete(product)
    db.commit()
    return None


@router.get("/{place_id}/products", response_model=List[PlaceProductOut])
def list_products(place_id: UUID, db: Session = Depends(get_db)) -> List[PlaceProductOut]:
    place = db.get(Place, place_id)
    if not place:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="place not found")
    return (
        db.query(PlaceProduct)
        .filter(PlaceProduct.place_id == place_id)
        .order_by(PlaceProduct.created_at.desc())
        .all()
    )


@router.get("/events", response_model=List[MapEventOut])
def list_events(
    category: Optional[str] = None,
    include_expired: bool = False,
    db: Session = Depends(get_db),
    limit: int = Query(100, ge=1, le=200),
    offset: int = Query(0, ge=0),
) -> List[MapEventOut]:
    query = db.query(MapEvent).order_by(MapEvent.start_at.asc())
    if category:
        query = query.filter(MapEvent.category == category)
    if not include_expired:
        query = query.filter(MapEvent.end_at >= datetime.utcnow())
    return query.offset(offset).limit(limit).all()


@router.post("/events", response_model=MapEventOut, status_code=status.HTTP_201_CREATED)
def create_event(
    body: MapEventCreate,
    user=Depends(require_any_user),
    db: Session = Depends(get_db),
) -> MapEventOut:
    if body.end_at <= body.start_at:
        raise HTTPException(status_code=400, detail="end_at must be after start_at")
    if body.place_id:
        place = db.get(Place, body.place_id)
        if not place:
            raise HTTPException(status_code=404, detail="place not found")
    event = MapEvent(owner_id=user["sub"], **body.model_dump())
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


@router.patch("/events/{event_id}", response_model=MapEventOut)
def update_event(
    event_id: UUID,
    body: MapEventUpdate,
    user=Depends(require_any_user),
    db: Session = Depends(get_db),
) -> MapEventOut:
    event = db.get(MapEvent, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="event not found")
    _ensure_event_owner(event, user)
    update_data = body.model_dump(exclude_unset=True)
    if "place_id" in update_data and update_data["place_id"]:
        place = db.get(Place, update_data["place_id"])
        if not place:
            raise HTTPException(status_code=404, detail="place not found")
    if {"start_at", "end_at"} & update_data.keys():
        start = update_data.get("start_at", event.start_at)
        end = update_data.get("end_at", event.end_at)
        if end <= start:
            raise HTTPException(status_code=400, detail="end_at must be after start_at")
    for key, value in update_data.items():
        setattr(event, key, value)
    db.commit()
    db.refresh(event)
    return event


@router.delete("/events/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_event(
    event_id: UUID,
    user=Depends(require_any_user),
    db: Session = Depends(get_db),
) -> None:
    event = db.get(MapEvent, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="event not found")
    _ensure_event_owner(event, user)
    db.delete(event)
    db.commit()
    return None
