from app.core.security import hash_password
from app.db.session import SessionLocal
from app.models.user import User, Role

db = SessionLocal()
try:
    u = User(
        email="admin@uis.edu",
        password_hash=hash_password("admin123"),
        role=Role.superuser,
        full_name="Admin José Valera"
    )
    db.add(u)
    db.commit()
    db.refresh(u)
    print(u.id)
finally:
    db.close()