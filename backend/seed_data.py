"""
Seed script: creates demo user, projects, tasks & waste logs for leanConstruction.
Run: cd /root/leanConstruction/backend && .venv/bin/python3 seed_data.py
"""

import sys
sys.path.insert(0, '.')
import os
from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
from app.database import SessionLocal, engine
from app.models import Base, User, Project, Task, WasteLog

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        # Check if already seeded
        existing = db.query(User).filter(User.demo_account == True).first()
        if existing:
            print("Demo data already exists — skipping. Delete users table to re-seed.")
            return

        # ── Demo User ──────────────────────────────────────────
        demo_user = User(
            email="demo@leanconstruction.ai",
            hashed_password=pwd_context.hash("demo123"),
            full_name="Fly (Demo Account)",
            company="Lean Construction AI",
            role="admin",
            is_active=1,
            is_onboarded=True,
            onboarding_step=5,
            company_size="enterprise",
            construction_type="infrastructure",
            email_verified=True,
            demo_account=True,
            trial_expires_at=datetime.now(timezone.utc) + timedelta(days=30),
            created_at=datetime.now(timezone.utc) - timedelta(days=60)
        )
        db.add(demo_user)
        db.flush()

        # ── Demo User 2 ─────────────────────────────────────────
        demo_user2 = User(
            email="project@leanconstruction.ai",
            hashed_password=pwd_context.hash("manager123"),
            full_name="Sarah Project-Manager",
            company="Lean Construction AI",
            role="manager",
            is_active=1,
            is_onboarded=True,
            onboarding_step=5,
            company_size="enterprise",
            construction_type="infrastructure",
            email_verified=True,
            demo_account=True,
            trial_expires_at=datetime.now(timezone.utc) + timedelta(days=30),
            created_at=datetime.now(timezone.utc) - timedelta(days=60)
        )
        db.add(demo_user2)
        db.flush()

        # ── Project 1: HS2 London-Birmingham ──────────────────
        hs2 = Project(
            name="HS2 London-Birmingham Phase 1",
            description="High Speed 2 rail link — Phase 1 from London Euston to Birmingham Curzon Street. Original budget £30B, current £100B+. Massive waste detection opportunity.",
            owner_id=demo_user.id,
            status="active",
            budget=100_000_000_000,
            start_date=datetime(2020, 1, 1),
            end_date=datetime(2033, 12, 31),
            created_at=datetime.now(timezone.utc) - timedelta(days=365)
        )
        db.add(hs2)
        db.flush()

        # Tasks for HS2
        hs2_tasks = [
            Task(project_id=hs2.id, name="Tunnel Boring — Chilterns", description="TBM drive through Chiltern Hills, 16km of twin-bore tunnel", status="in_progress", priority="high", estimated_hours=50000, actual_hours=62000),
            Task(project_id=hs2.id, name="Euston Station Redevelopment", description="Major station upgrade and new HS2 platforms at London Euston", status="in_progress", priority="critical", estimated_hours=80000, actual_hours=95000),
            Task(project_id=hs2.id, name="Colne Valley Viaduct", description="3.4km viaduct crossing Colne Valley — longest railway bridge in UK", status="in_progress", priority="high", estimated_hours=30000, actual_hours=28000),
            Task(project_id=hs2.id, name="Birmingham Curzon Street Station", description="New terminus station at Birmingham city centre", status="pending", priority="high", estimated_hours=40000, actual_hours=0),
            Task(project_id=hs2.id, name="Environmental Mitigation", description="Noise barriers, wildlife tunnels, tree planting along the route", status="in_progress", priority="medium", estimated_hours=15000, actual_hours=12000),
            Task(project_id=hs2.id, name="Track Laying — Phase 1", description="High-speed track installation from London to Birmingham", status="pending", priority="high", estimated_hours=25000, actual_hours=0),
        ]
        for t in hs2_tasks:
            db.add(t)

        # Waste logs for HS2
        hs2_waste = [
            WasteLog(project_id=hs2.id, waste_type="waiting", description="Design changes causing 18-month delay on Euston section", impact_cost=2_500_000_000, impact_time=13000),
            WasteLog(project_id=hs2.id, waste_type="defects", description="Ground settlement issues in Chiltern tunnel requiring remediation", impact_cost=450_000_000, impact_time=3000),
            WasteLog(project_id=hs2.id, waste_type="overproduction", description="Over-engineered bridge structures exceeding design specifications", impact_cost=180_000_000, impact_time=2000),
            WasteLog(project_id=hs2.id, waste_type="transportation", description="Material haulage inefficiencies — 40% empty return trips from tunnelling sites", impact_cost=95_000_000, impact_time=1500),
            WasteLog(project_id=hs2.id, waste_type="inventory", description="Excess steel and concrete stockpiled at 12 sites, weather-damaged", impact_cost=210_000_000, impact_time=800),
            WasteLog(project_id=hs2.id, waste_type="motion", description="Poor site layout causing 30% lost time in worker movement at Old Oak Common", impact_cost=75_000_000, impact_time=2500),
            WasteLog(project_id=hs2.id, waste_type="extra_processing", description="Duplicate reporting across 3 different project management systems", impact_cost=12_000_000, impact_time=400),
            WasteLog(project_id=hs2.id, waste_type="non_utilized_talent", description="Skilled engineers assigned to non-technical admin work (estimated 15% of workforce)", impact_cost=320_000_000, impact_time=5000),
        ]
        for w in hs2_waste:
            db.add(w)

        # ── Project 2: Thames Tideway Tunnel ──────────────────
        tideway = Project(
            name="Thames Tideway Tunnel — London",
            description="25km super-sewer under the River Thames to capture sewage overflows. £4.5B infrastructure megaproject.",
            owner_id=demo_user.id,
            status="active",
            budget=4_500_000_000,
            start_date=datetime(2016, 1, 1),
            end_date=datetime(2025, 12, 31),
            created_at=datetime.now(timezone.utc) - timedelta(days=200)
        )
        db.add(tideway)
        db.flush()

        t_tasks = [
            Task(project_id=tideway.id, name="TBM Drive — West Section", description="Tunnel boring from Acton to Carnwath Road", status="completed", priority="high", estimated_hours=20000, actual_hours=21500),
            Task(project_id=tideway.id, name="TBM Drive — Central Section", description="Tunnel boring from Carnwath Road to Chambers Wharf", status="in_progress", priority="high", estimated_hours=25000, actual_hours=23000),
            Task(project_id=tideway.id, name="TBM Drive — East Section", description="Tunnel boring from Chambers Wharf to Beckton", status="pending", priority="high", estimated_hours=22000, actual_hours=0),
            Task(project_id=tideway.id, name="Shaft Construction — 24 sites", description="Construction of 24 interception shafts along the route", status="in_progress", priority="critical", estimated_hours=35000, actual_hours=38000),
        ]
        for t in t_tasks:
            db.add(t)

        t_waste = [
            WasteLog(project_id=tideway.id, waste_type="waiting", description="Utility diversion delays at 8 shaft sites averaging 6 months each", impact_cost=85_000_000, impact_time=4000),
            WasteLog(project_id=tideway.id, waste_type="defects", description="Grouting defects in 3 shaft connections requiring rework", impact_cost=22_000_000, impact_time=800),
            WasteLog(project_id=tideway.id, waste_type="inventory", description="Segmental lining over-ordering by 12%, storage costs at 4 sites", impact_cost=8_500_000, impact_time=200),
        ]
        for w in t_waste:
            db.add(w)

        # ── Project 3: Birmingham Office Tower ─────────────────
        tower = Project(
            name="Birmingham 103 Colmore Row",
            description="26-storey Grade A office tower in Birmingham city centre. £120M commercial development.",
            owner_id=demo_user.id,
            status="active",
            budget=120_000_000,
            start_date=datetime(2024, 3, 1),
            end_date=datetime(2026, 6, 30),
            created_at=datetime.now(timezone.utc) - timedelta(days=90)
        )
        db.add(tower)
        db.flush()

        tower_tasks = [
            Task(project_id=tower.id, name="Foundations & Basement", description="Deep foundations and 3-storey basement excavation", status="completed", priority="high", estimated_hours=8000, actual_hours=9500),
            Task(project_id=tower.id, name="Core & Steel Frame", description="Concrete core and structural steel erection to 26 storeys", status="in_progress", priority="critical", estimated_hours=15000, actual_hours=14000),
            Task(project_id=tower.id, name="Facade Installation", description="Unitised curtain wall system installation", status="pending", priority="high", estimated_hours=10000, actual_hours=0),
            Task(project_id=tower.id, name="MEP Fit-Out", description="Mechanical, electrical and plumbing throughout", status="pending", priority="medium", estimated_hours=18000, actual_hours=0),
        ]
        for t in tower_tasks:
            db.add(t)

        tower_waste = [
            WasteLog(project_id=tower.id, waste_type="waiting", description="Steel delivery delays due to supply chain issues — 6 weeks behind", impact_cost=4_200_000, impact_time=1000),
            WasteLog(project_id=tower.id, waste_type="defects", description="Concrete strength test failures in basement columns — 3 columns demolished and re-poured", impact_cost=850_000, impact_time=320),
        ]
        for w in tower_waste:
            db.add(w)

        # ── Project 4: Residential Development ─────────────────
        residential = Project(
            name="Birmingham City Centre Residential",
            description="450-unit build-to-rent residential development with ground-floor retail. £95M project.",
            owner_id=demo_user.id,
            status="active",
            budget=95_000_000,
            start_date=datetime(2024, 9, 1),
            end_date=datetime(2026, 12, 31),
            created_at=datetime.now(timezone.utc) - timedelta(days=30)
        )
        db.add(residential)
        db.flush()

        res_tasks = [
            Task(project_id=residential.id, name="Site Clearance & Enabling", description="Demolition of existing structures and site preparation", status="completed", priority="medium", estimated_hours=3000, actual_hours=2800),
            Task(project_id=residential.id, name="Substructure", description="Piling, ground beams and ground floor slab", status="in_progress", priority="high", estimated_hours=6000, actual_hours=2000),
            Task(project_id=residential.id, name="Superstructure", description="RC frame construction for blocks A, B and C", status="pending", priority="high", estimated_hours=18000, actual_hours=0),
        ]
        for t in res_tasks:
            db.add(t)

        db.commit()
        print("✅ Seed data loaded successfully!")
        print(f"\n   Users: demo@leanconstruction.ai / demo123")
        print(f"          project@leanconstruction.ai / manager123")
        print(f"   Projects: 4 (HS2, Tideway, 103 Colmore Row, Resi)")
        print(f"   Tasks: {len(hs2_tasks) + len(t_tasks) + len(tower_tasks) + len(res_tasks)}")
        print(f"   Waste logs: {len(hs2_waste) + len(t_waste) + len(tower_waste)}")

    except Exception as e:
        db.rollback()
        print(f"❌ Seed failed: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed()
