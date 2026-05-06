# views/pei_arbol_view.py
from rest_framework.decorators import api_view
from rest_framework.response import Response
from ..services.composer.chain_composer import ChainComposer
from ..utils.exceptions import (
    ElementoNoEncontradoError,
    ProfundidadInvalidaError,
    TipoElementoNoSoportadoError,
)

from ..utils.utils import parse_bool_param, validar_tipo_indicador

@api_view(['GET'])
def pei_arbol_json(request, tipo, elemento_id):
    """
    Endpoint para obtener el árbol jerárquico en formato JSON.
    
    Útil para debugging, integración con frontend,
    o verificación de estructura antes de generar Word.
    
    Parámetros de URL:
        tipo: 'pei', 'objetivo', 'factor', 'indicador'
        elemento_id: ID del elemento raíz
    
    Parámetros GET:
        profundidad: 0, 1, 2, 'completa' (default: 'completa')
        incluir_indicadores: true/false (default: true)
        incluir_factores: true/false (default: true)
        tipo_indicador: 'cuantitativo', 'cualitativo', 'todos' (default: 'todos')
    
    Respuesta:
        200: Árbol JSON con la estructura jerárquica
        400: Parámetros inválidos
        404: Elemento no encontrado
    """
    try:
        profundidad = request.GET.get('profundidad', 'completa')
        incluir_indicadores = parse_bool_param(
            request.GET.get('incluir_indicadores', 'true')
        )
        incluir_factores = parse_bool_param(
            request.GET.get('incluir_factores', 'true')
        )
        tipo_indicador = validar_tipo_indicador(
            request.GET.get('tipo_indicador', 'TODOS')
        )

        composer = ChainComposer()
        arbol = composer.compose(
            tipo_elemento=tipo,
            elemento_id=elemento_id,
            profundidad=profundidad,
            incluir_indicadores=incluir_indicadores,
            incluir_factores=incluir_factores,
            tipo_indicador=tipo_indicador,
        )

        return Response(arbol)
    
    except ElementoNoEncontradoError as e:
        return Response({'error': e.mensaje, 'codigo': e.codigo}, status=404)
    except (ProfundidadInvalidaError, TipoElementoNoSoportadoError) as e:
        return Response({'error': e.mensaje, 'codigo': e.codigo}, status=400)
    except Exception as e:
        return Response(
            {'error': f'Error inesperado: {str(e)}', 'codigo': 'ERROR_INTERNO'},
            status=500
        )
    