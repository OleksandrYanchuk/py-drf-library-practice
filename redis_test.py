import redis

# Replace with your Redis host and port
redis_host = 'localhost'
redis_port = 6379

try:
    client = redis.Redis(host=redis_host, port=redis_port)
    client.ping()
    print('Successfully connected to Redis server.')
except redis.exceptions.ConnectionError as e:
    print(f'Failed to connect to Redis server: {e}')
