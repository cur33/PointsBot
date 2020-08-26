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

## Multiple behaviors

Implement the concept of actions, with a mapping between trigger keywords/patterns and actions. This will allow for multiple behaviors (eg mark as solved for one behavior, and just show points when summoned for another).

Maybe allow chains of actions. For example:
1. OP comments "!solved"
2. Bot receives comment
3. Action 1: Determine whether is "!solved" comment
4. Action 2: Determine solver
5. Action 3: Add points
6. Action 4: Reply

## Making the bot easier to configure

Allow bot user to just specify a list of strings to recognize to trigger the bot's response. Allow user to specify whether case-sensitive. Ways to do this, with varying performance:
* Just search each text for each keyword;
* Use `re.compile()` for each keyword before searching (*may* be faster?); or
* Build a binary search tree for all keywords for each action