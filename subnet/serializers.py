import ipaddress
from rest_framework import serializers
from .models import SubnetRequest


class SubnetRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubnetRequest
        fields = ['id', 'subnet', 'created_at']

    def validate_subnet(self, value):
        try:
            network = ipaddress.ip_network(value, strict=False)
        except ValueError:
            raise serializers.ValidationError(
                "Geçersiz format! Lütfen geçerli bir IPv4 veya IPv6 subnet'i girin (Örn: 10.0.0.0/24).")

        if network.version == 4:
            if network.prefixlen < 24:
                raise serializers.ValidationError(
                    "IPv4 için girilebilecek en büyük ağ maskesi /24'tür. Daha büyük bir ağ taranamaz.")

        elif network.version == 6:
            if network.prefixlen < 64:
                raise serializers.ValidationError(
                    "IPv6 için girilebilecek en büyük ağ maskesi /64'tür. Daha büyük bir ağ taranamaz.")

        return str(network)