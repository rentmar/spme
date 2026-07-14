from rest_framework.views import APIView, View
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.shortcuts import render
from datetime import datetime
from django.template.loader import render_to_string

from spme_email.tasks.email_tasks import send_templated_email

class TestSimpleEmailView(APIView):
    """
    Endpoint simple para probar envío de email
    
    POST /api/email/test-simple/
    {
        "email": "destinatario@gmail.com"
    }
    """
    permission_classes = [AllowAny]

    def post(self, request):

        destinatario = request.data.get('email')

        try:
            #Crear email
            msg = EmailMultiAlternatives(
                subject='Test simple spme',
                body='correo de prueba texto plano',
                from_email= settings.DEFAULT_FROM_EMAIL,
                to=[destinatario],
            )

            #Agregar una version html
            html = """
            <div style="font-family: Arial; padding: 20px;">
                <h2 style="color: #667eea;">🧪 Email de Prueba</h2>
                <p>Si ves esto, el <strong>endpoint de Django</strong> funciona.</p>
                <hr>
                <small>Enviado desde SPME</small>
            </div>
            """
            msg.attach_alternative(html, "text/html")

            #Envia el correo o dispara una excepcion en casao de falla
            msg.send(fail_silently=False)

            return Response({
                'success': True,
                'message': f'Email enviado a {destinatario}',
                'from': settings.DEFAULT_FROM_EMAIL,
            })
            
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e),
            }, status=500)
        

class PreviewEmailView(View):
    """
    Endpoint para previsualizar templates de email en el navegador.
    
    URLs:
        GET /api/email/preview/welcome/
        GET /api/email/preview/notification/
        GET /api/email/preview/report/
    """
    TEST_CONTEXT = {
        'welcome':{
            'user_name': 'Juan Pérez Rodríguez',
            'login_url': 'http://localhost:5173/login',
            'current_year': datetime.now().year,
        },
        'notification': {
            'user_name': 'María García López',
            'notification_title': 'Indicador Fuera de Rango',
            'notification_message': 'El indicador "Avance Físico" ha superado el umbral del 85%.',
            'action_url': 'http://localhost:5173/dashboard',
            'action_text': 'Ver Indicador',
            'current_year': datetime.now().year,  # Lo usa base.html en el footer
        },
        'report':{
            'user_name': 'Carlos Mendoza',
            'report_title': 'Reporte Mensual - Junio 2024',
            'report_data': {
                'Proyectos Activos': 42,
                'Presupuesto Total': 'Bs. 15,234,567',
                'Ejecutado': 'Bs. 12,845,320 (84.3%)',
                'Tareas Pendientes': 23,
            },
            'generated_at': datetime.now().strftime('%d/%m/%Y %H:%M'),
            'current_year': datetime.now().year,  # Lo usa base.html en el footer
        },
    }
    def get(self, request, template_name=None):

        # Validar que el template existe
        if template_name not in self.TEST_CONTEXT:
            return render(request, 'emails/preview_error.html', {
                'message': f'Template "{template_name}" no encontrado.',
                'available': list(self.TEST_CONTEXT.keys()),
            })

        #Renderiza template con datos de prueba
        return render(
            request,
            f'email/{template_name}.html',
            self.TEST_CONTEXT[template_name]
        )
    
class SendTemplatedEmailView(APIView):
    """
    Envía email usando las plantillas
    
    POST /api/email/send/
    {
        "email": "destinatario@gmail.com",
        "template": "welcome",
        "context": {
            "user_name": "Juan Pérez",
            "login_url": "http://localhost:5173/login"
        }
    }
    """
    permission_classes = [AllowAny]

    def post(self, request):
        destinatario = request.data.get('email')
        template_name = request.data.get('template')
        context = request.data.get('context', {})

        #Agregar la fecha
        context['current_year'] = datetime.now().year

        try:
            #renderizar la plantilla
            html_content = render_to_string(f'email/{template_name}.html', context)

            #texto plano simple
            text_content = f"Hola {context.get('user_name', 'Usuario')}, tienes un mensaje de SPME."

            # Asuntos según template
            subjects = {
                'welcome': '¡Bienvenido a SPME!',
                'notification': context.get('notification_title', 'Notificación SPME'),
                'report': context.get('report_title', 'Reporte SPME'),
            }
            
            # Enviar email
            msg = EmailMultiAlternatives(
                subject=subjects.get(template_name, 'Mensaje SPME'),
                body=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[destinatario],
            )
            msg.attach_alternative(html_content, "text/html")
            msg.send(fail_silently=False)

            return Response({
                'success': True,
                'message': f'Email "{template_name}" enviado a {destinatario}',
            })           
        
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e),
            }, status=500)

class SendAsyncEmailView(APIView):
    """
    Envío ASÍNCRONO (con Celery)
    
    POST /api/email/send-async/
    {
        "email": "destinatario@gmail.com",
        "template": "welcome",
        "context": {
            "user_name": "Juan Pérez",
            "login_url": "http://localhost:5173/login"
        }
    }
    """
    permission_classes = [AllowAny]

    def post(self, request):
        print(request.data)
        destinatario = request.data.get('email')
        template_name = request.data.get('template')
        context = request.data.get('context', {})
        subject = request.data.get('subject')
        #Combrobar si no hay destinatario
        if not destinatario:
            return Response({'success': False, 'error': 'Email requerido'}, status=400)
        
        #Enviar a celery
        task = send_templated_email.delay(
            to_email=destinatario,
            template_name=template_name,
            context=context,
            subject=subject,
        )

        return Response({
                'success': True,
                'message': f'Email "{template_name}" encolado para {destinatario}',
                #'task_id': task.id,
                'status': 'PENDING',
            })



        return Response({'msg':'Envio de email asincrono'})

