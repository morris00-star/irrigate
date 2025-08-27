import csv
import datetime
import json
import os
from datetime import datetime

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, Http404, JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import FileResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from accounts.models import CustomUser
from .models import SensorData, SystemConfiguration
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.utils.timezone import localtime
import pytz
import logging

from .services.knowledge.guide_bot import IrrigationGuide
from .sms import SMSService

logger = logging.getLogger(__name__)


@login_required
def about(request):
    return render(request, 'irrigation/about.html')


@login_required
def contact(request):
    return render(request, 'irrigation/contact.html')


@login_required
def ask_bot(request):
    return render(request, 'irrigation/chatbot.html')


@login_required
def help(request):
    return render(request, 'irrigation/help.html')


@login_required
def dashboard(request):
    try:
        config = SystemConfiguration.objects.get(user=request.user)
        emergency_active = config.emergency_stop
    except SystemConfiguration.DoesNotExist:
        emergency_active = False
    sensor_data = SensorData.objects.filter(user=request.user).order_by('-timestamp')[:20]

    context = {
        'emergency_active': emergency_active,
        'sensor_data': sensor_data,
    }
    return render(request, 'irrigation/dashboard.html', context)


@login_required
def download_user_manual_confirm(request):
    return render(request, 'irrigation/download_user_manual_confirm.html')


@login_required
def download_user_manual(request):
    if request.method == 'POST':
        confirm = request.POST.get('confirm', 'no')
        if confirm == 'yes':
            try:
                file_path = os.path.join(settings.BASE_DIR, 'irrigation', 'static', 'documents', 'user_guide.pdf')
                if os.path.exists(file_path):
                    response = FileResponse(open(file_path, 'rb'), content_type='application/pdf')
                    response['Content-Disposition'] = 'attachment; filename="user_guide.pdf"'
                    return response
                else:
                    raise Http404("User manual not found")
            except Exception as e:
                return render(request, 'irrigation/error.html',
                              {'error_message': 'An error occurred while downloading the manual.'})
        else:
            return redirect('dashboard')
    else:
        return redirect('download_user_manual_confirm')


def send_support_message(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')

        # Construct the email subject and body
        subject = f"Support Request from {name}"
        body = f"""
        Name: {name}
        Email: {email}
        Message: {message}
        """

        # Send the email
        send_mail(
            subject=subject,
            message=body,
            from_email=settings.DEFAULT_FROM_EMAIL,  # Use the default email address
            recipient_list=[settings.SUPPORT_EMAIL],  # Send to the support email
            fail_silently=False,
        )

        # Notify the user that the message was sent
        messages.success(request, "Your message has been sent to support. We'll get back to you soon!")
        return redirect('help')

    return redirect('help')


@login_required
def visualize_data(request):
    """
    Render the visualization page.
    """
    return render(request, 'irrigation/visualize.html')


@login_required
def privacy_policy(request):
    return render(request, 'irrigation/privacy.html')


@login_required
def terms_of_service(request):
    return render(request, 'irrigation/terms.html')


@login_required
def get_sensor_data(request):
    data_type = request.GET.get('type', 'temperature')  # Default to temperature
    user = request.user

    # Fetch the latest 50 sensor data entries for the logged-in user
    sensor_data = SensorData.objects.filter(user=user).order_by('-timestamp')[:50]

    # Prepare data for the chart (timestamps in UTC)
    labels = [data.timestamp.isoformat() + 'Z' for data in sensor_data]  # Add 'Z' to indicate UTC
    values = [getattr(data, data_type) for data in sensor_data]

    return JsonResponse({
        'labels': labels,
        'values': values
    })


@login_required
def download_data(request):
    """
    Download sensor data in CSV or Excel format with timestamps in East African Time (EAT).
    """
    format = request.GET.get('format', 'csv')  # Default to CSV

    # Fetch sensor data for the logged-in user
    sensor_data = SensorData.objects.filter(user=request.user).order_by('-timestamp')

    # Define East African Time (EAT) timezone
    eat_timezone = pytz.timezone('Africa/Nairobi')

    if format == 'csv':
        # Create CSV response
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="sensor_data.csv"'

        writer = csv.writer(response)
        writer.writerow(['Timestamp (EAT)', 'Temperature', 'Humidity', 'Moisture', 'Pump Status', 'Valve Status'])

        for data in sensor_data:
            # Convert UTC timestamp to East African Time (EAT)
            timestamp_eat = localtime(data.timestamp, timezone=eat_timezone).strftime('%Y-%m-%d %H:%M:%S')
            writer.writerow([
                timestamp_eat,  # Timestamp in EAT
                data.temperature,
                data.humidity,
                data.moisture,
                data.pump_status,
                data.valve_status
            ])

        return response

    elif format == 'excel':
        # Create Excel response (requires openpyxl)
        from openpyxl import Workbook

        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="sensor_data.xlsx"'

        wb = Workbook()
        ws = wb.active
        ws.title = "Sensor Data"

        # Add headers
        ws.append(['Timestamp (EAT)', 'Temperature', 'Humidity', 'Moisture', 'Pump Status', 'Valve Status'])

        # Add data
        for data in sensor_data:
            # Convert UTC timestamp to East African Time (EAT)
            timestamp_eat = localtime(data.timestamp, timezone=eat_timezone).strftime('%Y-%m-%d %H:%M:%S')
            ws.append([
                timestamp_eat,  # Timestamp in EAT
                data.temperature,
                data.humidity,
                data.moisture,
                data.pump_status,
                data.valve_status
            ])

        wb.save(response)
        return response

    else:
        return HttpResponse("Invalid format", status=400)


@login_required
def control_panel(request):
    """
    View for the control panel page.
    """
    return render(request, 'irrigation/control_panel.html')


def keep_alive(request):
    return JsonResponse({"status": "OK"}, status=200)


class EnvCheckView(LoginRequiredMixin, View):
    """View to verify environment variable access"""

    def get(self, request, *args, **kwargs):
        env_vars = {
            'DEBUG': str(settings.DEBUG),
            'ENVIRONMENT': os.getenv('ENVIRONMENT', 'Not set'),
            'DB_HOST': os.getenv('DB_HOST', 'Not set'),
            'SECRET_KEY': '*****' if os.getenv('SECRET_KEY') else 'Not set',
            'EGOSMS_CONFIG': {
                'API_URL': settings.EGOSMS_CONFIG.get('API_URL', 'Not set'),
                'USERNAME': '*****' if settings.EGOSMS_CONFIG.get('USERNAME') else 'Not set',
                'TEST_MODE': str(settings.EGOSMS_CONFIG.get('TEST_MODE', 'Not set'))
            }
        }

        logger.info("Environment variables checked")
        return JsonResponse({
            'status': 'success',
            'environment_vars': env_vars
        })


@csrf_exempt
def trigger_notifications(request):
    """Endpoint for cron service to trigger SMS notifications"""
    # Authentication
    if request.headers.get('X-CRON-TOKEN') != settings.CRON_SECRET_KEY:
        logger.warning("Unauthorized cron attempt")
        return JsonResponse({'status': 'error', 'message': 'Unauthorized'}, status=401)

    # Process notifications
    try:
        latest_data = SensorData.objects.latest('timestamp')
        users = CustomUser.objects.filter(
            is_active=True,
            phone_number__isnull=False
        ).exclude(phone_number='')

        results = []
        for user in users:
            success, msg = SMSService.send_alert(user, latest_data)
            results.append({
                'user': user.username,
                'phone': user.phone_number[:4] + '*****',  # Partial masking
                'status': 'success' if success else 'failed',
                'message': msg
            })
            logger.info(f"Processed {user.username}")

        return JsonResponse({'status': 'success', 'results': results})

    except ObjectDoesNotExist:
        logger.error("No sensor data available")
        return JsonResponse({'status': 'error', 'message': 'No sensor data'}, status=404)
    except Exception as e:
        logger.error(f"Cron job failed: {str(e)}")
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)



@csrf_exempt
@require_POST
def chatbot_view(request):
    """API endpoint for chatbot requests with enhanced error handling"""
    try:
        # Log the request for debugging
        logger.info(f"Chatbot request received: {request.method}, Content-Type: {request.content_type}")

        # Parse the request body
        try:
            if request.content_type == 'application/json':
                data = json.loads(request.body)
            else:
                data = request.POST

            query = data.get('query', '').strip()
        except Exception as e:
            logger.error(f"Error parsing request data: {str(e)}")
            return JsonResponse({
                'error': 'Invalid request data',
                'message': 'Please provide valid data'
            }, status=400)

        if not query:
            logger.warning("Empty query received")
            return JsonResponse({
                'error': 'Empty query',
                'message': 'Please enter a question or command'
            }, status=400)

        # Log the query
        logger.info(f"Processing query: {query}")

        # Import here to avoid circular imports
        try:
            guide = IrrigationGuide()
            response_data = guide.get_help_response(query, request)
        except Exception as e:
            logger.error(f"Error creating IrrigationGuide: {str(e)}")
            return JsonResponse({
                'error': 'Server configuration error',
                'message': 'Unable to process your request at this time'
            }, status=500)

        # Add typing simulation metadata
        response_data['typing_duration'] = min(len(query) * 0.05, 2.5)
        response_data['response_time'] = datetime.now().strftime('%H:%M:%S')

        # Log successful response
        logger.info(f"Response generated for query: {query}")

        return JsonResponse(response_data)

    except Exception as e:
        # Log the full error with traceback
        logger.error(f"Unexpected error in chatbot_view: {str(e)}", exc_info=True)

        return JsonResponse({
            'error': 'Internal server error',
            'message': 'An unexpected error occurred while processing your request'
        }, status=500)
