document.addEventListener("DOMContentLoaded", function () {

    /* =================================================
       IMAGE PREVIEW
    ================================================= */

    const dogImage = document.getElementById("dogImage");
    const uploadPreview = document.getElementById("uploadPreview");

    dogImage.addEventListener("change", function () {

        const file = this.files[0];

        if (!file) {
            return;
        }

        if (!file.type.startsWith("image/")) {
            alert("Please select an image.");
            return;
        }

        const reader = new FileReader();

        reader.onload = function (event) {

            uploadPreview.innerHTML = `
                <img src="${event.target.result}" alt="Dog image preview">
            `;

        };

        reader.readAsDataURL(file);

    });



    /* =================================================
       PUBLISH POST
    ================================================= */

    const publishBtn = document.getElementById("publishBtn");

    publishBtn.addEventListener("click", function () {

        const disease =
            document.getElementById("diseaseName").value.trim();

        const symptoms =
            document.getElementById("symptoms").value.trim();

        const suggestion =
            document.getElementById("suggestion").value.trim();


        /* VALIDATION */

        if (!disease) {
            alert("Please enter the disease name.");
            return;
        }

        if (!symptoms) {
            alert("Please describe the symptoms.");
            return;
        }

        if (!suggestion) {
            alert("Please enter your question or suggestion.");
            return;
        }


        /* IMAGE */

        let imageHTML = "";

        if (dogImage.files.length > 0) {

            const file = dogImage.files[0];

            const imageURL =
                URL.createObjectURL(file);

            imageHTML = `
                <div class="post-image">
                    <img src="${imageURL}" alt="Dog">
                </div>
            `;

        }


        /* CREATE POST */

        const post = document.createElement("article");

        post.className = "post-card new-post";


        post.innerHTML = `

            <div class="post-user">

                <div class="post-avatar">
                    <i class="fa-solid fa-user"></i>
                </div>

                <div>

                    <h3>Aparna</h3>

                    <span>Just now</span>

                </div>

            </div>


            <div class="post-body">

                ${imageHTML}

                <div class="post-information">

                    <h3>
                        Disease Name:
                        <strong>${escapeHTML(disease)}</strong>
                    </h3>

                    <h3>Symptoms:</h3>

                    <p>
                        ${escapeHTML(symptoms)}
                    </p>

                    <h3>My Question / Suggestion:</h3>

                    <p>
                        ${escapeHTML(suggestion)}
                    </p>

                </div>

            </div>


            <div class="post-actions">

                <button class="like-btn">

                    <i class="fa-regular fa-heart"></i>

                    <span>0</span>

                </button>


                <button class="comment-count">

                    <i class="fa-regular fa-comment"></i>

                    <span>0</span>

                </button>

            </div>


            <div class="reply-section">

                <div class="reply-avatar">

                    <i class="fa-solid fa-user"></i>

                </div>


                <input
                    type="text"
                    class="reply-input"
                    placeholder="Write your response or suggestion..."
                >


                <button class="reply-btn">
                    Reply
                </button>

            </div>

        `;


        const postsContainer =
            document.getElementById("postsContainer");


        postsContainer.prepend(post);


        /* CLEAR FORM */

        document.getElementById("diseaseName").value = "";

        document.getElementById("symptoms").value = "";

        document.getElementById("suggestion").value = "";

        dogImage.value = "";

        uploadPreview.innerHTML = `

            <i class="fa-regular fa-image"></i>

            <p>Upload Image</p>

            <span>of your dog</span>

        `;


        alert("Your post has been published!");

    });



    /* =================================================
       LIKE BUTTONS
    ================================================= */

    document.addEventListener("click", function (event) {

        const likeButton =
            event.target.closest(".like-btn");

        if (!likeButton) {
            return;
        }

        const icon =
            likeButton.querySelector("i");

        const count =
            likeButton.querySelector("span");


        let currentCount =
            parseInt(count.textContent) || 0;


        if (likeButton.classList.contains("liked")) {

            likeButton.classList.remove("liked");

            icon.className = "fa-regular fa-heart";

            currentCount--;

        } else {

            likeButton.classList.add("liked");

            icon.className = "fa-solid fa-heart";

            currentCount++;

        }


        count.textContent = currentCount;

    });



    /* =================================================
       REPLY
    ================================================= */

    document.addEventListener("click", function (event) {

        const replyButton =
            event.target.closest(".reply-btn");

        if (!replyButton) {
            return;
        }


        const replySection =
            replyButton.closest(".reply-section");

        const input =
            replySection.querySelector(".reply-input");


        const replyText =
            input.value.trim();


        if (!replyText) {

            alert("Please write a response.");

            return;

        }


        /* FIND POST */

        const postCard =
            replyButton.closest(".post-card");


        /* CREATE RESPONSE */

        const response =
            document.createElement("div");

        response.className = "response";


        response.innerHTML = `

            <div class="response-avatar">

                <i class="fa-solid fa-user"></i>

            </div>


            <div class="response-content">

                <div class="response-header">

                    <strong>Aparna</strong>

                    <span>Just now</span>

                </div>


                <p>

                    ${escapeHTML(replyText)}

                </p>


                <button class="response-like">

                    <i class="fa-regular fa-heart"></i>

                    0

                </button>

            </div>

        `;


        /* Insert response before reply box */

        postCard.insertBefore(
            response,
            replySection
        );


        /* Clear */

        input.value = "";


        /* Update comment count */

        const commentCount =
            postCard.querySelector(".comment-count span");


        if (commentCount) {

            let count =
                parseInt(commentCount.textContent) || 0;

            commentCount.textContent = count + 1;

        }

    });



    /* =================================================
       RESPONSE LIKE
    ================================================= */

    document.addEventListener("click", function (event) {

        const button =
            event.target.closest(".response-like");

        if (!button) {
            return;
        }


        const icon =
            button.querySelector("i");

        const elements =
            button.childNodes;


        let count = parseInt(
            [...elements]
                .find(node => node.nodeType === 3 &&
                    node.textContent.trim()
                )?.textContent
        ) || 0;


        if (button.classList.contains("liked")) {

            button.classList.remove("liked");

            icon.className =
                "fa-regular fa-heart";

            count--;

        } else {

            button.classList.add("liked");

            icon.className =
                "fa-solid fa-heart";

            count++;

        }


        button.innerHTML = `

            <i class="${
                button.classList.contains("liked")
                ? "fa-solid fa-heart"
                : "fa-regular fa-heart"
            }"></i>

            ${count}

        `;

    });



    /* =================================================
       HTML ESCAPE
    ================================================= */

    function escapeHTML(value) {

        const div =
            document.createElement("div");

        div.textContent = value;

        return div.innerHTML;

    }

});