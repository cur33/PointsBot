# TODO

File-specific lists are in loose descending order of priority.

## Current

N / A
## Bugs

* [ ] Users can get multiple points for same solution
    - Scenario:
        - OP comments !solved
        - OP deletes !solved comment
        - OP comments !solved again
    - Hopefully this will be easily solved once db migrations are working

## General

* [ ] Notifications
    * Let admins know if a comment can't be properly handled
    * Email preferable; could do Reddit message, too
        * Maybe have both and make into a config option
* [ ] Testing
    - Any PRAW model that inherits from `praw.PRAWBase` has a `parse` method
        that could perhaps be used to make fake objects for testing
    - Add regression tests for comments, etc.?
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

* [ ] (Maybe) sanitize input text?
* [ ] Now that the date of each solution is being stored, can check for missed
    submissions each time the bot is run by searching subreddit history until
    last solution found
* [ ] Allow mods and/or bot owner to add or remove points from specific users
* [ ] Make the algorithm for determining the problem solver more sophisticated
    - e.g. check entire comment tree instead of just ignoring if the OP also
        authored the parent comment
    - Ask OP for clarification only if solver cannot be sufficiently determined
    - Again, this behavior could also perhaps be better enforced through
        subreddit rules rather than algorithmically

### config.py

* [ ] Add list of emails to which notifications should be sent
* [ ] Switch from `toml` package to `tomlkit` package
    - Preserves style, comments, etc.

### database.py

* [ ] For each solved submission, store:
    - submission id
    - solution comment id
    - solved comment id
    - date
    - solver id
* [ ] Possibly refactor for a datastore type thing instead of database
    - Maybe even make models like Redditor to combine data storage/access with
        logic, e.g. determining current level
    - Seems like overkill, though
