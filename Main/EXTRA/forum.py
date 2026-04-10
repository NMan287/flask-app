from flask import  Blueprint, request, jsonify, session
from EXTRA.tables import db, user_posts, user_comments

forum_bp = Blueprint('forum', __name__, template_folder='templates')


@forum_bp.route("/addPost", methods=["POST"])
def add_post():
    if "user_id" not in session: # checks whether the user is loggedd in
        return jsonify({"message": "not logged in"})
    data = request.get_json()
    post_contents = data.get("post_contents")  # receives the data sent and assigns to a variable
    post_image = data.get("post_image")
    subject = data.get("subject")

    if not post_contents:
        return jsonify({"message": "Please enter something"})# error when user does not enter message
    try:
        post = user_posts(
            user_id=session["user_id"],
            post_contents=post_contents,
            post_image=post_image,
            subject= subject
        )
        db.session.add(post)
        db.session.commit()
        return jsonify({"message": "Post added"})
    except Exception as e:
        db.session.rollback() # rolls back session if error occured
        print("error with database:", e)
        return jsonify({"message": "Post did not get added"})


@forum_bp.route("/get_posts", methods=["GET"])
def get_posts():
    try:
        subject = request.args.get("subject")
        query = user_posts.query
        if subject:
            query = query.filter_by(subject=subject)
        posts = query.order_by(user_posts.post_id.desc()).all()
        # list of posts
        post_list = []
        for post in posts:
            post_list.append({
                "id": post.post_id,
                "user_id": post.user_id,
                "username": post.user.username,
                "post_contents": post.post_contents,
                "post_image": post.post_image
            })

        return jsonify(post_list)
    except Exception as e:
        print("error fetching posts:", e)
        return jsonify({"message": "error", "error": str(e)})


@forum_bp.route("/add_comment", methods=["POST"])
def add_comment():
    if "user_id" not in session:
        return jsonify({"message": "You are not logged in"})
    data = request.get_json()
    post_id = data.get("post_id")
    body = data.get("body")
    if not body:
        return jsonify({"message:" "empty comment"})
    try:
        comment = user_comments(post_id=post_id, user_id=session["user_id"], body=body)
        db.session.add(comment)
        db.session.commit()
        return jsonify({"message": "Comment added"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "error", "error": str(e)}), 500

@forum_bp.route("/get_comments", methods=["GET"])
def get_comments():
    post_id = request.args.get("post_id") # makes argument for postid
    comments = user_comments.query.filter_by(post_id=post_id).all()
    comment_list = []
    for c in comments:
        comment_list.append({
            "comment_id": c.comment_id,
            "user_id": c.user_id,
            "username": c.user.username,
            "body": c.body
        })

    return jsonify(comment_list)
    
