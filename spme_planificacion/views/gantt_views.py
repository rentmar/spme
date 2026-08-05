# spme_planificacion/views/gantt_views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from ..services.gantt_service import GanttService

class ProyectosGanttView(APIView):
    def get(self, request):
        service = GanttService()
        return Response(service.get_gantt_data())