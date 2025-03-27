import re
from flask import Flask, jsonify, render_template, redirect, url_for, flash,abort,request
from flask_bootstrap import Bootstrap5
from flask_ckeditor import CKEditor, CKEditorField
from datetime import date
import logging
from models import Comment, User, db, BlogPost
from forms import RegisterForm, LoginForm, CreatePostForm, CommentForm  
from flask_login import LoginManager, login_user, current_user, logout_user, login_required
from functools import wraps
import hashlib


app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
bootstrap = Bootstrap5(app)
ckeditor = CKEditor(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///C:/Users/user/Documents/Programming/Flask/BLOG_CAPSTONE_PROJECT/instance/posts.db'
db.init_app(app)


# gravatar
def gravatar_url(email, size=40, rating='g', default='retro'):
    email_hash = hashlib.md5(email.lower().encode('utf-8')).hexdigest()
    return f"https://www.gravatar.com/avatar/{email_hash}?s={size}&d={default}&r={rating}"

# Register gravatar_url as a global template function
app.jinja_env.globals['gravatar_url'] = gravatar_url


with app.app_context():
    db.create_all()

# Initialize Flask-Login
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# User loader callback
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Admin-only decorator
def admin_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.id != 1:
            return abort(403)
        return f(*args, **kwargs)
    return decorated_function

@app.route('/register', methods=["POST", "GET"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        # Check if the user already exists
        existing_user = User.query.filter_by(email=form.email.data).first()
        if existing_user:
            flash('Email already registered. Please log in or use a different email.', 'danger')
            return redirect(url_for('login'))   

        # Create a new user
        new_user = User(
            email=form.email.data,
            name=form.name.data,
        )
        new_user.set_password(form.password.data)

        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for("login"))
    
    else:
        print(form.errors)
    return render_template("register.html", form=form)

@app.route('/login', methods=["POST", "GET"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            if user.check_password(form.password.data):
                login_user(user)
                return redirect(url_for("get_all_posts"))
            else:
                flash("Password incorrect, please try again.", 'danger')
        else:
            flash("Email does not exist, please register or try another email.", 'danger')
            redirect(url_for("register"))

    return render_template("login.html", form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for("get_all_posts"))

@app.route('/')
def get_all_posts():
    result = db.session.execute(db.select(BlogPost))
    posts = result.scalars().all()

    return render_template("index.html", all_posts=posts)
    # return jsonify(error={"Not Found":"Sorry, no posts in the database."}, posts=posts)

@app.route('/post/<int:post_id>', methods=['GET','POST'])
def show_post(post_id):
    requested_post = db.get_or_404(BlogPost, post_id)
    comment_form = CommentForm()
    if requested_post:
        if request.method == 'POST':
            app.logger.info(f"Received POST request for post_id {post_id}")
            if  comment_form.validate_on_submit():
                if not current_user.is_authenticated:
                    flash("You need to log in or register to comment.", "warning")
                    return redirect(url_for("login"))
                
                app.logger.info(f"Form validated with data: {comment_form.comment.data}")
                new_comment = Comment(
                    text=comment_form.comment.data,
                    comment_author=current_user,
                    parent_post_id=post_id
                )
                db.session.add(new_comment)
                db.session.commit()
                app.logger.info("New comment saved to the database!")
                return redirect(url_for("show_post", post_id=post_id, ), 302)
            else:
                app.logger.error("Form validation failed.")
                return redirect(url_for("show_post", post_id=post_id))


        return render_template("post.html", post=requested_post, form=comment_form, current_user=current_user), 200
    return jsonify(error={"Not Found": "Sorry, the post with that id was not found in the database."})


@app.route('/new-post', methods=["GET", "POST"])
@login_required
@admin_only
def add_new_post():
    form = CreatePostForm()
    if form.validate_on_submit():
        try:
            # Retrieve the User instance by ID (or another unique field)
            author = User.query.get(current_user.id)

            new_post = BlogPost(
                title=form.title.data,
                subtitle=form.subtitle.data,
                body=form.body.data,
                img_url=form.img_url.data,
                author=author,  # Assign the User instance here.
                date=date.today().strftime("%B %d, %Y")
            )
            db.session.add(new_post)
            db.session.commit()
            app.logger.info("New post saved to the database!")
            return redirect(url_for("get_all_posts"))
            
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Error saving post to the database: {e}", exc_info=True)

    else:
        logging.error("Failed to submit the form. Please check your inputs and try")
        flash("Failed to submit the form. Please check your inputs and try again.", "error")
    return render_template("make-post.html", form=form)



@app.route('/edit-post/<int:post_id>', methods=["GET", "POST"])
@login_required
@admin_only
def edit_post(post_id):
    post = db.get_or_404(BlogPost, post_id)
    form = CreatePostForm(
        title=post.title,
        subtitle=post.subtitle,
        img_url=post.img_url,
        body=post.body
    )
    if form.validate_on_submit():
        try:
            # Retrieve the current User instance for the `author` field
            author = User.query.get(current_user.id)

            post.title = form.title.data
            post.subtitle = form.subtitle.data
            post.author = author  # Assign the User instance here.
            post.img_url = form.img_url.data
            post.body = form.body.data
            db.session.commit()
            app.logger.info(f"Post with id {post_id} updated successfully!")
            return redirect(url_for("get_all_posts"))
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Error updating post with id {post_id}: {e}", exc_info=True)
            raise

    return render_template("make-post.html", form=form, is_edit=True, post=post)


@app.route('/delete/<int:post_id>')
@login_required
@admin_only
def delete(post_id):
    post = db.get_or_404(BlogPost, post_id)
    db.session.delete(post)
    db.session.commit()
    app.logger.info(f"Post with id {post_id} deleted successfully!")
    return redirect(url_for("get_all_posts"), post=post)


@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/contact")
def contact():
    return render_template("contact.html")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

if __name__ == "__main__":
    app.run(debug=True, port=5003)