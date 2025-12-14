from rest_framework import serializers
from app.document.models import Document
from app.ai.models import DocumentAnalysis
from app.signer.models import Signer  # Importar o modelo Signer


class DocumentAnalysisSerializer(serializers.ModelSerializer):
    """
    Serializer para o modelo DocumentAnalysis.
    """

    class Meta:
        model = DocumentAnalysis
        fields = [
            "status",
            "summary",
            "missing_topics",
            "insights",
            "model_used",
            "created_at",
            "last_updated_at",
        ]
        read_only_fields = fields  # Todos os campos são somente leitura para a API


class SignerCreateUpdateSerializer(serializers.ModelSerializer):  # <--- NOVO SERIALIZER
    """
    Serializer para criar e atualizar signatários, usado aninhado no DocumentSerializer.
    Permite receber 'id' para identificar signatários existentes.
    """

    id = serializers.IntegerField(
        required=False, allow_null=True
    )  # ID é opcional para criação, mas presente para atualização

    class Meta:
        model = Signer
        fields = ["id", "name", "email", "externalID", "token", "status"]
        read_only_fields = (
            "token",
            "status",
        )  # Token e status são gerenciados pelo backend/ZapSign


class DocumentSerializer(serializers.ModelSerializer):
    signers_db = serializers.SerializerMethodField(read_only=True)
    ai_analysis = DocumentAnalysisSerializer(read_only=True, allow_null=True)
    # Adicionado o serializer de signatários para escrita
    signers = SignerCreateUpdateSerializer(
        many=True, required=False, source="signers_set"
    )  # <--- MODIFICADO

    class Meta:
        model = Document
        fields = [
            "id",
            "openID",
            "token",
            "name",
            "status",
            "created_at",
            "last_updated_at",
            "created_by",
            "company",
            "externalID",
            "url_pdf",  # <--- ADICIONADO: url_pdf agora é um campo do modelo
            "signers_db",
            "ai_analysis",
            "signers",  # <--- ADICIONADO: para permitir a escrita de signatários
        ]
        read_only_fields = (
            "openID",
            "token",
            "status",
            "created_at",
            "last_updated_at",
            "signers_db",  # signers_db continua sendo read-only, 'signers' é para escrita
            "company",  # Company is assigned automatically based on user
        )

    def get_signers_db(self, obj):
        signers_queryset = obj.signers.all()
        return [
            {
                "id": s.id,
                "name": s.name,
                "email": s.email,
                "status": s.status,
                "externalID": s.externalID,
                "token": s.token,
            }
            for s in signers_queryset
        ]

    # Adicionado método create para lidar com signatários aninhados
    def create(self, validated_data):
        document = Document.objects.create(**validated_data)
        return document

    # Adicionado método update para lidar com signatários aninhados
    def update(self, instance, validated_data):
        signers_data = validated_data.pop("signers_set", [])
        signers_to_remove_ids = self.context.get(
            "signers_to_remove_ids", []
        )  # Obtém IDs para remover do contexto

        # Atualiza campos do documento
        instance.name = validated_data.get("name", instance.name)
        instance.company = validated_data.get("company", instance.company)
        instance.url_pdf = validated_data.get("url_pdf", instance.url_pdf)
        instance.externalID = validated_data.get("externalID", instance.externalID)
        instance.save()

        # Lógica para remover signatários
        for signer_id in signers_to_remove_ids:
            try:
                signer_to_delete = Signer.objects.get(id=signer_id, document=instance)
                # A remoção na ZapSign será tratada na view
                signer_to_delete.delete()
            except Signer.DoesNotExist:
                pass  # Signatário já pode ter sido removido ou não existe

        # Lógica para criar ou atualizar signatários
        for signer_data in signers_data:
            signer_id = signer_data.get("id")
            if signer_id:  # Signatário existente, tenta atualizar
                try:
                    signer_instance = Signer.objects.get(
                        id=signer_id, document=instance
                    )
                    for attr, value in signer_data.items():
                        setattr(signer_instance, attr, value)
                    signer_instance.save()
                except Signer.DoesNotExist:
                    # Se o ID foi fornecido mas não existe, pode ser um erro ou um novo signatário com ID inválido
                    # Por simplicidade, vamos ignorar e deixar a view lidar com a criação se for o caso
                    pass
            else:  # Novo signatário, cria
                Signer.objects.create(document=instance, **signer_data)
                # A adição na ZapSign será tratada na view

        return instance
