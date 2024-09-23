from isi_project.settings import config

SECRET_KEY = config('SECRET_KEY')
ROOT_URLCONF = 'isi_project.urls'

WSGI_APPLICATION = 'isi_project.wsgi.application'
ASGI_APPLICATION = 'isi_project.asgi.application'

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
