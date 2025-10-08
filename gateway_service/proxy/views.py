from django.http import HttpResponse, JsonResponse
from django.core.cache import cache
import requests
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    print(f"got hit from========={ip}")
    return ip


SERVICE_MAP = settings.SERVICE_MAP


@csrf_exempt
def dynamic_proxy_handler(request, service_name, service_path):
    ip = get_client_ip(request)
    rate_limit_key = f"rate_limit:{ip}"
    
    RATE_LIMIT = settings.RATE_LIMIT
    TIMEOUT = settings.RATE_LIMIT_TIMEOUT

    request_count = cache.get(rate_limit_key, 0)
    
    if request_count >= RATE_LIMIT:
        return JsonResponse({"error": "Too many requests"}, status=429)

    cache.set(rate_limit_key, request_count + 1, timeout=TIMEOUT)

    print(SERVICE_MAP)
    if service_name not in SERVICE_MAP:
        return JsonResponse({"error": "Service not found"}, status=404)
    

    print('Came to this far.')
    # now passing the request to container after all the validation.
    try:
        internal_url = f"{SERVICE_MAP[service_name]}/{service_path}"
        method = request.method.lower()
        headers = dict(request.headers)
        
        response = requests.request(
            method,
            internal_url,
            headers=headers,
            data=request.body,
            params=request.GET
        )
        
        return HttpResponse(
            response.content,
            status=response.status_code,
            content_type=response.headers.get('Content-Type')
        )

    except Exception as e:
        return JsonResponse({"error": f"Internal service communication error: {e}"}, status=502)