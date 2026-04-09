from rest_framework import viewsets, status
from rest_framework.response import Response
from django.core.cache import cache
from .models import SubnetRequest
from .serializers import SubnetRequestSerializer
from .tasks import process_subnet_ping


class SubnetRequestViewSet(viewsets.ModelViewSet):
    queryset = SubnetRequest.objects.all().order_by('-created_at')
    serializer_class = SubnetRequestSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        self.perform_create(serializer)

        process_subnet_ping.delay(serializer.instance.id)

        return Response(
            {
                "mesaj": "Subnet kabul edildi. Ping işlemi arka planda sıraya alındı (Kuyrukta).",
                "istek_detayi": serializer.data
            },
            status=status.HTTP_201_CREATED
        )

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()

        cache_key = f"subnet_ping_logs_{instance.id}"

        cached_logs = cache.get(cache_key)

        if cached_logs:
            return Response({
                "veri_kaynagi": "REDIS CACHE (Önbellek)",
                "istek": self.get_serializer(instance).data,
                "ping_sonuclari": cached_logs
            })

        logs = instance.logs.all().values('ip_address', 'is_active', 'timestamp')
        log_list = list(logs)

        if log_list:
            cache.set(cache_key, log_list, timeout=300)

        return Response({
            "veri_kaynagi": "POSTGRESQL DB (Veritabanı)",
            "istek": self.get_serializer(instance).data,
            "ping_sonuclari": log_list
        })