from database import db

from .models import (
    CommunityPost,
    CommunityComment,
    CommunityLike,
    CommunityReport
)


# ============================================================
# CREATE POST
# ============================================================

def create_post(user_id, content, image_url=None):

    post = CommunityPost(
        user_id=user_id,
        content=content,
        image_url=image_url
    )

    db.session.add(post)
    db.session.commit()

    return post


# ============================================================
# GET ALL POSTS
# ============================================================

def get_all_posts():

    return CommunityPost.query.order_by(
        CommunityPost.created_at.desc()
    ).all()


# ============================================================
# GET SINGLE POST
# ============================================================

def get_post_by_id(post_id):

    return CommunityPost.query.get(post_id)


# ============================================================
# ADD COMMENT
# ============================================================

def add_comment(
    post_id,
    user_id,
    content
):

    comment = CommunityComment(
        post_id=post_id,
        user_id=user_id,
        content=content
    )

    db.session.add(comment)
    db.session.commit()

    return comment


# ============================================================
# LIKE / UNLIKE POST
# ============================================================

def toggle_like(
    post_id,
    user_id
):

    existing_like = CommunityLike.query.filter_by(
        post_id=post_id,
        user_id=user_id
    ).first()

    if existing_like:

        db.session.delete(existing_like)

        liked = False

    else:

        like = CommunityLike(
            post_id=post_id,
            user_id=user_id
        )

        db.session.add(like)

        liked = True

    db.session.commit()

    like_count = CommunityLike.query.filter_by(
        post_id=post_id
    ).count()

    return liked, like_count


# ============================================================
# REPORT POST
# ============================================================

def report_post(
    post_id,
    user_id,
    reason
):

    report = CommunityReport(
        post_id=post_id,
        user_id=user_id,
        reason=reason
    )

    db.session.add(report)
    db.session.commit()

    return report
# ============================================================
# GET POSTS BY CATEGORY
# ============================================================

def get_posts_by_category(category):
    """
    Return posts belonging to a specific category.
    """

    return CommunityPost.query.filter_by(
        category=category
    ).order_by(
        CommunityPost.created_at.desc()
    ).all()


# ============================================================
# SEARCH POSTS
# ============================================================

def search_posts(search_term):
    """
    Search posts by their content.
    """

    search_term = search_term.strip()

    if not search_term:
        return get_all_posts()

    return CommunityPost.query.filter(
        CommunityPost.content.ilike(
            f"%{search_term}%"
        )
    ).order_by(
        CommunityPost.created_at.desc()
    ).all()


# ============================================================
# UPDATE POST
# ============================================================

def update_post(
    post_id,
    user_id,
    content,
    category=None
):
    """
    Update a post.
    Only the post owner can update it.
    """

    post = CommunityPost.query.get(post_id)

    if post is None:
        return None

    # Security check
    if post.user_id != user_id:
        return None

    content = content.strip()

    if not content:
        return None

    post.content = content

    if category is not None:
        post.category = category.strip()

    db.session.commit()

    return post


# ============================================================
# DELETE POST
# ============================================================

def delete_post(
    post_id,
    user_id
):
    """
    Delete a post.
    Only the post owner can delete it.
    """

    post = CommunityPost.query.get(post_id)

    if post is None:
        return False

    # Security check
    if post.user_id != user_id:
        return False

    db.session.delete(post)

    db.session.commit()

    return True