import comment

levels = [
    ('Helper', 5),
    ('Trusted Helper', 15),
    ('Super Helper', 40),
]

tests = [1, 5, 10, 15, 30, 40, 45]

for testpoints in tests:
    progbar = comment.progress_bar(testpoints, levels)
    print(f'Points: {testpoints}')
    print(progbar)
    print()
