from flask import Blueprint, request, jsonify, session

from database import db
from community.models import CommunityPost, CommunityComment

from .service import add_comment
comment_bp = Blueprint(
    "community_comments",
    __name__,
    url_prefix="/community"
)


# ============================================================
# GET COMMENTS FOR A POST
# ============================================================

@comment_bp.route(
    "/post/<int:post_id>/comments",
    methods=["GET"]
)
def get_post_comments(post_id):

    post = CommunityPost.query.get(post_id)

    if post is None:
        return jsonify({
            "success": False,
            "message": "Post not found."
        }), 404

    comments = CommunityComment.query.filter_by(
        post_id=post_id
    ).order_by(
        CommunityComment.created_at.asc()
    ).all()

    comment_data = []

    for comment in comments:

        comment_data.append({
            "id": comment.id,
            "post_id": comment.post_id,
            "user_id": comment.user_id,
            "content": comment.content,
            "created_at": comment.created_at.isoformat()
            if comment.created_at else None
        })

    return jsonify({
        "success": True,
        "comments": comment_data
    })


# ============================================================
# CREATE COMMENT
# ============================================================

@comment_bp.route(
    "/post/<int:post_id>/comments",
    methods=["POST"]
)
def add_comment(post_id):

    # User must be logged in
    if "user_id" not in session:

        return jsonify({
            "success": False,
            "message": "Please login first."
        }), 401

    post = CommunityPost.query.get(post_id)

    if post is None:

        return jsonify({
            "success": False,
            "message": "Post not found."
        }), 404

    data = request.get_json(
        silent=True
    ) or {}

    content = str(
        data.get("content", "")
    ).strip()

    if not content:

        return jsonify({
            "success": False,
            "message": "Comment cannot be empty."
        }), 400

    if len(content) > 2000:

        return jsonify({
            "success": False,
            "message": "Comment cannot exceed 2000 characters."
        }), 400

    comment = CommunityComment(
        post_id=post_id,
        user_id=session["user_id"],
        content=content
    )

    db.session.add(comment)
    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Comment added successfully.",
        "comment": {
            "id": comment.id,
            "post_id": comment.post_id,
            "user_id": comment.user_id,
            "content": comment.content,
            "created_at": comment.created_at.isoformat()
            if comment.created_at else None
        }
    }), 201


# ============================================================
# DELETE COMMENT
# ============================================================

@comment_bp.route(
    "/comments/<int:comment_id>",
    methods=["DELETE"]
)
def delete_comment(comment_id):

    if "user_id" not in session:

        return jsonify({
            "success": False,
            "message": "Please login first."
        }), 401

    comment = CommunityComment.query.get(comment_id)

    if comment is None:

        return jsonify({
            "success": False,
            "message": "Comment not found."
        }), 404

    # Only the comment owner can delete it
    if comment.user_id != session["user_id"]:

        return jsonify({
            "success": False,
            "message": "You are not authorized to delete this comment."
        }), 403

    db.session.delete(comment)
    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Comment deleted successfully."
    })