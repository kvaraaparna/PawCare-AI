from flask import (
    Blueprint,
    jsonify,
    request,
    session
)

from database import db

from community.models import (
    CommunityPost,
    CommunityLike,
    CommunityReport
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
# GET ALL POSTS
# ============================================================

@community_api.route(
    "/posts",
    methods=["GET"]
)
def get_posts():

    try:

        posts = CommunityPost.query.order_by(
            CommunityPost.created_at.desc()
        ).all()

        result = []

        for post in posts:

            result.append({

                "id": post.id,

                "user_id": post.user_id,

                "title": post.title,

                "content": post.content,

                "category": post.category,

                "disease": post.category,

                "user_name": (
                    getattr(
                        post,
                        "user_name",
                        f"User {post.user_id}"
                    )
                ),

                "created_at": (
                    post.created_at.isoformat()
                    if post.created_at
                    else None
                ),

                "updated_at": (
                    post.updated_at.isoformat()
                    if post.updated_at
                    else None
                ),

                "comments": []

            })

        return jsonify({

            "success": True,

            "posts": result

        }), 200

    except Exception as e:

        print(
            "GET POSTS API ERROR:",
            e
        )

        return jsonify({

            "success": False,

            "message":
                "Unable to load community posts.",

            "error": str(e)

        }), 500


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

        db.session.delete(
            existing_like
        )

        liked = False

    else:

        new_like = CommunityLike(

            post_id=post_id,

            user_id=session["user_id"]

        )

        db.session.add(
            new_like
        )

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

    post = CommunityPost.query.get(
        post_id
    )

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

    post = CommunityPost.query.get(
        post_id
    )

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

            "message":
                "Please select a reason."

        }), 400

    existing_report = CommunityReport.query.filter_by(

        post_id=post_id,

        user_id=session["user_id"]

    ).first()

    if existing_report:

        return jsonify({

            "success": False,

            "message":
                "You have already reported this post."

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

        "message":
            "Report submitted successfully."

    }), 201

from flask import (
    Blueprint,
    jsonify,
    request,
    session
)

from database import db

from community.models import (
    CommunityPost,
    CommunityComment,
    CommunityLike,
    CommunityReport
)


community_api = Blueprint(
    "community_api",
    __name__,
    url_prefix="/api/community"
)


# ============================================================
# GET ALL POSTS
# ============================================================

@community_api.route("/posts", methods=["GET"])
def get_posts():

    try:

        posts = CommunityPost.query.order_by(
            CommunityPost.created_at.desc()
        ).all()

        result = []

        for post in posts:

            comments = []

            for comment in post.comments:

                comments.append({
                    "id": comment.id,
                    "user_id": comment.user_id,
                    "content": comment.content,
                    "created_at": (
                        comment.created_at.isoformat()
                        if comment.created_at
                        else None
                    )
                })

            like_count = CommunityLike.query.filter_by(
                post_id=post.id
            ).count()

            user_liked = False

            if "user_id" in session:

                user_liked = (
                    CommunityLike.query.filter_by(
                        post_id=post.id,
                        user_id=session["user_id"]
                    ).first()
                    is not None
                )

            result.append({

                "id": post.id,

                "user_id": post.user_id,

                "title": post.title,

                "content": post.content,

                "category": post.category,

                "disease": post.category,

                "user_name": f"User {post.user_id}",

                "created_at": (
                    post.created_at.isoformat()
                    if post.created_at
                    else None
                ),

                "updated_at": (
                    post.updated_at.isoformat()
                    if post.updated_at
                    else None
                ),

                "like_count": like_count,

                "liked": user_liked,

                "comments": comments
            })

        return jsonify({
            "success": True,
            "posts": result
        }), 200

    except Exception as e:

        db.session.rollback()

        print(
            "GET POSTS API ERROR:",
            e
        )

        return jsonify({
            "success": False,
            "message": "Unable to load community posts.",
            "error": str(e)
        }), 500


# ============================================================
# LIKE / UNLIKE
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

        db.session.delete(existing_like)

        liked = False

    else:

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
    }), 200





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
    }), 200
# ============================================================
# ADD COMMENT / SUGGESTION
# ============================================================

@community_api.route(
    "/post/<int:post_id>/comment",
    methods=["POST"]
)
def add_comment(post_id):

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

    data = request.get_json(silent=True) or {}

    content = str(
        data.get("content", "")
    ).strip()

    if not content:
        return jsonify({
            "success": False,
            "message": "Please enter a comment."
        }), 400

    if len(content) > 1000:
        return jsonify({
            "success": False,
            "message": "Comment is too long."
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
            "user_name": f"User {comment.user_id}",
            "content": comment.content,
            "created_at": (
                comment.created_at.isoformat()
                if comment.created_at
                else None
            )
        }
    }), 201

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