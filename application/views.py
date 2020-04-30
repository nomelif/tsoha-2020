from application import app
from flask import render_template, request, redirect, url_for
from application.account import Account
from application.post import Post, submit_post, Vote
from flask_login import login_required, current_user
import bleach

@app.route("/")
def index():
    if current_user.is_authenticated:
        account = Account.query.filter_by(id=current_user.get_id()).first()
        tags = []
        query = request.args.get("tag")
        if query != None:
            for tag in query.split():
                tag = tag.lower()
                if not tag.startswith("#"):
                    tags.append("#" + tag)
                else:
                    tags.append(tag)

        # Remove HTML 

        posts = Post.get_displayable_posts(tags)
        for post in posts:
            post["text"] = bleach.clean(post["text"])

        return render_template("index.html", user_name=account.user_name, account_id=account.id, posts=posts, title="Värkki", index=True)
    else:
        return render_template("index-unlogged.html", title="Värkki (kirjautumaton)")
