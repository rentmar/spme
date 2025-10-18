from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import FileResponse
from spme_proyectos_reportes.services.proyecto_report_service import ProyectoReportService

class ProyectoReportAllView(APIView):
    def get(self, request, proyecto_id):
        try:
            service = ProyectoReportService(proyecto_id)
            path = service.build_report()
            return FileResponse(open(path, 'rb'), as_attachment=True, filename=path.split('/')[-1])
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
