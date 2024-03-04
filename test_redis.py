from redis import Redis

redis_host = '2.56.91.74'
r = Redis(redis_host, socket_connect_timeout=1)  # short timeout for the test

r.ping()

print('connected to redis "{}"'.format(redis_host))