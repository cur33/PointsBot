# PointsBot

## Table of Contents

* [Description](#description)
* [Installation](#installation)
* [Configuration](#configuration)
* [Usage](#usage)
* [Ideas](#ideas)
* [Questions](#questions)
* [Terms of Use for a bot for Reddit](#terms-of-use-for-a-bot-for-reddit)
* [License](#license)

## Description

This is a bot for Reddit that monitors solutions to questions or problems in a
subreddit and awards points to the user responsible for the solution.

This bot is intended as a solution for
[this request](https://www.reddit.com/r/RequestABot/comments/emdeim/expert_level_bot_coding/).

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

* [Python 3](https://www.python.org/downloads/) (specifically version 3.7 or greater)
    * pip (should be installed automatically with Python)
* [pipenv](https://pipenv.readthedocs.io/en/latest/)
    * After installying Python & pip, install by running `pip install pipenv`
    * For other installation options,
        [see here](https://pipenv.readthedocs.io/en/latest/install/#installing-pipenv)

First, download this project using `git` or by downloading a ZIP archive from
the Github repository using the green `Clone or download` button. If ZIP, be
sure to extract the files from the archive before moving on.

To install the packages necessary for running the bot, navigate to the project
root directory and run `pipenv install`.
To uninstall (i.e. delete the project's virtual environment and the installed
python packages), navigate to the project root directory and instead run
`pipenv --rm`.

## Configuration

The bot can be configured by changing the values in the configuration files in
the project root directory:

* `praw.ini`
    - Contains the account information for the bot
* `pointsbot.ini`
    - Contains settings for bot behavior

You shouldn't have to worry about it, but if you need it, the syntax for the
config files can be found on the
[INI file format's Wikipedia page](https://en.wikipedia.org/wiki/INI_file).

If this is your first time running the bot, you will need to copy
`praw.sample.ini` to a new file called `praw.ini`, and likewise copy
`pointsbot.sample.ini` to a new file called `pointsbot.ini`. Any instances of
the word "REDACTED" should be replaced with the desired values; other values
should work as-is, but can be changed as desired.

The reason for this is that these config files (especially `praw.ini`) can
contain sensitive information, and maintaining only sample versions of these
files helps developers to avoid accidentally uploading that sensitive
information to a public (or even private) code repository.

### praw.ini

In order to make a bot, you must first have a bot account. This could be a
personal account, but it is wise to create a dedicate account for the bot,
especially one with the word "bot" somewhere in the name.

Once you have that, you can create a Reddit app for the bot. This is needed for
authenticating with Reddit.

1. First, go to your [app preferences](https://www.reddit.com/prefs/apps).
2. Select the "are you a developer? create an app..." button.
3. Provide a name for the bot, which could probably be the same as the account's
   username.
4. Select the "script" radio button.
5. Provide a brief description.
6. For the "about url", you can provide a link to this Github repository:
    https://github.com/cur33/PointsBot
7. Since it is unused, the "redirect uri" can be set to something like:
    http://www.example.com/unused/redirect/uri
8. Select "create app".

Now you should be redirected to a page which contains the credentials you will
need; under the name of the bot is the unlabeled `client_id`, and below that
with the label "secret" is the `client_secret`.

If you have already done this in the past, the `client_id` and `client_secret`
can be found by navigating to your
[app preferences](https://www.reddit.com/prefs/apps) and selecting the "edit"
button for the app under the "developed applications" section.

Several credentials are needed for running your bot, each of which is listed in
the `praw.ini` config file:

* `client_id`: Copy from your app preferences, as specified in the previous
    steps.
* `client_secret`: Copy from your app preferences, as specified in the previous
    steps.
* `user-agent`: This field can be left as-is, thought if you'd like, you can
    change it by following [these guidelines]().
* `username`: The username for the bot account.
* `password`: The password for the bot account.

### pointsbot.ini

For now, these settings are pretty straightforward.

The `Core` section:

* `subreddit_name`: The name of the subreddit to monitor
* `praw_site_name`: This should probably be left alone; it tells the bot which
    credentials to use when authenticating with Reddit. It's useful for
    development and easy testing with different accounts without having to
    modify values in the code.
* `database_name`: This is the filepath to the SQLite database file, which ends
    with the `.db` file extension.

The `Levels` section is used to determine the available user levels and
corresponding flair texts.

* The key on the left-hand side specifies the title and flair text for the
    level; the case is ignored, and the text is converted to title case (first
    letter of each word capitalized, and the rest lowercase).
* The value on the right-hand side of each line is the total number of points
    required to reach that level.

The order of these lines doesn't matter; the bot will sort them in order of
point totals.

## Usage

The simplest way to run the bot is to navigate to the project root directory and
run:

```bash
pipenv run python -m pointsbot
```

## Ideas

### Config

* Store all config and data in a hidden `.pointsbot` directory or similar in the
    user's home or data directory (OS-dependent).
* Could do something similar to packages like PRAW:
    1. Look in current working directory first.
    2. Look in OS-dependent location next.
    3. (Maybe) Finally, could look in the directory containing the source files
       (using `__file__`).
* Could also allow use of environment variables, but this seems unnecessary and
    could be a little too technical (though any more technically-minded users
    might appreciate the option).
* Consolidate `pointsbot.ini` and `praw.ini` into a single config file.
* Write a CLI script or GUI to handle this so the config values don't have to be
    changed manually.

### Database

* Should it keep track of the solved posts for future reference and calculate
    points on the fly, rather than just keeping track of points? If so, should
    have a column denoting whether the post has been deleted, if that
    information is decided to be useful when determining a user's points.

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
* Should the comment contain a notice that the post was made by a bot, similar
    to the notice on posts by automod?

## Terms of Use for a bot for Reddit

Since this is an open-source, unmonetized program, it should be considered
non-commercial, and is thus allowed to use the Reddit API without registration.
However, this bot is provided under the permissive MIT license. Therefore, if
your use of the bot becomes commercial, you should
[read the Reddit API terms and register here](https://www.reddit.com/wiki/api).

## License

Copyright &copy;2020 Collin U. Rapp. This repository is released under the MIT
license.
