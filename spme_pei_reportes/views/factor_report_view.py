#views/factor_report_view.py
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
from ..utils.utils import generar_filename


@api_view(['GET'])
def factor_report_word(request, factor_id):
    """Endpoint para generar reporte Word desde un factor crítico."""
    try:
        profundidad = request.GET.get('profundidad', 'completa')
        
        composer = ChainComposer()
        arbol = composer.compose(
            tipo_elemento='factor',
            elemento_id=factor_id,
            profundidad=profundidad,
        )
        
        word_service = PEIWordService()
        doc_bytes = word_service.generate_document(arbol)
        
        filename = generar_filename('factor', factor_id)
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