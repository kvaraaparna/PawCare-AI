from flask import Blueprint, request, jsonify, session

from database import db

from community.models import (
    CommunityPost,
    CommunityLike,
    CommunityReport
)


community_api = Blueprint(
    "community_api",
    __name__,
    url_prefix="/api/community"
)


# ============================================================
# LIKE / UNLIKE POST
# ============================================================

@community_api.route(
    "/post/<int:post_id>/like",
    methods=["POST"]
)
def toggle_post_like(post_id):

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

    existing_like = CommunityLike.query.filter_by(
        post_id=post_id,
        user_id=session["user_id"]
    ).first()

    if existing_like:

        # Unlike
        db.session.delete(existing_like)
        liked = False

    else:

        # Like
        new_like = CommunityLike(
            post_id=post_id,
            user_id=session["user_id"]
        )

        db.session.add(new_like)
        liked = True

    db.session.commit()

    like_count = CommunityLike.query.filter_by(
        post_id=post_id
    ).count()

    return jsonify({
        "success": True,
        "liked": liked,
        "like_count": like_count
    })


# ============================================================
# GET LIKE COUNT
# ============================================================

@community_api.route(
    "/post/<int:post_id>/likes",
    methods=["GET"]
)
def get_like_count(post_id):

    post = CommunityPost.query.get(post_id)

    if post is None:

        return jsonify({
            "success": False,
            "message": "Post not found."
        }), 404

    count = CommunityLike.query.filter_by(
        post_id=post_id
    ).count()

    return jsonify({
        "success": True,
        "like_count": count
    })


# ============================================================
# REPORT POST
# ============================================================

@community_api.route(
    "/post/<int:post_id>/report",
    methods=["POST"]
)
def report_post(post_id):

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

    reason = str(
        data.get("reason", "")
    ).strip()

    description = str(
        data.get("description", "")
    ).strip()

    if not reason:

        return jsonify({
            "success": False,
            "message": "Please select a reason."
        }), 400

    # Prevent duplicate reports
    existing_report = CommunityReport.query.filter_by(
        post_id=post_id,
        user_id=session["user_id"]
    ).first()

    if existing_report:

        return jsonify({
            "success": False,
            "message": "You have already reported this post."
        }), 400

    report = CommunityReport(
        post_id=post_id,
        user_id=session["user_id"],
        reason=reason,
        description=description,
        status="pending"
    )

    db.session.add(report)
    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Report submitted successfully."
    }), 201