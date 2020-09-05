from . import model


class Redditor(model.Model):

    def __init__(self):
        # TODO when created, add to db?
        pass

    # TODO is this method needed?
    def get(self):
        # Lazy load?
        pass

    # TODO is this method needed?
    def save(self):
        pass

    def add_points(self, points):
        pass

    def remove_points(self, points):
        pass

    def _update_points(self, points_modifier):
        pass

    # def get_points(self):
    def points(self):
        pass

    # def get_points_modifier(self):
    def points_modifier(self):
        pass

    # TODO use properties for these instead?

    # @property
    # def points(self):
    #     pass

    # @points.setter
    # def points(self, value):
    #     pass

    # @property
    # def points_modifier(self):
    #     pass

