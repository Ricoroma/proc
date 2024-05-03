from tgbot.services.database import User, Session


class LocalText:
    def __init__(self, user_id):
        lang = get_language(user_id)
        self.lang = lang


class LocalButton:

    def __init__(self, user_id):
        lang = get_language(user_id)


def get_language(user_id):
    with Session() as db_session:
        user: User = db_session.query(User).filter(User.id == user_id).one()
    return user.lang
