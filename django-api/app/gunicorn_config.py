workers = 2
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2

# Logging
errorlog = '-'
loglevel = 'info'
accesslog = '-'

# Bind
bind = "127.0.0.1:8000"

# Prevent excessive memory usage
limit_request_line = 8190
limit_request_fields = 100
limit_request_field_size = 8190
