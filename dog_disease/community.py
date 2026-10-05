from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from datetime import datetime
import uuid


# ============================================================
# COMMUNITY BLUEPRINT
# ============================================================

community_bp = Blueprint(
    "community",
    __name__,
    url_prefix="/community"
)


# ============================================================
# COMMENT BLUEPRINT
# ============================================================

comment_bp = Blueprint(
    "comments",
    __name__,
    url_prefix="/community"
)


# ============================================================
# COMMUNITY API BLUEPRINT
# ============================================================

community_api = Blueprint(
    "community_api",
    __name__,
    url_prefix="/api/community"
)


# ============================================================
# TEMPORARY IN-MEMORY DATA
# ============================================================
# This is only for testing the Community page.
# Later we can connect these to PostgreSQL.

community_posts = []


# ============================================================
# COMMUNITY HOME PAGE
# ============================================================

@community_bp.route("/")
def community_home():
    """
    Displays the PawCare AI Community page.
    """

    return render_template(
        "community.html",
        posts=community_posts
    )


# ============================================================
# CREATE POST
# ============================================================

@community_bp.route("/create", methods=["POST"])
def create_post():

    content = request.form.get("content", "").strip()

    if not content:
        return jsonify({
            "success": False,
            "message": "Post content cannot be empty."
        }), 400

    post = {
        "id": str(uuid.uuid4()),
        "content": content,
        "author": "PawCare User",
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "comments": []
    }

    community_posts.insert(0, post)

    return jsonify({
        "success": True,
        "message": "Post created successfully.",
        "post": post
    })


# ============================================================
# GET ALL POSTS
# ============================================================

@community_api.route("/posts", methods=["GET"])
def get_posts():

    return jsonify({
        "success": True,
        "posts": community_posts
    })


# ============================================================
# GET SINGLE POST
# ============================================================

@community_api.route("/posts/<post_id>", methods=["GET"])
def get_post(post_id):

    post = next(
        (p for p in community_posts if p["id"] == post_id),
        None
    )

    if not post:
        return jsonify({
            "success": False,
            "message": "Post not found."
        }), 404

    return jsonify({
        "success": True,
        "post": post
    })


# ============================================================
# ADD COMMENT
# ============================================================

@comment_bp.route("/posts/<post_id>/comment", methods=["POST"])
def add_comment(post_id):

    post = next(
        (p for p in community_posts if p["id"] == post_id),
        None
    )

    if not post:
        return jsonify({
            "success": False,
            "message": "Post not found."
        }), 404

    comment_text = request.form.get("comment", "").strip()

    if not comment_text:
        return jsonify({
            "success": False,
            "message": "Comment cannot be empty."
        }), 400

    comment = {
        "id": str(uuid.uuid4()),
        "author": "PawCare User",
        "content": comment_text,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M")
    }

    post["comments"].append(comment)

    return jsonify({
        "success": True,
        "message": "Comment added successfully.",
        "comment": comment
    })


# ============================================================
# DELETE POST
# ============================================================

@community_api.route("/posts/<post_id>", methods=["DELETE"])
def delete_post(post_id):

    global community_posts

    original_length = len(community_posts)

    community_posts = [
        post for post in community_posts
        if post["id"] != post_id
    ]

    if len(community_posts) == original_length:
        return jsonify({
            "success": False,
            "message": "Post not found."
        }), 404

    return jsonify({
        "success": True,
        "message": "Post deleted successfully."
    })


# ============================================================
# COMMUNITY HEALTH CHECK
# ============================================================

@community_api.route("/health", methods=["GET"])
def community_health():

    return jsonify({
        "success": True,
        "message": "PawCare AI Community API is working.",
        "posts_count": len(community_posts)
    })