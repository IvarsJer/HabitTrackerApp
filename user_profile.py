class UserProfile:
    def __init__(self, username="User", avatar_path="default_avatar.png", level=1, exp=0, max_exp=100):
        self.username = username
        self.avatar_path = avatar_path
        self.level = level
        self.exp = exp
        self.max_exp = max_exp

    def update_username(self, new_username):
        self.username = new_username

    def update_avatar(self, new_avatar_path):
        self.avatar_path = new_avatar_path
