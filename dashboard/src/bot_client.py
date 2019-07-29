import requests
from time import sleep, time


class HouseCatClient:
    """
    This class will be used to get the list of all guilds the
    bot is in. Required for the dashboard.
    TODO cache in database
    """
    def __init__(self, token):
        self.token = token
        self.cached_guilds = []
        self.next_reset = 0

    @staticmethod
    def _can_manage_messages(permissions):
        return bool((permissions >> 13) & 1)

    @staticmethod
    def _is_moderator(permissions):
        return bool((permissions >> 4) & 1)

    def get_common_guilds_to_manage(self, user_guilds: list):
        list_user_guilds = [x['id'] for x in user_guilds]
        common_guilds = self._get_common_guilds(list_user_guilds)
        return [x for x in user_guilds if x['id'] in common_guilds and self._is_moderator(x['permissions'])]

    def get_common_guilds_to_create_template(self, user_guilds: list):
        list_user_guilds = [x['id'] for x in user_guilds]
        common_guilds = self._get_common_guilds(list_user_guilds)
        return [x for x in user_guilds if x['id'] in common_guilds and self._can_manage_messages(x['permissions'])]

    def get_common_guilds(self, user_guilds: list):
        list_user_guilds = [x['id'] for x in user_guilds]
        common_guilds = self._get_common_guilds(list_user_guilds)
        return [x for x in user_guilds if x['id'] in common_guilds]

    def _get_common_guilds(self, user_guilds: list):
        return list(set(self.guilds()).intersection(user_guilds))

    def guilds(self):
        if time() < self.next_reset:
            return self.cached_guilds
        response = self._get_guilds()
        if response.status_code == 200:
            guilds = [x['id'] for x in response.json()]
            self.cached_guilds = guilds
            return guilds
        while response.status_code == 429:
            millis_to_sleep = response.headers.get("Retry-After")
            sleep(int(millis_to_sleep)/1000)
            return self.guilds()

    def _get_guilds(self):
        headers = {"Authorization": "Bot " + self.token}
        response = requests.get('https://discordapp.com/api/users/@me/guilds', headers=headers)
        print(response.headers)
        self.next_reset = int(response.headers.get("X-RateLimit-Reset"))
        return response
