# backend/create_tables.py
"""
Simple script to create all database tables
Run this file to initialize your database: python create_tables.py
"""

from app.db.database import engine, Base
from app.models import user, project, product, calculation


def create_tables():
    """Create all tables in the database"""
    print("Creating database tables...")

    # Import all models to ensure they're registered with Base
    Base.metadata.create_all(bind=engine)

    print("✅ Database tables created successfully!")
    print("\nCreated tables:")
    print("  - users")
    print("  - business_projects")
    print("  - products")
    print("  - calculations")


if __name__ == "__main__":
    create_tables()