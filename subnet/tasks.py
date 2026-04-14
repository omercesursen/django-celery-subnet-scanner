from celery import shared_task
from django.conf import settings
from .models import SubnetRequest, PingLog
import ipaddress
from ping3 import ping
import datetime
from concurrent.futures import ThreadPoolExecutor


def check_single_ip(ip_str):
    try:
        delay = ping(str(ip_str), timeout=1)
        is_active = delay is not None and delay is not False
        return {'ip_address': str(ip_str), 'is_active': is_active}
    except Exception:
        return {'ip_address': str(ip_str), 'is_active': False}

@shared_task
def process_subnet_ping(request_id):
    try:
        subnet_req = SubnetRequest.objects.get(id=request_id)
        network = ipaddress.ip_network(subnet_req.subnet, strict=False)

        max_workers = getattr(settings, 'CONCURRENT_PING_LIMIT', 100)

        ip_list = [str(ip) for ip in network.hosts()]
        results = []

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            for result in executor.map(check_single_ip, ip_list):
                results.append(
                    PingLog(
                        subnet_request=subnet_req,
                        ip_address=result['ip_address'],
                        is_active=result['is_active'],
                        timestamp=datetime.datetime.now()
                    )
                )
        PingLog.objects.bulk_create(results)

        return f"{len(results)} adet IP tarandı. Hedef: {subnet_req.subnet}"

    except Exception as e:
        return f"Hata oluştu: {str(e)}"