class LobbyManager:
    def __init__(self):
        self.lobbies = {}

    def create_lobby(self, host):
        import random, string
        code = ''.join(random.choices(string.ascii_uppercase, k=4))
        self.lobbies[code] = [host]
        return code

    def join_lobby(self, code, user):
        if code in self.lobbies and len(self.lobbies[code]) < 2:
            self.lobbies[code].append(user)
            return True
        return False

    def get_players(self, code):
        return self.lobbies.get(code, [])