import unittest

import praw
# from collections import namedtuple

import common
import context

import pointsbot.bot as bot

# Comment = namedtuple('Comment', [ 'is_root', 'is_submitter', 'parent', ])


def setUpModule():
    global REDDIT
    REDDIT = common.get_reddit_instance()


def tearDownModule():
    pass


# Might be a little too optimistic?
class TestMonitorComments(unittest.TestCase):
    pass


class TestMarksAsSolved(unittest.TestCase):

    #  @classmethod
    #  def setUpClass(cls):
        #  cls._default_comment_data = {
            #  'author': None,
            #  'body': '',
            #  'submission': None,
            #  'subreddit': None,
            #  'is_root': True,
            #  'is_submitter': False,
        #  }

    #  @classmethod
    #  def tearDownClass(cls):
        #  del cls._default_comment_data

    def setUp(self):
        #  data = dict(cls._default_comment_data)
        data = {
            'id': None,
            'author': None,
            'body': '',
            'submission': None,
            'subreddit': None,
            'is_root': True,
            'is_submitter': False,
        }
        self.comment = praw.models.Comment.parse(data, REDDIT)

    def tearDown(self):
        pass

    def test_basic_case(self):
        pass


class TestIsModComment(unittest.TestCase):
    pass


class TestIsFirstSolution(unittest.TestCase):
    pass


class TestFindSolver(unittest.TestCase):
    pass


if __name__ == '__main__':
    unittest.main()
