# Django PAT (Personal Access Tokens)

![Tests](https://github.com/camuthig/django-pat/actions/workflows/ci.yml/badge.svg)
[![codecov](https://codecov.io/gh/camuthig/django-pat/branch/main/graph/badge.svg?token=GAGIIZXC95)](https://codecov.io/gh/camuthig/django-pat)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Source Code](https://img.shields.io/badge/Source-code-lightgrey)](https://github.com/camuthig/django-pat)
![PyPI](https://img.shields.io/pypi/v/django-pat)
![Python Versions](https://img.shields.io/pypi/pyversions/django-pat)
![Django Versions](https://img.shields.io/pypi/djversions/django-pat?label=django)

This application creates personal access tokens that clients can send via HTTP headers to authenticate as a particular user.
This application expands on the standard functionality provided in REST Framework tokens by allowing users to create
more than one token and cycle/revoke tokens for security purposes.

Personal access tokens are API keys that allow clients to pass a secure value to an API without having to first exchange
a username and password. This  makes interactions between machines straightforward and consistent. While these tokens are
easy to use, it is important to ensure they are secure. This application accomplishes this security by:

1. Hashing all token values after creation. This ensures admins of the application and malicious actors are never be able
   to access token values in plain text via a data breach.
2. Allowing for tokens to be "cycled". This is accomplished by revoking existing tokens and creating new ones. Clients
   can do this easily via APIs on a regular basis or as needed, if they believe a token has been compromised.

## Usage

By default, both the standard middleware and the REST Framework authentication will look for the token in the
`Authorization` HTTP header with a prefix of `Access-Token`. So this might look like

```
Authorization: Access-Token 41ecea63-66eb-4e6a-bffd-e85cd29718ab
```

### Initial Setup
1. Install the package: `pip install django-pat`
2. Add `django_pat` to the `INSTALLED_APPS` of your project
3. Add the `PAT_SECRET` value to your settings file to hash secrets. This value should be kept secret!
    ```python
    PAT_SECRET = "super-secret-hashing-key"
    ```


### Django Middleware

1. Add the middleware to your middleware stack
   ```python
   MIDDLEWARE = [
       "django.contrib.auth.middleware.AuthenticationMiddleware",
       "django_pat.middleware.PatAuthenticationMiddleware",
   ]
   ```

### REST Framework

1. Add the authentication class to your DRF default authentication classes
   ```python
   REST_FRAMEWORK = {
       "DEFAULT_AUTHENTICATION_CLASSES": [
           "django_pat.rest_framework.auth.PatAuthentication",
           "rest_framework.authentication.SessionAuthentication",
       ],
   }
   ```

**Optional: Add Personal Access Token Views**

APIs can be added to your Django application to create, retrieve, and revoke tokens out of the box. This will create new Django Rest Routes at `/personalAccessTokens`

```python
# urls.py
from django.urls import include
from django.urls import path

from django_pat.rest_framework.urls import router as pat_router

urlpatterns = [
    # other routes...

    path("api/", include(pat_router.urls)),
]
```

Alternatively, the `PersonalAccessTokenViewSet` can be added to any route you prefer.

## Configuration

Along with the `PAT_SECRET` value that is required, you can also configure certain behaviors of the package in your Django
application settings.

* `PAT_CUSTOM_HEADER` - Sets the HTTP header to check for the token. This defaults to `Authorization`
* `PAT_CUSTOM_HEADER_PREFIX` - Sets the prefix for the header value. This defaults to `Access-Token`. The middleware
    and the REST authentication expect a space between the prefix and the token value.
* `PAT_USES_SHARED_HEADER` - If set to True, then the package will not attempt to validate the prefix on the authorization
    header. This is most useful when different prefixes are used for different types of authentication, but are all sent
    using the same HTTP header.

## Implementation Details

Access token values are implemented as UUID4 values. These are sufficiently unique to remain secure and avoid collisions.

## Security Concerns

**Personal access token records should NOT be deleted from the database, even if revoked.** If tokens are deleted, there is the
possibility that the token value could be reassigned to a different user at a later time. If the user originally provided
the token retains it, they may later use it to inadvertently access the API as the new user. The default behavior of this
application in the admin is to _revoke_ token instead of deleting them, and it is recommended users follow this same
pattern.

If a brute force attack is a concern, then rate limiting should be applied to API views. The possibility of brute
forcing all possible UUID4 values is unlikely, but rate limiting provides another way to avoid it.

## Alternative Packages

* [Django REST Framework API Key](https://florimondmanca.github.io/djangorestframework-api-key/guide/) This project
  similarly provides the ability to create and manage API keys for machine-to-machine API calls. It is focused on
  supporting unauthorized requests, i.e. those not linked to a particular user. There are a few reasons I chose to go
  with a different option.
  * The Django REST Framework API Keys is tightly coupled with Django REST Framework. I wanted this package to support
    DRF without being coupled to it, such that developers who want to build APIs without DRF have the option.
  * The default behavior of Django REST Framework API Keys is not linked to users. The key can be extended to have a
    reference to the user, but this requires additional configuration and the default model table is still created for
    the base API key model. This means that by default developers will be able to use existing user permissions with
    working with a User API Key. See: [Issue 180](https://github.com/florimondmanca/djangorestframework-api-key/issues/180)
  * The Django REST Framework API Key encryption technique used by the application creates a slower API. This has been
    alleviated in Django User API Key by using HMAC hashing instead. See:
    [Issue 173](https://github.com/florimondmanca/djangorestframework-api-key/issues/173)
  * The primary key pattern of the Django REST Framework API Key records use special characters, making them difficult
    to encode for browsers. See: [Issue 128](https://github.com/florimondmanca/djangorestframework-api-key/issues/128)
* [Django REST Framework TokenAuthentication](https://www.django-rest-framework.org/api-guide/authentication/#tokenauthentication)
  The standard DRF `TokenAuthentication` model has a couple of drawbacks that this project attempts to avoid by
  expanding on the pattern. In the standard token pattern:
  * The token value is stored in a plain-text format
  * The token value acts as the primary key of the token. If building an API to retrieve the token, you would not
    want to use this key in a URL, as it would go over the network in plain-text.
  * Each user can only have a single token.
  * Revoking one user's token opens up the possibility of generating the same token again for a different user.
