# Changelog

## 2020/05/10

Features:
1. Adding basic initial logging
    * Logs both to a file and to the command prompt

Fixes: N/A

Miscellaneous:
1. Moved feedback & scoreboard links for bot reply into configuration; will need to specify them when re-configuring
2. Changed recommended program entry point to `PointsBot.py`
    * This means that the recommended way to run the bot is now `pipenv run PointsBot.py`
3. Added ability to freeze the app as a simple executable

## 2020/08/21

Features: N/A

Fixes:
1. Removed ability to freeze to comply with r/RequestABot guidelines

Miscellaneous: N/A

## 2020/08/25

Features:
1. Added database migrations
    * This will make it easier to change the database design without losing data or having to do anything manually