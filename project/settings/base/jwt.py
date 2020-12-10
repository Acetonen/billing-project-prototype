import datetime


JWT_AUTH = {
    'JWT_EXPIRATION_DELTA': datetime.timedelta(days=31 * 6),
    'JWT_REFRESH_EXPIRATION_DELTA': datetime.timedelta(days=31 * 12),
}
