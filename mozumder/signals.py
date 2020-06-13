import django.dispatch

log_response = django.dispatch.Signal(providing_args=["response"])
