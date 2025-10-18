from rest_framework import serializers

class ReporteConfigSerializer(serializers.Serializer):
    incluir_relaciones = serializers.BooleanField(default=True)
    profundidad = serializers.IntegerField(default=2, min_value=1, max_value=5)
    formato = serializers.ChoiceField(choices=['docx', 'pdf'], default='docx')