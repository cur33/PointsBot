# Changelog

## Version 0.2.1, 2021-04-24

Features: N/A

Fixes:
1. Bot no longer crashes when a mod marks a deleted submission as solved
2. Bot no longer crashes for solutions whose comment has already been stored in the db

Miscellaneous: N/A

## Version 0.2.0, 2021-03-07

Features:
1. Points can now be awarded to multiple comments on the same post
2. The bot summoning keyword has been changed from "solved" to "helped"

Fixes: N/A

Miscellaneous:
1. Introduced versioning for the bot and database

## 2020-08-21

Features: N/A

Fixes:
1. Removed freezing to comply with r/RequestABot guidelines

Miscellaneous: N/A

## 2020-05-10

Features:
1. Adding basic initial logging
    * Logs both to a file and to the command prompt

Fixes: N/A

Miscellaneous:
1. Moved feedback & scoreboard links for bot reply into configuration
2. Changed program entry point to `PointsBot.py`
3. Added ability to freeze the app as a simple executable
