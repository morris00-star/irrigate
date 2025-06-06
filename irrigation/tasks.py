from accounts.models import CustomUser
from irrigation.models import SensorData
from irrigation.sms import SMSService
from django.core.exceptions import ObjectDoesNotExist


def send_notifications_to_all_users():
    try:
        latest_data = SensorData.objects.latest('timestamp')
        users = CustomUser.objects.filter(
            is_active=True,
            phone_number__isnull=False
        ).exclude(phone_number='')

        results = []
        for user in users:
            success, message = SMSService.send_alert(user, latest_data)
            results.append({
                'user': user.username,
                'phone': user.phone_number,
                'status': 'success' if success else 'failed',
                'message': message
            })
        return results

    except ObjectDoesNotExist:
        return {'error': 'No sensor data available'}
    except Exception as e:
        return {'error': str(e)}
