"""Startup resilience — runs on every container start to fix common crash-recovery issues."""
import time
import logging

logger = logging.getLogger("startup")

def ensure_demo_user():
    """Create demo user if missing (survives DB resets)."""
    from .database import SessionLocal
    from .models import User
    from .auth import get_password_hash

    max_retries = 10
    for i in range(max_retries):
        try:
            db = SessionLocal()
            demo = db.query(User).filter(User.email == "demo@leanconstruction.ai").first()
            if not demo:
                demo = User(
                    email="demo@leanconstruction.ai",
                    hashed_password=get_password_hash("demo123"),
                    full_name="Demo User",
                    company="Demo Construction Co",
                    role="Project Manager",
                    company_size="small",
                    construction_type="commercial",
                    is_active=1,
                    email_verified=True,
                )
                db.add(demo)
                db.commit()
                logger.info("Demo user created")
            else:
                logger.info("Demo user exists")
            db.close()
            return
        except Exception as e:
            logger.warning(f"DB not ready (attempt {i+1}/{max_retries}): {e}")
            time.sleep(3)
    logger.error("Failed to ensure demo user after retries")

def run_startup():
    logger.info("Running startup checks...")
    ensure_demo_user()
    logger.info("Startup complete")
