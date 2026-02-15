
import os
from pathlib import Path
import dj_database_url
from dotenv import load_dotenv
from decouple import config

load_dotenv()


BASE_DIR = Path(__file__).resolve().parent.parent


SECRET_KEY = os.getenv('SECRET_KEY')


DEBUG = config('DEBUG', default=False, cast=bool)


ALLOWED_HOSTS = ['*']  # À restreindre en prod


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework_simplejwt',
    'drf_spectacular',
    'corsheaders',
    'accounts',
    'documents',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'secure_doc.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'secure_doc.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }

if not DEBUG:
    ALLOWED_HOSTS = ['alioune25.pythonanywhere.com']  # ← Remplace "tonnom"
    
    # Database (PythonAnywhere fournit une DB)
    DATABASES = {
     'default': dj_database_url.parse(os.getenv('DATABASE_URL'))
    }
    
    # Static files
    STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# DATABASE
# import dj_database_url
# DATABASES = {
#     'default': dj_database_url.parse(os.getenv('DATABASE_URL'))
# }

# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {'min_length': 8}
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

# STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

#-------------------------------- Mon cofiguraciones de REST Framework y JWT -------------------------------#
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

from datetime import timedelta
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'TOKEN_OBTAIN_SERIALIZER': 'accounts.serializers.CustomTokenObtainPairSerializer',
}

AUTH_USER_MODEL = 'accounts.User'  # On va créer notre propre User

# EMAIL CONFIG (DEV / TEST)
# EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'  # Affiche dans la console
# DEFAULT_FROM_EMAIL = 'aliouneelemine@gmail.com'
#APPEND_SLASH = False
# EMAIL CONFIG (PRODUCTION / REAL EMAILS)
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST = 'smtp.gmail.com'
# EMAIL_PORT = 587
# EMAIL_USE_TLS = True
# EMAIL_HOST_USER = 'aliouneelemine@gmail.com'  # Votre email Gmail
# EMAIL_HOST_PASSWORD = 'liox quqy zexn qlms'  # Mot de passe d'application
# DEFAULT_FROM_EMAIL = 'aliouneelemine@gmail.com'


from decouple import config
# Email Configuration - MailerSend
if not DEBUG:
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = 'smtp.mailersend.net'
    EMAIL_PORT = 587
    EMAIL_USE_TLS = True
    EMAIL_HOST_USER = 'MS_vkepXh@test-yxj6lj9vpjq4do2r.mlsender.net'  # Mot-clé fixe pour MailerSend
    EMAIL_HOST_PASSWORD = config('MAILERSEND_API_KEY')  # Ta clé API
    DEFAULT_FROM_EMAIL = 'noreply@test-yxj6lj9vpjq4do2r.mlsender.net'  # Remplace XXXX

# MinIO / S3 Configuration
# if not DEBUG:
    # En production, tu activeras ceci
    # pass

# Pour le dev, on active MinIO que si les vars sont présentes
# USE_MINIO = os.getenv('AWS_S3_ENDPOINT_URL', None) is not None
# MINIO_PUBLIC_URL = "http://10.36.147.68:9000"



# if USE_MINIO:
#     DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
#     AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
#     AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
#     AWS_STORAGE_BUCKET_NAME = os.getenv('AWS_STORAGE_BUCKET_NAME')
#     AWS_S3_ENDPOINT_URL = os.getenv('AWS_S3_ENDPOINT_URL')
#     AWS_S3_REGION_NAME = os.getenv('AWS_S3_REGION_NAME', 'us-east-1')
#     AWS_S3_USE_SSL = os.getenv('AWS_S3_USE_SSL', 'True') == 'True'
#     AWS_S3_VERIFY = os.getenv('AWS_S3_VERIFY', 'True') == 'True'
#     AWS_DEFAULT_ACL = None  # Important : pas de ACL publique
#     AWS_S3_FILE_OVERWRITE = False
#     AWS_S3_OBJECT_PARAMETERS = {
#         'CacheControl': 'max-age=86400',
#     }


# Swagger / OpenAPI
SPECTACULAR_SETTINGS = {
    'TITLE': 'SecureDoc API',
    'DESCRIPTION': 'API sécurisée de gestion électronique de documents (GED) avec chiffrement client.',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,  # Cache le schéma brut
    'SCHEMA_PATH_PREFIX': '/api/',
    'CONTACT': {
        'name': 'Équipe SecureDoc',
        'email': 'admin@secdoc.example.com'
    },
    'LICENSE': {
        'name': 'Propriétaire'
    },
    'TAGS': [
        {'name': 'Authentification', 'description': 'Login, profil, mot de passe'},
        {'name': 'Utilisateurs', 'description': 'Gestion des utilisateurs (admin)'},
        {'name': 'Documents', 'description': 'Upload, partage, téléchargement'},
        {'name': 'Catégories', 'description': 'Gestion des catégories de documents'},
    ]
}

CORS_ALLOW_ALL_ORIGINS = True

CORS_ALLOW_HEADERS = [
    "authorization",
    "content-type",
    "accept",
    "origin",
    "x-csrftoken",
]



# Pour Render
import os
from decouple import config

# === CONFIGURATION UNIFIÉE MINIO / BACKBLAZE B2 ===
USE_S3 = os.getenv('AWS_S3_ENDPOINT_URL', None)
#MINIO_PUBLIC_URL = "https://s3.eu-central-003.backblazeb2.com"

if USE_S3:
    # Stockage S3 (MinIO ou Backblaze B2)
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    AWS_ACCESS_KEY_ID = config('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = config('AWS_SECRET_ACCESS_KEY')
    AWS_STORAGE_BUCKET_NAME = config('AWS_STORAGE_BUCKET_NAME')
    AWS_S3_ENDPOINT_URL = config('AWS_S3_ENDPOINT_URL')
    AWS_S3_REGION_NAME = config('AWS_S3_REGION_NAME', default='us-east-1')
    AWS_S3_USE_SSL = config('AWS_S3_USE_SSL', default=True, cast=bool)
    AWS_S3_VERIFY = config('AWS_S3_VERIFY', default=True, cast=bool)
    AWS_DEFAULT_ACL = None
    AWS_S3_FILE_OVERWRITE = False
    AWS_S3_OBJECT_PARAMETERS = {'CacheControl': 'max-age=86400'}

# Static files (obligatoire pour Render)
STATIC_URL = '/static/'
if not DEBUG:
    STATIC_ROOT = BASE_DIR / 'staticfiles'
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'