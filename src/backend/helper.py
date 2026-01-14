import redis
from redis.exceptions import RedisError, ConnectionError, TimeoutError


class RedisHelper:
    def __init__(self, client: redis.Redis):
        """Private constructor - stores client internally."""
        self._client = client  # Private attribute (convention)

    # ---------- PRIVATE static factory ---------- #
    @staticmethod
    def _create_client(
        host: str = "localhost",
        port: int = 6379,
        db: int = 0,
        timeout: int = 2,
        decode_responses: bool = True,
    ) -> "RedisHelper":
        """
        PRIVATE static factory. Creates Redis client and returns helper.
        Call only via public create() method.
        """
        client = redis.Redis(
            host=host,
            port=port,
            db=db,
            socket_connect_timeout=timeout,
            socket_timeout=timeout,
            decode_responses=decode_responses,
        )
        return RedisHelper(client)

    # ---------- PUBLIC factory method ---------- #
    @classmethod
    def create(cls, host: str = "localhost", **kwargs) -> "RedisHelper":
        """
        Public factory: creates and returns RedisHelper with configured client.
        """
        return cls._create_client(host=host, **kwargs)

    # ---------- PUBLIC methods (no access to internal client) ---------- #
    def is_redis_running(self) -> bool:
        """Check Redis connectivity."""
        try:
            return self._client.ping()
        except (ConnectionError, RedisError, TimeoutError) as e:
            print(f"ERROR (ping): {e}")
            return False

    def set_value(self, key: str, value, expiry: int | None = None) -> bool:
        """Set key-value with optional expiry."""
        try:
            if expiry is not None:
                return self._client.setex(key, expiry, value)
            return self._client.set(key, value)
        except (ConnectionError, RedisError, TimeoutError) as e:
            print(f"ERROR (set_value): {e}")
            return False

    def get_value(self, key: str):
        """Get value by key."""
        try:
            return self._client.get(key)
        except (ConnectionError, RedisError, TimeoutError) as e:
            print(f"ERROR (get_value): {e}")
            return None

    # Prevent direct access
    def __getattr__(self, name):
        """Block access to unlisted attributes/methods."""
        if name == '_client':
            raise AttributeError(f"'RedisHelper' object has no attribute '{name}'")
        raise AttributeError(f"'RedisHelper' object has no attribute '{name}'")


if __name__ == "__main__":
    client = RedisHelper.create()
    print(client.is_redis_running())