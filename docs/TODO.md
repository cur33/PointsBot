# TODO

## Current

## General

* [ ] Logging
* [ ] Testing
    - Any PRAW model that inherits from `praw.PRAWBase` has a `parse` method
        that could perhaps be used to make fake objects for testing.
* [ ] GUI
    - [ ] Create a GUI for configuring and running the bot, and performing other jobs
        like adding or subtracting points for specific redditors
    - [ ] Check for updates in the Github repo and prompt user to update
        - Github API overview:
            - https://developer.github.com/v3/
            - https://developer.github.com/v4/
                - It turns out that v4 might only be possible with a Github user
                    account to authenticate with the API.
        - Useful links:
            - https://developer.github.com/v3/repos/branches/#get-branch
            - https://developer.github.com/v3/repos/contents/#get-archive-link
            - https://developer.github.com/v3/repos/commits/
            - https://developer.github.com/v3/repos/releases/
            - https://developer.github.com/v3/#timezones
        - Webhooks:
            - https://developer.github.com/webhooks/
            - https://developer.github.com/v3/repos/hooks/
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

## File-Specific

### bot.py

* [ ] Allow mods and/or bot owner to add or remove points from specific users
* [ ] Make the algorithm for determining the problem solver more sophisticated
    - e.g. check entire comment tree instead of just ignoring if the OP also
        authored the parent comment
    - Ask OP for clarification only if solver cannot be sufficiently determined
    - Again, this behavior could also perhaps be better enforced through
        subreddit rules rather than algorithmically

### config.py

* [ ] Switch from `toml` package to `tomlkit` package
    - Preserves style, comments, etc.

### database.py

* [ ] Store date for each "!solved" comment
    - This basically means storing a link to each "![Ss]olved" comment, and
        perhaps a link to the submission, although that can be derived as long
        as the comment doesn't get deleted
* [ ] Possibly refactor for a datastore type thing instead of database
    - Maybe even make models like Redditor to combine data storage/access with
        logic, e.g. determining current level

