workers = 2  # You can adjust this based on your machine's capacity
worker_class = "sync"  # Use a synchronous worker class for lower memory usage
worker_connections = 1000  # Adjust based on your application's needs
timeout = 30  # Adjust based on your application's expected response times
keepalive = 2  # Number of requests a worker will process before restarting

# Logging
errorlog = '-'  # Log to stderr
loglevel = 'info'  # Adjust as needed
accesslog = '-'  # Log to stdout

# Bind
bind = "0.0.0.0:8000"  # Adjust the host and port as needed

# Prevent excessive memory usage
limit_request_line = 8190
limit_request_fields = 100
limit_request_field_size = 8190
