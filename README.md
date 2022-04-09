# Django User API Keys

API Keys allow clients to pass a secure value to an API without having to first exchange a username and password. This
makes interactions between machines straight forward and consistent. While these keys are easy to use, it is important
to ensure they are secure. This application accomplishes this security by:

1. Hashing all key values after creation. This means admins of the application and malicious actors should never be able
   to access key values in plain text.
2. Allowing for keys to be "cycled". This can be accomplished by revoking current keys and creating new ones. Clients
   can choose to do this on a regular basis or as needed, if they believe a key has been compromised.

## Usage

### Standard Django

1. Install the package: `pip install git+https://github.com/camuthig/django-user-api-key.git@master` (not yet available on pypi)
2. Add `django_user_api_key` to the `INSTALLED_APPS` of your project
3. Add the middleware to your middleware stack
   ```python
   MIDDLEWARE = [
       "django.contrib.auth.middleware.AuthenticationMiddleware",
        # Putting this after the standard session authentication will defer to the session if it defines a user.
       "django_user_api_key.middleware.ApiKeyAuthenticationMiddleware",
   ]
   ```
4. Create a key and add it to your settings file as `USER_API_KEY_SECRET`
5. Create a key for yourself using the Django Admin
6. Send an API request with the setting the authorization header as `Authorization: Api-Key xyz`

### REST Framework

1. Install the package: `pip install git+https://github.com/camuthig/django-user-api-key.git@master` (not yet available on pypi)
2. Add `django_user_api_key` to the `INSTALLED_APPS` of your project
3. Add the authentication class to your DRF default authentication classes
   ```python
   REST_FRAMEWORK = {
       "DEFAULT_AUTHENTICATION_CLASSES": [
           "django_user_api_key.rest_framework.auth.UserApiKeyAuthentication",
           "rest_framework.authentication.SessionAuthentication",
       ],
   }
   ```
4. Create a key and add it to your settings file as `USER_API_KEY_SECRET`
5. Create a key for yourself using the Django Admin
6. Send an API request with the setting the authorization header as `Authorization: Api-Key xyz`

**Optional: Add API Key Views**

APIs can be added to your Django application to create, retrieve, and revoke keys out of the box.

```python
# urls.py
from django.urls import include
from django.urls import path

from django_user_api_key.rest_framework.urls import router as api_key_router

urlpatterns = [
    # other routes...

    path("api/", include(api_key_router.urls)),
]
```


## Implementation Details

API values are implemented as UUID4 values. These are sufficiently unique to remain secure and avoid collisions.

## Security Concerns

**API Key records should NOT be deleted from the database, even if revoked.** If keys are deleted, there is the
possibility that the key value could be reassigned to a different user at a later time. If the user originally provided
the key retains it, they may later use it to inadvertently access the API as the new user. The default behavior of this
application in the admin is to _revoke_ keys instead of deleting them, and it is recommended users follow this same
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
* Django OAuth Toolkit - WIP
* Django REST Framework TokenAuthentication - WIP
