# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# Configurar contexto para templates
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
            ],
        },
    },
]

# Configurações de processamento de imagem
IMAGE_MAX_SIZE = 512  # Reduzido para processamento mais rápido
BATCH_SIZE = 8  # Aumentado para melhor utilização da GPU
MODEL_OPTIMIZATION = {
    'quantize': True,
    'optimize_memory': True,
    'half_precision': True,  # Usar FP16 para processamento mais rápido
    'thread_count': 4  # Número de threads para processamento
}

# Cache mais rápido usando Redis
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
    }
}