
import os
from pathlib import Path
from dotenv import load_dotenv


load_dotenv()


BASE_DIR = Path(__file__).resolve().parent.parent


SECRET_KEY = os.getenv('SECRET_KEY')


DEBUG = os.getenv('DEBUG', 'False') == 'true'


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

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

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

STATIC_URL = 'static/'

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
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'aliouneelemine@gmail.com'  # Votre email Gmail
EMAIL_HOST_PASSWORD = 'liox quqy zexn qlms'  # Mot de passe d'application
DEFAULT_FROM_EMAIL = 'aliouneelemine@gmail.com'



# MinIO / S3 Configuration
if not DEBUG:
    # En production, tu activeras ceci
    pass

# Pour le dev, on active MinIO que si les vars sont présentes
USE_MINIO = os.getenv('AWS_S3_ENDPOINT_URL', None) is not None
MINIO_PUBLIC_URL = "http://10.36.147.68:9000"



if USE_MINIO:
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
    AWS_STORAGE_BUCKET_NAME = os.getenv('AWS_STORAGE_BUCKET_NAME')
    AWS_S3_ENDPOINT_URL = os.getenv('AWS_S3_ENDPOINT_URL')
    AWS_S3_REGION_NAME = os.getenv('AWS_S3_REGION_NAME', 'us-east-1')
    AWS_S3_USE_SSL = os.getenv('AWS_S3_USE_SSL', 'True') == 'True'
    AWS_S3_VERIFY = os.getenv('AWS_S3_VERIFY', 'True') == 'True'
    AWS_DEFAULT_ACL = None  # Important : pas de ACL publique
    AWS_S3_FILE_OVERWRITE = False
    AWS_S3_OBJECT_PARAMETERS = {
        'CacheControl': 'max-age=86400',
    }


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

if not DEBUG:
    # Static files
    STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
    
    # Database (Render fournit DATABASE_URL)
    import dj_database_url
    DATABASES['default'] = dj_database_url.config(conn_max_age=600)
    
    # MinIO/Backblaze B2
    AWS_ACCESS_KEY_ID = config('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = config('AWS_SECRET_ACCESS_KEY')
    AWS_STORAGE_BUCKET_NAME = config('AWS_STORAGE_BUCKET_NAME')
    AWS_S3_ENDPOINT_URL = config('AWS_S3_ENDPOINT_URL')
    AWS_S3_REGION_NAME = config('AWS_S3_REGION_NAME', default='us-east-1')
    AWS_S3_CUSTOM_DOMAIN = f"{AWS_STORAGE_BUCKET_NAME}.{AWS_S3_ENDPOINT_URL.split('//')[1]}"
    AWS_S3_OBJECT_PARAMETERS = {'CacheControl': 'max-age=86400'}
    AWS_DEFAULT_ACL = 'private'
    AWS_S3_FILE_OVERWRITE = False
    
    # Utiliser S3 pour les fichiers uploadés
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'