from sqlalchemy.orm import validates
from sqlalchemy.ext.hybrid import hybrid_property
from marshmallow import Schema, fields

from config import db, bcrypt


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    _password_hash = db.Column(db.String, default="")
    image_url = db.Column(db.String)
    bio = db.Column(db.String)

    recipes = db.relationship("Recipe", backref="user", cascade="all, delete-orphan")

    @hybrid_property
    def password_hash(self):
        raise AttributeError("Password hashes may not be viewed.")

    @password_hash.setter
    def password_hash(self, password):
        password_hash = bcrypt.generate_password_hash(password)
        self._password_hash = password_hash.decode("utf-8")

    def authenticate(self, password):
        return bcrypt.check_password_hash(self._password_hash, password)

    @validates("username")
    def validate_username(self, key, username):

        if not username:
            raise ValueError("Username is required")

        return username


class Recipe(db.Model):
    __tablename__ = "recipes"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    instructions = db.Column(db.String, nullable=False)
    minutes_to_complete = db.Column(db.Integer)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))

    @validates("title")
    def validate_title(self, key, title):

        if not title:
            raise ValueError("Title is required")

        return title

    @validates("instructions")
    def validate_instructions(self, key, instructions):

        if not instructions:
            raise ValueError("Instructions are required")

        if len(instructions) < 50:
            raise ValueError("Instructions must be at least 50 characters long")

        return instructions


class UserSchema(Schema):

    id = fields.Int()
    username = fields.Str()
    image_url = fields.Str()
    bio = fields.Str()

    recipes = fields.List(
        fields.Nested(lambda: RecipeSchema(exclude=("user",)))
    )


class RecipeSchema(Schema):

    id = fields.Int()
    title = fields.Str()
    instructions = fields.Str()
    minutes_to_complete = fields.Int()

    user = fields.Nested(
        UserSchema(exclude=("recipes",))
    )