import json
import os


DATABASE_PATH = os.path.join('hexlet_flask_example', 'users.json')


class Database:
    def __init__(self, cookies: dict) -> None:
        data = cookies.get('data', '{}')
        schema = json.loads(data)
        self.largest_id = schema.get('largest_id', 1)
        self.users = schema.get('users', [])
    
    def filter(self, key, value):
        result = (user for user in self.users if user[key] == value)
        return result
    
    def find(self, key, value):
        for user in self.users:
            if user[key] == value:
                return user
    
    def save(self, user):
        if not user.get('id'):
            user['id'] = self.largest_id + 1
            self.largest_id += 1
            self.users.append(user)

    def content(self):
        return self.users
    
    def delete(self, key, value):
        self.users = list(filter(lambda user: user[key] != value, self.users))

    def set_cookies(self, response):
        schema = {
            'largest_id': self.largest_id,
            'users': self.users
        }
        response.set_cookie('data', json.dumps(schema))
