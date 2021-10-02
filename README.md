# django-society-elections
A Django app to run first-past-the-post elections for a university society


## Build and Installation

First, make sure you have the required version of Python (>=3.6) and you have created a virtual environment with `python -m venv venv`. To create migrations during development, run `make migrations`. This will also be done as part of the build and install stages.

To build: `make build` or alternatively `python setup.py build`

To install: `make install` or alternatively `python setup.py install`


## Using it in your Django project

You will need some settings for your Django project to make this work. If you want to use the emailing features you will need the following settings in your `settings.py`:

```python
# The root URL of your site without the trailing slash
ROOT_URL = "http(s)://[hostname]"

# Email address to send emails from
DEFAULT_FROM_EMAIL = "noreply@hostname"
```

You will also need any additional email configuration to get the emailing functionality working in your Django application. See https://docs.djangoproject.com/en/dev/topics/email/

You will also need a URL path with a name `verify_candidate` which points at a view to validate a given candidate. URL configuration should take one argument which will be the UUID used to verify the email. You can check that an email has been validated by comparing the UUID supplied against a lookup in the database, and then marking the resulting record as verified. Optionally, you can then clear the `email_uuid` field in the database.