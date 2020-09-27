import logging

import praw


class Bot:

    def __init__(self, reddit, subreddit, level_factory, reply_factory):
        self.reddit = reddit
        self.subreddit = subreddit
        self.level_factory = level_factory
        self.reply_factory = reply_factory

    def run(self):
        self._monitor_all_comments()

    # def monitor_all_submissions(self):
    #     pass
    
    def _monitor_all_comments(self):
        # Passing pause_after=0 will bypass the internal exponential delay, but have
        # to check if any comments are returned after each query
        for comm in self.subreddit.stream.comments(skip_existing=True, pause_after=0):
            if comm is None:
                continue
            if comm.author == self.reddit.user.me():
                logging.info('Comment was posted by this bot')
                continue
            # if comm.author.name == reddit.user.me().name:
            #     logging.info('Comment was posted by this bot name')
            #     continue

            logging.info('Found comment')
            logging.debug('Comment author: "%s"', comm.author.name)
            logging.debug('Comment text: "%s"', comm.body)

            if not self._marks_as_solved(comm):
                # Skip this "!solved" comment
                logging.info('Comment does not mark issue as solved')
                continue
            logging.info('Comment marks issue as solved')

            if self._is_mod_comment(comm):
                logging.info('Comment was submitted by mod')
            elif self._is_first_solution(comm):
                logging.info('Comment is the first to mark the issue as solved')
            else:
                logging.info('Comment is NOT the first to mark the issue as solved')
                continue
            self._log_solution_info(comm)

            solver = self._find_solver(comm)
            # TODO replace
            db.add_solution(comm.submission, comm.parent(), comm, solver)
            logging.info('Added point for user "%s"', solver.name)

            # TODO replace
            points = db.get_points(solver)
            logging.info('Total points for user "%s": %d', solver.name, points)
            # level_info = level.user_level_info(points, levels)
            level_info = self.level_factory(points)

            # Reply to the comment marking the submission as solved
            # reply_body = reply.make(solver,
            #                         points,
            #                         level_info,
            #                         feedback_url=cfg.feedback_url,
            #                         scoreboard_url=cfg.scoreboard_url)
            reply_body = self.reply_factory(solver, points, level_info)
            try:
                comm.reply(reply_body)
                logging.info('Replied to the comment')
                logging.debug('Reply body: %s', reply_body)
            except praw.exceptions.APIException as e:
                logging.error('Unable to reply to comment: %s', e)
                # TODO replace
                db.remove_solution(comm.submission, comm.parent(), comm, solver)
                logging.error('Removed point that was just awarded to user "%s"', solver.name)
                logging.error('Skipping comment')
                continue

            # Check if (non-mod) user flair should be updated to new level
            lvl = level_info.current
            if lvl and lvl.points == points:
                logging.info('User reached level: %s', lvl.name)
                if not self.subreddit.moderator(redditor=solver):
                    logging.info('User is not mod; setting flair')
                    logging.info('Flair text: %s', lvl.name)
                    logging.info('Flair template ID: %s', lvl.flair_template_id)
                    self.subreddit.flair.set(solver,
                                             text=lvl.name,
                                             flair_template_id=lvl.flair_template_id)
                else:
                    logging.info('Solver is mod; don\'t alter flair')

    def _find_solver(self, comment):
        return comment.parent().author

    def _marks_as_solved(self, comment):
        pass

    def _is_mod_comment(self, comment):
        pass

    def _is_first_solution(self, comment):
        pass

    def _log_solution_info(self, comment):
        pass

