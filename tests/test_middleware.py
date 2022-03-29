from django.test import TestCase


class TestApiKeyAuthenticationMiddleware(TestCase):
    # WIP Build out some tests for the middleware logic
    #   Validate that it works/parses and saves the last time the token was used
    #   Validate that, based on position, it defers to the session auth
    #   Validate that it supports a custom header
    #   Validate that it supports a custom prefix
    pass
