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

def create_post(
    user_id,
    title,
    content,
    category
):
    """
    Create a new community discussion post.
    """

    post = CommunityPost(
        user_id=user_id,
        title=title.strip(),
        content=content.strip(),
        category=category.strip()
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
# GET POSTS BY CATEGORY
# ============================================================

def get_posts_by_category(category):

    return CommunityPost.query.filter_by(
        category=category
    ).order_by(
        CommunityPost.created_at.desc()
    ).all()


# ============================================================
# SEARCH POSTS
# ============================================================

def search_posts(search_term):

    search_term = search_term.strip()

    if not search_term:
        return get_all_posts()

    return CommunityPost.query.filter(
        db.or_(
            CommunityPost.title.ilike(
                f"%{search_term}%"
            ),
            CommunityPost.content.ilike(
                f"%{search_term}%"
            ),
            CommunityPost.category.ilike(
                f"%{search_term}%"
            )
        )
    ).order_by(
        CommunityPost.created_at.desc()
    ).all()


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
        content=content.strip()
    )

    db.session.add(comment)
    db.session.commit()

    return comment


# ============================================================
# GET COMMENTS
# ============================================================

def get_comments(post_id):

    return CommunityComment.query.filter_by(
        post_id=post_id
    ).order_by(
        CommunityComment.created_at.asc()
    ).all()


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
# GET LIKE COUNT
# ============================================================

def get_like_count(post_id):

    return CommunityLike.query.filter_by(
        post_id=post_id
    ).count()


# ============================================================
# REPORT POST
# ============================================================

def report_post(
    post_id,
    user_id,
    reason,
    description=None
):

    report = CommunityReport(
        post_id=post_id,
        user_id=user_id,
        reason=reason.strip(),
        description=description.strip()
        if description
        else None,
        status="pending"
    )

    db.session.add(report)
    db.session.commit()

    return report


# ============================================================
# UPDATE POST
# ============================================================

def update_post(
    post_id,
    user_id,
    title,
    content,
    category
):

    post = CommunityPost.query.get(post_id)

    if post is None:
        return None, "Post not found."

    if post.user_id != user_id:
        return None, "You are not authorized to edit this post."

    if not title.strip():
        return None, "Title is required."

    if not content.strip():
        return None, "Content is required."

    if not category.strip():
        return None, "Category is required."

    post.title = title.strip()
    post.content = content.strip()
    post.category = category.strip()

    db.session.commit()

    return post, None


# ============================================================
# DELETE POST
# ============================================================

def delete_post(
    post_id,
    user_id
):

    post = CommunityPost.query.get(post_id)

    if post is None:
        return False, "Post not found."

    if post.user_id != user_id:
        return False, "You are not authorized to delete this post."

    db.session.delete(post)

    db.session.commit()

    return True, None