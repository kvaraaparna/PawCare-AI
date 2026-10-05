from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session
)

from database import db
from community.models import(
    CommunityPost,
    CommunityComment, 
    CommunityLike, 
    CommunityReport
    )
from .service import (
    create_post,
    get_all_posts,
    get_post_by_id,
    get_posts_by_category,
    search_posts,
    update_post,
    delete_post
)


community_bp = Blueprint(
    "community",
    __name__,
    url_prefix="/community"
)


# ============================================================
# COMMUNITY HOME
# ============================================================

@community_bp.route("/", methods=["GET"])
def community_home():

    category = request.args.get("category")
    search = request.args.get("search")

    if search:
        posts = search_posts(
            CommunityPost,
            search
        )

    elif category:
        posts = get_posts_by_category(
            CommunityPost,
            category
        )

    else:
        posts = get_all_posts(
            CommunityPost
        )

    return render_template(
        "community/community.html",
        posts=posts,
        selected_category=category,
        search_query=search
    )


# ============================================================
# CREATE POST
# ============================================================

@community_bp.route("/create", methods=["GET", "POST"])
def create_community_post():

    # User must be logged in
    if "user_id" not in session:
        flash("Please login to create a community post.", "warning")
        return redirect(url_for("login"))

    if request.method == "POST":

        title = request.form.get("title", "").strip()
        content = request.form.get("content", "").strip()
        category = request.form.get("category", "").strip()

        # Validation
        if not title:
            flash("Please enter a post title.", "danger")
            return render_template(
                "community/create_post.html"
            )

        if not content:
            flash("Please enter your post content.", "danger")
            return render_template(
                "community/create_post.html"
            )

        if not category:
            flash("Please select a category.", "danger")
            return render_template(
                "community/create_post.html"
            )

        post = create_post(
            db=db,
            CommunityPost=CommunityPost,
            user_id=session["user_id"],
            title=title,
            content=content,
            category=category
        )

        flash("Your post was created successfully!", "success")

        return redirect(
            url_for(
                "community.view_post",
                post_id=post.id
            )
        )

    return render_template(
        "community/create_post.html"
    )


# ============================================================
# VIEW SINGLE POST
# ============================================================

@community_bp.route("/post/<int:post_id>", methods=["GET"])
def view_post(post_id):

    post = get_post_by_id(
        CommunityPost,
        post_id
    )

    if post is None:
        flash("Post not found.", "danger")
        return redirect(
            url_for("community.community_home")
        )

    return render_template(
        "community/post_detail.html",
        post=post
    )


# ============================================================
# EDIT POST
# ============================================================

@community_bp.route(
    "/post/<int:post_id>/edit",
    methods=["GET", "POST"]
)
def edit_post(post_id):

    if "user_id" not in session:
        flash("Please login first.", "warning")
        return redirect(url_for("login"))

    post = get_post_by_id(
        CommunityPost,
        post_id
    )

    if post is None:
        flash("Post not found.", "danger")
        return redirect(
            url_for("community.community_home")
        )

    # Check ownership
    if post.user_id != session["user_id"]:
        flash(
            "You are not authorized to edit this post.",
            "danger"
        )

        return redirect(
            url_for(
                "community.view_post",
                post_id=post_id
            )
        )

    if request.method == "POST":

        title = request.form.get("title", "").strip()
        content = request.form.get("content", "").strip()
        category = request.form.get("category", "").strip()

        updated_post, error = update_post(
            db=db,
            CommunityPost=CommunityPost,
            post_id=post_id,
            user_id=session["user_id"],
            title=title,
            content=content,
            category=category
        )

        if error:
            flash(error, "danger")

            return redirect(
                url_for(
                    "community.view_post",
                    post_id=post_id
                )
            )

        flash(
            "Post updated successfully!",
            "success"
        )

        return redirect(
            url_for(
                "community.view_post",
                post_id=updated_post.id
            )
        )

    return render_template(
        "community/create_post.html",
        post=post,
        edit_mode=True
    )


# ============================================================
# DELETE POST
# ============================================================

@community_bp.route(
    "/post/<int:post_id>/delete",
    methods=["POST"]
)
def delete_community_post(post_id):

    if "user_id" not in session:
        flash("Please login first.", "warning")
        return redirect(url_for("login"))

    success, error = delete_post(
        db=db,
        CommunityPost=CommunityPost,
        post_id=post_id,
        user_id=session["user_id"]
    )

    if not success:
        flash(error, "danger")

        return redirect(
            url_for(
                "community.view_post",
                post_id=post_id
            )
        )

    flash(
        "Post deleted successfully.",
        "success"
    )

    return redirect(
        url_for(
            "community.community_home"
        )
    )


# ============================================================
# MY POSTS
# ============================================================

@community_bp.route("/my-posts", methods=["GET"])
def my_posts():

    if "user_id" not in session:
        flash("Please login first.", "warning")
        return redirect(url_for("login"))

    posts = CommunityPost.query.filter_by(
        user_id=session["user_id"]
    ).order_by(
        CommunityPost.created_at.desc()
    ).all()

    return render_template(
        "community/my_posts.html",
        posts=posts
    )