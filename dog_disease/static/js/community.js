// ============================================================
// PAWCARE AI COMMUNITY JAVASCRIPT
// ============================================================


// ================= CHARACTER COUNTERS =================

document.addEventListener("DOMContentLoaded", function () {

    const title = document.getElementById("title");
    const titleCounter = document.getElementById("titleCounter");

    if (title && titleCounter) {

        function updateTitleCounter() {

            titleCounter.textContent =
                `${title.value.length} / 200`;

        }

        title.addEventListener(
            "input",
            updateTitleCounter
        );

        updateTitleCounter();
    }


    const content = document.getElementById("content");
    const contentCounter = document.getElementById("contentCounter");

    if (content && contentCounter) {

        function updateContentCounter() {

            contentCounter.textContent =
                `${content.value.length} / 5000`;

        }

        content.addEventListener(
            "input",
            updateContentCounter
        );

        updateContentCounter();
    }


    const commentInput =
        document.getElementById("commentInput");

    const commentCounter =
        document.getElementById("commentCounter");

    if (commentInput && commentCounter) {

        function updateCommentCounter() {

            commentCounter.textContent =
                `${commentInput.value.length} / 2000`;

        }

        commentInput.addEventListener(
            "input",
            updateCommentCounter
        );

        updateCommentCounter();
    }


    // ================= COMMENT FORM =================

    const commentForm =
        document.getElementById("commentForm");

    if (commentForm) {

        commentForm.addEventListener(
            "submit",
            function (event) {

                event.preventDefault();

                const content =
                    commentInput.value.trim();

                if (!content) {

                    alert(
                        "Please write a comment."
                    );

                    return;
                }

                /*
                 * Comment API will be connected
                 * after we create the backend
                 * comment routes.
                 */

                alert(
                    "Comment feature will be connected next."
                );

            }
        );

    }

});


// ================= DELETE CONFIRMATION =================

function confirmDelete() {

    return confirm(
        "Are you sure you want to delete this post?"
    );

}


// ================= LIKE =================

function likePost(postId) {

    /*
     * This function will be connected to:
     *
     * POST /community/post/<post_id>/like
     *
     * after the CommunityLike model
     * and backend route are created.
     */

    alert(
        "Like system will be connected next."
    );

}