from typing import Optional
from . import slack_client


class UserProfile:
    def __init__(self, *, user_id: str, display_name: Optional[str] = None):
        self.user_id = user_id
        self.display_name = display_name or user_id


class UserProfileProvider:
    def __init__(self):
        self.__store = {}

    def get(self, user_id: str) -> UserProfile:
        if user_id not in self.__store:
            display_name = None
            resp = slack_client.users_profile_get(user=user_id)
            profile = resp.get("profile")
            if profile:
                display_name = profile.get("display_name")
                if not display_name:
                    display_name = profile.get("real_name")

            self.__store[user_id] = UserProfile(user_id=user_id, display_name=display_name)

        return self.__store[user_id]


user_profile_provider = UserProfileProvider()
