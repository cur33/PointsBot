# TODO

## Current

## General

* [ ] Logging
* [ ] Testing
* [ ] GUI
    - [ ] Create a GUI for configuring and running the bot, and performing other jobs
        like adding or subtracting points for specific redditors
    - [ ] Check for updates in the Github repo and prompt user to update
        - It turns out that this might only be possible with a Github user
            account to authenticate with the API.
        - Github API overview:
            - https://developer.github.com/v3/
            - https://developer.github.com/v4/
        - Useful links:
            - https://developer.github.com/v3/repos/branches/#get-branch
            - https://developer.github.com/v3/repos/commits/
            - https://developer.github.com/v3/repos/releases/
            - https://developer.github.com/v3/repos/hooks/
        - Webhooks:
            - https://developer.github.com/webhooks/
            - https://developer.github.com/v3/activity/events/types/#pushevent
* [ ] Determine whether and how to check "![Ss]olved" comments have been later
    edited to remove the "![Ss]olved" string, and whether and how to remove or
    reassign points
    - If so, it could do that daily or something.
    - This will be especially important if a "recovery mode" is implemented that
        crawls through the whole subreddit to rebuild the database, since the
        bot would only be able to see comments that haven't been removed, or
        the newest version of edited comments.
    - This could also just be encouraged through sub rules; e.g. "don't mark as
        solved until you've actually tried the proposed solution"
* [ ] As mentioned in the previous section, implement a recovery mode

## File-Specific Tasks

### bot.py

* [ ] Allow mods and/or bot owner to add or remove points from specific users
* [ ] Make the algorithm for determining the problem solver more sophisticated
    - e.g. check entire comment tree instead of just ignoring if the OP also
        authored the parent comment
    - Ask OP for clarification only if solver cannot be sufficiently determined
    - Again, this behavior could also perhaps be better enforced through
        subreddit rules rather than algorithmically
* [X] Allow mods to mark a post as solved with "/solved"
* [X] When replying to solution, the bot should...
    - [X] Reply to the comment containing the "![Ss]olved" string
    - [X] Tag the solver so they will be notified
    - ~~Delete the automod message~~
* ~~Add a star to the user flair for every 100 points~~
* ~~Add a way to look up user points~~
    - i.e. summon bot by tagging it and provide a username to look up
    - the bot will reply with the last message that the user received

### config.py

* [ ] Switch from `toml` package to `tomlkit` package
    - Preserves style, comments, etc.
* [X] Change from `ini` to `toml `
* [X] Consolidate `pointsbot.ini` and `praw.ini` into a single config file.
* [X] Add option for flair_template_id
* [X] Check for config file in a well-known location, e.g. `~` directory
    - Probably named `~/.pointsbot` or something similar
    - Could do something similar to packages like PRAW:
        1. Look in current working directory first.
        2. Look in OS-dependent location next.
        3. (Maybe) Finally, could look in the directory containing the source files
           (using `__file__`).
* [X] Add interactive config scipt
* ~~Fix titlecase problem with roman numerals~~
    - Only an issue with `ini` format
* ~~Separate the development-handy config items into separate section~~
    - Don't really have any right now

### database.py

* [ ] Possibly refactor for a datastore type thing instead of database
    - Maybe even make models like Redditor to combine data storage/access with
        logic, e.g. determining current level

### reply.py

* [ ] For the footer section of the reply comment regarding the bot, could have the
    bot make a post on its account explaining itself, and link to that (and then
    also link to the source code separately, and perhaps in that post, too).
    Could even have the bot make this post automatically if it doesn't have a
    link to the post in its config, and then store the link for future use.
* [X] Fix progress bar

## Ideas

### Config

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
