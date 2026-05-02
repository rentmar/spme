#views/objetivo_report_view.py
from django.http import FileResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from ..services.composer.chain_composer import ChainComposer
from ..services.pei_word_service import PEIWordService
from ..utils.exceptions import (
    ElementoNoEncontradoError,
    ProfundidadInvalidaError,
    TipoElementoNoSoportadoError,
)
from ..utils.utils import parse_bool_param, generar_filename


@api_view(['GET'])
def objetivo_report_word(request, objetivo_id):
    """Endpoint para generar reporte Word desde un objetivo."""
    try:
        profundidad = request.GET.get('profundidad', 'completa')
        incluir_indicadores = parse_bool_param(
            request.GET.get('incluir_indicadores', 'true')
        )
        incluir_factores = parse_bool_param(
            request.GET.get('incluir_factores', 'true')
        )
        
        composer = ChainComposer()
        arbol = composer.compose(
            tipo_elemento='objetivo',
            elemento_id=objetivo_id,
            profundidad=profundidad,
            incluir_indicadores=incluir_indicadores,
            incluir_factores=incluir_factores,
        )
        
        word_service = PEIWordService()
        doc_bytes = word_service.generate_document(arbol)
        
        filename = generar_filename('objetivo', objetivo_id)
        response = FileResponse(
            doc_bytes,
            content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        )
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
    
    except ElementoNoEncontradoError as e:
        return Response({'error': e.mensaje, 'codigo': e.codigo}, status=404)
    except (ProfundidadInvalidaError, TipoElementoNoSoportadoError) as e:
        return Response({'error': e.mensaje, 'codigo': e.codigo}, status=400)
    except Exception as e:
        return Response(
            {'error': f'Error inesperado: {str(e)}', 'codigo': 'ERROR_INTERNO'},
            status=500
        )