import time
from prometheus_client import Counter, Histogram, Info
from flask import request

METRICS_REQUEST_LATENCY = Histogram(
    "app_request_latency_seconds", "Application Request Latency", ["method", "endpoint"]
)

METRICS_REQUEST_COUNT = Counter(
    "app_request_count",
    "Application Request Count",
    ["method", "endpoint", "http_status"],
)

METRICS_INFO = Info("app_version", "Application Version")

def before_request():
    request._prometheus_metrics_request_start_time = time.time()


def after_request(response):
    request_latency = time.time() - request._prometheus_metrics_request_start_time
    METRICS_REQUEST_LATENCY.labels(request.method, request.path).observe(
        request_latency
    )
    METRICS_REQUEST_COUNT.labels(
        request.method, request.path, response.status_code
    ).inc()
    return response

def register_metrics(app, app_version=None, app_config=None):
    app.before_request(before_request)
    app.after_request(after_request)
    METRICS_INFO.info({"version": "1", "config": "develop"})
