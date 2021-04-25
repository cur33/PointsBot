# DONE

## General

* [X] Initial/Basic Logging
    * Especially when unable to handle a comment
* [X] Change commands from !solved and /solved to !helped and /helped
* [X] Allow multiple users to be awarded points on a single post
    * So just check whether each user is already awarded a point for a given post

## Bugs
* [X] mod /helped command doesn't work on one post (some posts?)
    * the problem here seems to be the fact that when the bot adds a point for a solution comment, it
    also adds the comment to the comments table without first checking whether it already exists
    * while it is the case that we should only have one one `solution` row for each comment, it is potentially
    possible that a comment could already be in the db when we add a solution for it, e.g. if the solution was
    deleted (meaning the point was removed) and then we want to add it back, or something??
* [X] bot crashes when a mod is trying to award a point to a solution on a deleted post
    * the problem is that the new schema had the submission_id as a required foreign key, but a
    deleted post will not have one
    * according to them, since only mods will award points on deleted posts, it's fine if the fix is limited to mods

## File-Specific

### bot.py

* [X] Allow mods to mark a post as solved with "/[Ss]olved"
* [X] Allow mods to use "/[Ss]olved" in any context
* [X] When replying to solution, the bot should...
    - [X] Reply to the comment containing the "![Ss]olved" string
    - [X] Tag the solver so they will be notified
    - ~~Delete the automod message~~
* ~~Add a star to the user flair for every 100 points~~
* ~~Add a way to look up user points~~
    - i.e. summon bot by tagging it and provide a username to look up
    - the bot will reply with the last message that the user received

### config.py

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

### reply.py

* [X] Fix progress bar
* ~~For the footer section of the reply comment regarding the bot, could have the
    bot make a post on its account explaining itself, and link to that (and then
    also link to the source code separately, and perhaps in that post, too).
    Could even have the bot make this post automatically if it doesn't have a
    link to the post in its config, and then store the link for future use.~~

