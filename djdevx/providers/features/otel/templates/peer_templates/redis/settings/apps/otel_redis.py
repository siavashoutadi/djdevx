from settings.utils.base_settings import AppBaseSettings


class OtelRedisSettings(AppBaseSettings):
    otel_redis_enabled: bool = True


_otel_redis = OtelRedisSettings()

OTEL_REDIS_ENABLED: bool = _otel_redis.otel_redis_enabled
