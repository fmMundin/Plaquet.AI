// ...existing code...

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