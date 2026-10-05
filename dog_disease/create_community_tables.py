from app import app
from database import db

# ============================================================
# IMPORTANT:
# Import Community models so SQLAlchemy registers
# the tables before db.create_all()
# ============================================================

from community.models import (
    CommunityPost,
    CommunityComment,
    CommunityLike,
    CommunityReport
)


def create_community_tables():

    with app.app_context():

        print("=" * 60)
        print("PAWCARE AI - COMMUNITY DATABASE INITIALIZATION")
        print("=" * 60)

        print("\nCreating Community tables...")

        db.create_all()

        print("\nCommunity tables created successfully!")

        print("\nTables:")
        print("  1. community_posts")
        print("  2. community_comments")
        print("  3. community_likes")
        print("  4. community_reports")

        print("\nDatabase connection is working.")
        print("=" * 60)


if __name__ == "__main__":

    create_community_tables()