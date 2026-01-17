import requests
from dotenv import load_dotenv
import os
import json
from datetime import timedelta
import redis
from requests_ratelimiter import LimiterSession
import hashlib

load_dotenv(".env")

# Redis connection
def redis_connect():
    try:
        client = redis.Redis(
            host="localhost",
            port=6379,
            db=0,
            decode_responses=True,
            socket_timeout=5,
        )
        if client.ping():
            return client
    except redis.ConnectionError:
        print("Redis connection failed")
        return None

redis_client = redis_connect()

# Rate-limited session (5 requests per second)
session = LimiterSession(per_minute=1)

PINCODE = "580031"

def get_cache_key(pincode):
    """Generate cache key"""
    return f"weather:{pincode}"

def get_from_cache(key):
    """Get data from Redis cache"""
    if redis_client:
        data = redis_client.get(key)
        if data:
            return json.loads(data)
    return None

def set_to_cache(key, value, ttl_seconds=3600):
    """Set data to Redis cache with TTL (default 1 hour)"""
    if redis_client:
        return redis_client.setex(
            key,
            timedelta(seconds=ttl_seconds),
            json.dumps(value)
        )
    return False

def fetch_weather_data(pincode):
    """Fetch weather data with caching and rate limiting"""
    cache_key = get_cache_key(pincode)
    
    # Try cache first
    cached_data = get_from_cache(cache_key)
    if cached_data:
        print("Data served from cache")
        return cached_data
    
    # If not cached, fetch from API with rate limiting
    url = f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{pincode},INDIA?key={os.getenv('API_KEY')}"
    
    response = session.get(url)
    data = response.json()
    
    # Cache the response
    if response.status_code == 200:
        set_to_cache(cache_key, data, ttl_seconds=1800)  # Cache for 30 minutes
        print("Data fetched from API and cached")
    
    return data

# Usage
data = fetch_weather_data(PINCODE)

selected_data = {key: data[key] for key in ['resolvedAddress', 'address', 'timezone', 'description']}
for key, value in selected_data.items():
    print(f"{key}: {value}")
