from rest_framework import serializers
from django.contrib.auth.models import User
from app.company.models import Company, UserProfile


class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True)
    company_name = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ("email", "password", "company_name")

    def validate_email(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("This email is already registered.")
        return value

    def create(self, validated_data):
        email = validated_data["email"]
        password = validated_data["password"]
        company_name = validated_data["company_name"]

        # 1. Create User (username = email)
        user = User.objects.create_user(username=email, email=email, password=password)

        # 2. Find or Create Company
        # For this requirement, we create a new company automatically if the user registers.
        # But if we want to support inviting users to existing companies, logic would be different.
        # The prompt says: "Cria um Usuário novo + Cria uma Empresa nova automaticamente."
        company = Company.objects.create(name=company_name)

        # 3. Create UserProfile
        UserProfile.objects.create(user=user, company=company)

        return user
