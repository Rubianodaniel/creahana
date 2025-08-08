class UserNotFoundException(Exception):
    def __init__(self, user_id: int):
        self.user_id = user_id
        super().__init__(f"User with ID {user_id} not found")


class DuplicateEmailException(Exception):
    def __init__(self, email: str):
        self.email = email
        super().__init__(f"User with email '{email}' already exists")


class DuplicateUsernameException(Exception):
    def __init__(self, username: str):
        self.username = username
        super().__init__(f"User with username '{username}' already exists")
