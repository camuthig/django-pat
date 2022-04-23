import nox


@nox.session
@nox.parametrize(
    "python, django",
    [
        (python, django)
        for python in ("3.7", "3.8", "3.9", "3.10")
        for django in ("3.2", "4.0")
        if (python, django) != ("3.7", "4.0")
    ],
)
def tests(session, django):
    session.run("poetry", "install", external=True)
    session.install(f"django=={django}")
    session.run("pytest", "--cov", "--cov-report=xml")


lint_dirs = ["django_user_api_key", "tests", "example_project"]


@nox.session(python=["3.7"])
def types(session):
    session.run("poetry", "install", external=True)
    session.run("mypy", ".", external=True)


@nox.session(python=["3.7"])
def formatting(session):
    session.run("poetry", "install", external=True)
    session.run("flake8", *lint_dirs)
    session.run("isort", "--check-only", "--diff", "--force-single-line-imports", "--profile", "black", *lint_dirs)
    session.run("black", "--check", "--diff", *lint_dirs)
