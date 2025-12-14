from rest_framework import serializers
from app.signer.models import Signer

class SignerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Signer
        fields = '__all__'
