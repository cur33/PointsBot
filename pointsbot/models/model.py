from ..data import database as db


class Model:

    def get(self):
        raise NotImplementedError

    def save(self):
        raise NotImplementedError

