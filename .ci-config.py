from daktari.checks.git import GitInstalled

title = "CI Test"

checks = [
    GitInstalled(),
]
