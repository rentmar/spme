# views/pei_report_view.py
from django.http import FileResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from ..services.composer.chain_composer import ChainComposer
from ..services.pei_word_service import PEIWordService
from ..utils.exceptions import (
    ElementoNoEncontradoError, ProfundidadInvalidaError,
    TipoElementoNoSoportadoError, GeneracionWordError,
)
from ..utils.utils import parse_bool_param, generar_filename, validar_tipo_indicador

@api_view(['GET'])
def pei_report_word(request, pei_id):
    try:
        profundidad = request.GET.get('profundidad', 'completa')
        incluir_indicadores = parse_bool_param(request.GET.get('incluir_indicadores', 'true'))
        incluir_factores = parse_bool_param(request.GET.get('incluir_factores', 'true'))
        tipo_indicador = validar_tipo_indicador(request.GET.get('tipo_indicador', 'TODOS'))
        
        composer = ChainComposer()
        arbol = composer.compose(
            tipo_elemento='pei', elemento_id=pei_id, profundidad=profundidad,
            incluir_indicadores=incluir_indicadores, incluir_factores=incluir_factores,
            tipo_indicador=tipo_indicador,
        )
        #DEbug, ver la estrucutura del arbol
        import json
        print("=== ÁRBOL GENERADO ===")
        print(json.dumps(arbol, indent=2, default=str))
        print("======================")

        word_service = PEIWordService()
        doc_bytes = word_service.generate_document(arbol)
        filename = generar_filename('pei', pei_id) 
        
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
    except GeneracionWordError as e:
        return Response({'error': e.mensaje, 'codigo': e.codigo}, status=500)
    except Exception as e:
        return Response({'error': f'Error inesperado: {str(e)}', 'codigo': 'ERROR_INTERNO'}, status=500)