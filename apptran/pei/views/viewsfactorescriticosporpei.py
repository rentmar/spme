# views.py
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from spme_estructuracion_pei.models import Pei, FactoresCriticos
from ..serializador.serializadorfactorescriticosporpei import FactoresCriticosSerializer
# from .models import Pei, FactoresCriticos
# from .serializers import FactoresCriticosSerializer

@api_view(['GET'])
def factores_criticos_por_pei(request, pei_id):
    try:
        # Verificar que el PEI existe
        pei = Pei.objects.get(id=pei_id)
        
        # Obtener todos los factores críticos relacionados con este PEI
        # a través de los objetivos específicos
        factores = FactoresCriticos.objects.filter(
            objetivo_especifico__pei=pei
        ).select_related('objetivo_especifico')
        
        serializer = FactoresCriticosSerializer(factores, many=True)
        return Response(serializer.data)
    
    except Pei.DoesNotExist:
        return Response(
            {"error": f"PEI con id {pei_id} no encontrado"},
            status=status.HTTP_404_NOT_FOUND
        )
    
    except Exception as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )