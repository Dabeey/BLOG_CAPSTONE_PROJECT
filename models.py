from sqlalchemy import Column, Integer, String,Text
from flask_login import UserMixin
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash


# CONFIGURE DATABASE
class Base(DeclarativeBase):
    pass
db = SQLAlchemy(model_class=Base)


# CREATE TABLE

class BlogPost(db.Model):
    __tablename__ = 'blog_post'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(250), nullable=False)
    subtitle: Mapped[str] = mapped_column(String(250), nullable=False)
    date: Mapped[str] = mapped_column(String(250), nullable=False)
    body: Mapped[str] = mapped_column(String(250), nullable=False)
    img_url: Mapped[str] = mapped_column(String(250), nullable=False)

    # child relationship with user
    author_id:Mapped[int]=mapped_column(Integer,db.ForeignKey('user.id'),nullable=False)
    author = relationship("User", back_populates="posts")    # create reference to the user object
    
    # parent elationship with comment
    comments = relationship('Comment', back_populates='parent_post')
    


class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(100), unique=True)
    password: Mapped[str] = mapped_column(String(100))
    name: Mapped[str] = mapped_column(String(1000))

    # parent relationship with blogpost
    posts = relationship("BlogPost", back_populates="author")
    
    # parent relationship with comment
    comments = relationship("Comment", back_populates="comment_author")


    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)
    


class Comment(db.Model):
    __tablename__ = "comments"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    
    # child relationship with user
    author_id: Mapped[int] = mapped_column(Integer, db.ForeignKey("user.id"))
    comment_author = relationship("User", back_populates="comments")

    # child relationship with blogpost
    parent_post_id: Mapped[int] = mapped_column(Integer, db.ForeignKey("blog_post.id"))
    parent_post = relationship("BlogPost", back_populates="comments")


    def __repr__(self):
        return f'Comment: {self.text}'