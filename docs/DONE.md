# DONE

## General

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

* [X] For each solved submission, store:
    - submission id
    - solution comment id
    - solved comment id
    - date
    - solver id

### reply.py

* [X] Fix progress bar
* ~~For the footer section of the reply comment regarding the bot, could have the
    bot make a post on its account explaining itself, and link to that (and then
    also link to the source code separately, and perhaps in that post, too).
    Could even have the bot make this post automatically if it doesn't have a
    link to the post in its config, and then store the link for future use.~~

