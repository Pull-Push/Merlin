from flask_app import app  # noqa: F401
from flask_app.config.mysqlconnection import connectToMySQL
from flask import flash, session
import re

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')


class User:
    def __init__(self, data):
        self.id = data['id']
        self.username = data['username']
        self.email = data['email']
        self.password = data['password']
        self.date_created = data['dateCreated']
        self.date_updated = data['dateUpdated']

    @classmethod
    def save_user(cls, data):
        query = """
            INSERT INTO users (username, email, password)
            VALUES (%(username)s, %(email)s, %(password)s)
        """
        return connectToMySQL('merlin_db').query_db(query, data)

    @classmethod
    def check_user(cls, data):
        query = "SELECT * FROM users WHERE email = %(email)s"
        results = connectToMySQL('merlin_db').query_db(query, data)
        if not results:
            return False
        return cls(results[0])

    @classmethod
    def get_by_id(cls, user_id):
        query = "SELECT * FROM users WHERE id = %(id)s"
        results = connectToMySQL('merlin_db').query_db(query, {'id': user_id})
        if not results:
            return None
        return cls(results[0])

    @staticmethod
    def validate(data):
        is_valid = True

        username = data.get('username', '').strip()
        if len(username) < 3:
            flash("Username must be at least 3 characters.", 'error')
            is_valid = False

        if not EMAIL_REGEX.match(data.get('email', '')):
            flash("Please enter a valid email address.", 'error')
            is_valid = False
        elif User.check_user(data):
            flash("An account with that email already exists.", 'error')
            is_valid = False

        password = data.get('password', '')
        if len(password) < 8:
            flash("Password must be at least 8 characters.", 'error')
            is_valid = False
        elif password != data.get('conf_pass', ''):
            flash("Passwords must match.", 'error')
            is_valid = False

        return is_valid
