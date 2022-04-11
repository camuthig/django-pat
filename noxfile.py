import nox


# TODO 3.10 currently causes errors on build. Support will be added later.
@nox.session(python=["3.6", "3.7", "3.8", "3.9"])
def tests(session):
    session.run("poetry", "install", external=True)
    session.run("pytest")


lint_dirs = ["django_user_api_key", "tests", "example_project"]


@nox.session(python=["3.6"])
def types(session):
    session.run("poetry", "install", external=True)
    session.run("mypy", ".", external=True)


@nox.session(python=["3.6"])
def formatting(session):
    session.run("poetry", "install", external=True)
    session.run("flake8", *lint_dirs)
    session.run("isort", "--check-only", "--diff", "--force-single-line-imports", "--profile", "black", *lint_dirs)
    session.run("black", "--check", "--diff", *lint_dirs)
