from datetime import datetime

from database import db



# ============================================================
# COMMUNITY POST
# ============================================================

class CommunityPost(db.Model):
    __tablename__ = "community_posts"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    user_id = db.Column(
        db.Integer,
        nullable=False,
        index=True
    )

    title = db.Column(
        db.String(100),
        nullable=True
    )

    content = db.Column(
        db.Text,
        nullable=False
    )

    category = db.Column(
        db.String(100),
        nullable=False,
        index=True
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    # Relationships
    comments = db.relationship(
        "CommunityComment",
        backref="post",
        lazy=True,
        cascade="all, delete-orphan"
    )

    likes = db.relationship(
        "CommunityLike",
        backref="post",
        lazy=True,
        cascade="all, delete-orphan"
    )

    reports = db.relationship(
        "CommunityReport",
        backref="post",
        lazy=True,
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<CommunityPost {self.id}>"


# ============================================================
# COMMUNITY COMMENT
# ============================================================

class CommunityComment(db.Model):
    __tablename__ = "community_comments"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    post_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "community_posts.id",
            ondelete="CASCADE"
        ),
        nullable=False,
        index=True
    )

    user_id = db.Column(
        db.Integer,
        nullable=False,
        index=True
    )

    content = db.Column(
        db.Text,
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    def __repr__(self):
        return f"<CommunityComment {self.id}>"


# ============================================================
# COMMUNITY LIKE
# ============================================================

class CommunityLike(db.Model):
    __tablename__ = "community_likes"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    post_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "community_posts.id",
            ondelete="CASCADE"
        ),
        nullable=False,
        index=True
    )

    user_id = db.Column(
        db.Integer,
        nullable=False,
        index=True
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    # One user can like a post only once
    __table_args__ = (
        db.UniqueConstraint(
            "post_id",
            "user_id",
            name="unique_post_user_like"
        ),
    )

    def __repr__(self):
        return f"<CommunityLike {self.id}>"


# ============================================================
# COMMUNITY REPORT
# ============================================================

class CommunityReport(db.Model):
    __tablename__ = "community_reports"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    post_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "community_posts.id",
            ondelete="CASCADE"
        ),
        nullable=False,
        index=True
    )

    user_id = db.Column(
        db.Integer,
        nullable=False,
        index=True
    )

    reason = db.Column(
        db.String(255),
        nullable=False
    )

    description = db.Column(
        db.Text,
        nullable=True
    )

    status = db.Column(
        db.String(30),
        default="pending",
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    def __repr__(self):
        return f"<CommunityReport {self.id}>"