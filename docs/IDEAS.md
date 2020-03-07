# IDEAS

## Determining when to award points

To ensure that points are only awarded for the first comment marked as a
solution:

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
