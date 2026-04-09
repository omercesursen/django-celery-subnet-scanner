from django.db import models


class SubnetRequest(models.Model):
    subnet = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"İstek: {self.subnet} - Tarih: {self.created_at.strftime('%Y-%m-%d %H:%M')}"


class PingLog(models.Model):

    subnet_request = models.ForeignKey(SubnetRequest, related_name='logs', on_delete=models.CASCADE)

    ip_address = models.GenericIPAddressField()

    is_active = models.BooleanField(default=False)

    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        status = "Aktif" if self.is_active else "Pasif"
        return f"{self.ip_address} - {status}"