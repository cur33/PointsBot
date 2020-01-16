# PointsBot

## Table of Contents

* [Description](#description)
* [Installation](#installation)
* [Usage](#usage)
* [TODO](#todo)
* [Ideas](#ideas)
* [Questions](#questions)
* [License](#license)

## Description

This is a bot for Reddit that monitors solutions to questions or problems in a
subreddit and awards points to the user responsible for the solution.

This bot is based on the description in
[this request](https://www.reddit.com/r/RequestABot/comments/emdeim/expert_level_bot_coding/).
While this could be used for other subreddits, this means that it is intended
for [r/MinecraftHelp](https://www.reddit.com/r/MinecraftHelp/).

The bot will award a point to a redditor when the OP of a submission includes
"!Solved" or "!solved" somewhere in a reply to the redditor's comment on that
submission.  These points will allow the redditor to advance to different
levels:

* Helper (5 points)
* Trusted Helper (15 points)
* Super Helper (40 points)

At each level, the redditor's flair for the subreddit will be updated to reflect
their current level. However, the bot should not change a mod's flair.

Each time a point is awarded, the bot will reply to the solution comment to
notify the redditor of their total points, with a progress bar to show how many
points they need to reach the next level and a reminder of the title of the next
level.

The first time a point is awarded, the bot's reply comment will also include a
brief message detailing the points system.

Only the submission OP's first "!Solved" comment should result in a point being
awarded for each submission.

## Installation

Requirements:

* [python3](www.python.org) (specifically, version 3.7 or greater)
    * pip (should be installed automatically alongside python)
* [pipenv](https://pipenv.readthedocs.io/en/latest/)
    * Install by running `pip install pipenv`

First, download this project using `git` or by downloading a zipfile from the
Github repository.

To install, navigate to the project root directory and run `pipenv install`.
To uninstall (i.e. delete the project's virtual environment and the installed
python packages), instead run `pipenv --rm`.

## Usage

The bot can be configured by changing the values in the configuration files:

* `praw.ini`
    - Contains the account information for the bot
* `pointsbot.ini`
    - Contains settings for bot behavior

The simplest way to run the bot is to navigate to the project root directory and
run:

```bash
pipenv run python -m pointsbot
```

## Ideas & To-Do

### Config

* Store all config and data in a `.pointsbot` directory or similar in the user's
    home or data directory (OS-dependent).
* Could do something similar to packages like PRAW:
    1. Look in current working directory first.
    2. Look in OS-dependent location next.
    3. (Maybe) Finally, could look in the directory containing the source files
       (using `__file__`).
* Could also allow use of environment variables, but this seems unnecessary and
    could be a little too technical (though any more technically-minded users
    might appreciate the option).
* Consolidate `pointsbot.ini` and `praw.ini` into a single config file.

### Database

Should it keep track of the solved posts for future reference and calculate
points on the fly, rather than just keeping track of points? If so, should have
a column denoting whether the post has been deleted, if that information is
decided to be useful when determining a user's points.

### Determining when to award points

To ensure that points are only awarded for the first comment marked as a
solution:

* Alter the database to allow for tracking of each submission and the first
    comment marked as the solution. Then, everytime a new solution comment is
    detected, simply check the database to see if the submission is already
    counted. This will avoid unnecessary calls to Reddit, which would include
    scanning all the submission comments each time.
* This approach could also make it simpler to check whether a solution comment
    has been edited. Instead of having to do a daily search for edits, it could
    just check the original solution comment to ensure that it still contains
    the "!solved" string. If not, it can remove points from that author and
    award points to the new author.

To ensure that a point is awarded to the correct user:

* We could expand the "!solved" bot summons to include an optional username
    argument. Without the argument, the bot will award the point to either the
    top-level comment or the parent comment of the "!solved" comment, whichever
    is decided upon. However, if the username argument is provided, the bot
    could simple check that one of the comments in the comment tree belongs to
    that user, and then award them the point.
    - Honestly, this is probably overcomplicated and unnecessary, though.

## Questions

* Should it really display a progress bar without a bounds, since the user could
    get a large amount of points? Or should it end at 40 or whatever the max
    level is?
* Should the bot reply directly to the solution comment, or the OP's "!Solved"
    comment and just tag the point earner?
* Should the bot check whether comments containing "!solved" have been edited to
    remove it?
    - If so, it could do that daily or something.
    - This will be especially important if a "recovery mode" is implemented that
        crawls through the whole subreddit to rebuild the database, since the
        bot would only be able to see comments that haven't been removed, or
        the newest version of edited comments.
* When a "!solved" comment is found, should the bot award the point to the
    author of the parent comment or the root comment? In other words, should
    only top-level comments be considered for points?
* Should the bot assume that the parent comment belongs to the user who solved
    the issue, or should it find the first ancestor comment not made by the OP
    (in case the OP responds "!solved" to one of their own comments on the
    solution comment)?
* Should the bot still keep track of points for mods, even though it doesn't
    update their flair?
* Should the reply comment always tag them, even if it's not their first point?
* When a user levels up, should the reply comment also mention that they have
    been awarded a new flair?

## License

Copyright &copy;2020 Collin U. Rapp. This repository is released under the MIT
license.
