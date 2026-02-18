from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view

def validar_lista_ids(ids):
    if not isinstance(ids, list):
        return None, Response({'error': 'El campo "ids" debe ser una lista'}, status=status.HTTP_400_BAD_REQUEST)
    if not ids:
        return None, Response({'error': 'La lista de IDs no puede estar vacía'}, status=status.HTTP_400_BAD_REQUEST)
    try:
        return [int(id) for id in ids], None
    except:
        return None, Response({'error': 'Todos los IDs deben ser números enteros'}, status=status.HTTP_400_BAD_REQUEST)

def procesar_consulta_indicadores(modelo, serializer_class, tipo, request):
    ids = request.data.get('ids', [])
    ids_validados, error = validar_lista_ids(ids)
    if error:
        return error
    
    queryset = modelo.objects.filter(id__in=ids_validados)
    encontrados = set(queryset.values_list('id', flat=True))
    no_encontrados = set(ids_validados) - encontrados
    
    return Response({
        'tipo': f'indicador_{tipo}',
        'total_solicitados': len(ids_validados),
        'total_encontrados': len(queryset),
        'ids_no_encontrados': list(no_encontrados) if no_encontrados else [],
        'resultados': serializer_class(queryset, many=True).data
    })