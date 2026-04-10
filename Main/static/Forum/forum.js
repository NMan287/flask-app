document.addEventListener("DOMContentLoaded", function() {
    const subjects = ["General", "Maths", "Physics", "Chemistry", "Computing", "Other"];
    for (const subject of subjects) {
        load_posts(subject);
    }
});

async function submit_post(subject, input_id) {
    const post_content = document.getElementById(input_id).value;
    
    // Find the file input in the same InputBox
    const inputBox = document.getElementById(input_id).closest('.InputBox');
    const fileInput = inputBox.querySelector('.File');
    const file = fileInput.files[0];

    if (!post_content.trim() && !file) return;

    // Convert image to base64 if one was selected
    let post_image = null;
    if (file) {
        post_image = await new Promise((resolve) => {
            const reader = new FileReader();
            reader.onload = (e) => resolve(e.target.result); // gives "data:image/png;base64,..."
            reader.readAsDataURL(file);
        });
    }

    const response = await fetch("/addPost", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            post_contents: post_content,
            post_image: post_image,  // now sends actual base64 string
            subject: subject
        })
    });

    const result = await response.json();

    if (response.ok) {
        document.getElementById(input_id).value = "";
        fileInput.value = "";  // clear the file input too
        load_posts(subject);
    } else {
        alert(result.message || "Could not post");
    }
}


const subjectContainers = {
    "General": "generalPosts",
    "Maths": "mathsPosts",
    "Physics": "physicsPosts",
    "Chemistry": "chemistryPosts",
    "Computing": "computingPosts",
    "Other": "otherPosts"}
async function load_posts(subject) {
    const response = await fetch(`/get_posts?subject=${subject}`);
    const container = document.getElementById(subjectContainers[subject]);
    console.log(subject, subjectContainers[subject], container);
    const data = await response.json();

    if (!response.ok) {
        console.log("Error loading posts:", data.error);
        return;
    }


    container.innerHTML = data.map(post => `
    <div class="PostDiv" id="post-${post.id}">
        <span class="postAuthor">Posted by: ${post.username}</span>
        <p>${post.post_contents}</p>
        ${post.post_image ? `<img src="${post.post_image}">` : ""}
        <div class="commentsSection">
            <h3 style="font-family:Nunito;">Replies<h3>
            <div class="commentsList" id="comments-${post.id}"></div>
            <input class="commentInput" id="commentInput-${post.id}" placeholder="Write a comment...">
            <button onclick="submit_comment(${post.id}, '${subject}')">Reply</button>
        </div>
    </div>
`).join("");
        for (const post of data) {
            load_comments(post.id);
    }
}

async function load_comments(post_id) {
    const response = await fetch(`/get_comments?post_id=${post_id}`);
    const data = await response.json();
    const container = document.getElementById(`comments-${post_id}`);
    if (!container) return;
    container.innerHTML = data.map(c => `
        <hr>
        <div class="CommentDiv">
            <span class="commentAuthor">${c.username}</span>  <!-- make sure this line is here -->
            <p>${c.body}</p>
        </div>
        <hr>
    `).join("");
}

async function submit_comment(post_id, subject) {
    const input = document.getElementById(`commentInput-${post_id}`);
    const body = input.value.trim();
    if (!body) return;
    const response = await fetch("/add_comment", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ post_id, body })
    });
    if (response.ok) {
        input.value = "";
        load_comments(post_id);
    } else {
        alert("Could not post comment");
    }
}