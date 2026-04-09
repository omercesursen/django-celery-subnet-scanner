from celery import shared_task
import ipaddress
from ping3 import ping
from .models import SubnetRequest, PingLog


@shared_task
def process_subnet_ping(request_id):
    try:
        subnet_req = SubnetRequest.objects.get(id=request_id)

        network = ipaddress.ip_network(subnet_req.subnet, strict=False)

        logs_to_create = []

        for ip in network.hosts():
            ip_str = str(ip)

            response = ping(ip_str, timeout=1)

            is_active = False
            if response is not None and response is not False:
                is_active = True

            logs_to_create.append(
                PingLog(
                    subnet_request=subnet_req,
                    ip_address=ip_str,
                    is_active=is_active
                )
            )

        PingLog.objects.bulk_create(logs_to_create)

        return f"{subnet_req.subnet} için ping işlemi tamamlandı."

    except Exception as e:
        return f"Hata oluştu: {str(e)}"