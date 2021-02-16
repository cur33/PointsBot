"""Entry point used for either runnning or freezing the bot."""
import pointsbot

try:
    pointsbot.run()
except KeyboardInterrupt as e:
    print('\nShutting down...\n')
