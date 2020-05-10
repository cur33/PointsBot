# PointsBot

## Table of Contents

* [Description](#description)
* [Installation](#installation)
* [Prerequisites & Configuration](#prerequisites--configuration)
* [Usage](#usage)
* [Terms of Use for a bot for Reddit](#terms-of-use-for-a-bot-for-reddit)
* [License](#license)

## Description

This is a bot for Reddit that monitors solutions to questions or problems in a
subreddit and awards points to the user responsible for the solution.

This bot was conceived as a response to
[this request](https://www.reddit.com/r/RequestABot/comments/emdeim/expert_level_bot_coding/).

The bot will award a point to a redditor when the OP of a submission includes
"!Solved" or "!solved" somewhere in a reply to the redditor's comment on that
submission.  These points will allow the redditor to advance to different
levels.

At each level, the redditor's flair for the subreddit will be updated to reflect
their current level. However, the bot should not change a mod's flair.

Each time a point is awarded, the bot will reply to the solution comment to
notify the redditor of their total points, with a progress bar to show how many
points they need to reach the next level and a reminder of the title of the next
level.
In order to prevent the progress bar from being excessively long, some points
will be consolidated into stars instead. Right now, stars are hard-coded to
represent 100 points each, but this behavior may be configurable in the future.

The first time a point is awarded, the bot's reply comment will also include a
brief message detailing the points system.

Only the submission OP's first "!Solved" comment should result in a point being
awarded for each submission.

## Installation

### Basic Installation

These are the instructions for simply using the bot without needing to edit the
code. These instructions are best suited for users with less technical
experience.

Go the the [releases page](https://github.com/cur33/PointsBot/releases) for this
project, then download and unzip the latest release. Make sure you pick the
release best suited for your machine & operating system.

### Advanced Installation

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

## Prerequisites & Configuration

### Bot account

In order to make a bot, you must first have a bot account. This could be a
personal account, but it is recommended to create a dedicated account for the
bot, especially one with the word "bot" somewhere in the name.

Once you have that, you can create a Reddit app for the bot. This is needed for
authenticating with Reddit.

1. First, go to your [app preferences](https://www.reddit.com/prefs/apps).
2. Select the "are you a developer? create an app..." button.
3. Provide a name for the bot, which could probably be the same as the account's
   username.
4. Select the "script" radio button.
5. Provide a brief description.
6. For the "about url", you can provide a link to the Github repository:
    https://github.com/cur33/PointsBot
7. Since it is unused, the "redirect uri" can be set to something like:
    http://www.example.com/unused/redirect/uri
8. Select "create app".

You should be redirected to a page which contains the credentials you will need;
under the name of the bot is the unlabeled `client_id`, and below that with the
label "secret" is the `client_secret`.

If you have already done this in the past, the `client_id` and `client_secret`
can be found by navigating to your
[app preferences](https://www.reddit.com/prefs/apps) and selecting the "edit"
button for the app under the "developed applications" section.

### Make the bot a mod in your subreddit

Some of the bot's behaviors, e.g. altering redditor flairs, require moderator
permissions. It should require just the "Flair" and "Posts" permissions and
perhaps the "Access" permission, so you don't need to grant it full permissions.

### Configuration file

The bot will store its configuration file in a `.pointsbot` directory under the
home directory for your user on your machine. By default, this directory is also
where it will store its database and log files, but you can alter this behavior
by specifying other locations for those in the configuration process.

If this is your first time running the bot, then it will fail to detect a
configuration file and will prompt you for the necessary fields. This includes
the credentials for the Reddit account and Reddit app which you created for the
bot in the [Prerequisites & Configuration](#prerequisites--configuration) step
above. The bot will create the configuration file and save this information for
future use.

At the moment, there is not a good way to edit the existing configuration unless
you want to edit the configuration file yourself (see next paragraph). This is
the recommended process for editing the configuration until this feature is
added:
1. Go to your home directory and open the `.pointsbot` directory.
2. Either rename the `pointsbot.toml` file to something else, or move it to a
   different directory.
3. Open that file in a text editor (if you haven't installed one, you can use
   the default text editor for your operating system, like Notepad on Windows).
4. Run the bot and walk through the configuration process again, copying and
   pasting any unchanged values from the original configuration file.
5. Once you are finished, you can either keep the old configuration file for a
   while just in case, or you can delete it.

If you'd prefer, you can instead create and edit the configuration file
yourself. You will need to copy `pointsbot.sample.toml` to a new file called
`pointsbot.toml` located in the `.pointsbot` directory mentioned above. Any
instances of the word "REDACTED" should be replaced with the appropriate values;
other values should work as-is, but can be changed as needed.

This is because the config file can contain sensitive information, and
maintaining only sample versions of these files in this repository helps
developers to avoid accidentally uploading that sensitive information to a
public (or even private) code repository.

More information on the specific config options can be found in the comments in
the sample config file.

You shouldn't have to worry about it, but if you need it, information on the
TOML syntax used for the file can be found on
[TOML's Github page](https://github.com/toml-lang/toml).

## Usage

### Basic Usage

Follow these instructions if you downloaded the bot from the releases page in
the [Installation](#installation) step above.

In the unzipped folder, double-click on the `PointsBot.exe` file. It will open a
command prompt that will ask you for any additional information it may require.
You will *not* need any knowledge of the command prompt for your operating
system to interact with the bot.

### Advanced Usage

The simplest way to run the bot is to navigate to the project root directory and
run:

```bash
pipenv run python PointsBot.py
```

## Terms of use for a bot for Reddit

Since this is an open-source, unmonetized program, it should be considered
non-commercial, and is thus allowed to use the Reddit API without registration.
However, this bot is provided under the permissive MIT license, so if your use
of the bot becomes commercial, you should
[read the Reddit API terms and register here](https://www.reddit.com/wiki/api).

## License

Copyright &copy;2020 Collin U. Rapp. This repository is released under the MIT
license.
