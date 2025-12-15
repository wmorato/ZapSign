# D:\Projetos\DesafioTecnico\ZapSign\backend\app\company\admin.py
from django.contrib import admin
from .models import Company, UserProfile


# Inline para ver os usuários vinculados (opcional, mas útil)
class UserProfileInline(admin.TabularInline):
    model = UserProfile
    extra = 0
    can_delete = False
    fields = ("user",)
    readonly_fields = ("user",)


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ("name", "apiToken", "created_at")
    search_fields = ("name", "apiToken")
    readonly_fields = ("created_at", "last_updated_at")
    inlines = [UserProfileInline]  # Mostra os usuários da empresa
