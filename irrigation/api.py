from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import SensorData, ControlCommand, Threshold
from django.core.cache import cache
import logging
logger = logging.getLogger(__name__)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def receive_sensor_data(request):
    """
    API endpoint to receive sensor data from the NodeMCU.
    """
    if request.method == 'POST':
        try:
            data = request.data
            # Save sensor data to the database
            SensorData.objects.create(
                temperature=data.get('temperature'),
                humidity=data.get('humidity'),
                moisture=data.get('moisture'),
                pump_status=data.get('pump_status'),
                valve_status=data.get('valve_status'),
                threshold=data.get('threshold'),
                user=request.user
            )
            return Response({"status": "success"}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"status": "error", "message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    return Response({"status": "error", "message": "Invalid request method"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def control_system(request):
    """
    API endpoint to control the pump, valve, and threshold.
    """
    action = request.data.get('action')
    user_id = request.user.id

    if action == 'toggle_pump':
        pump_state = cache.get(f'pump_state_{user_id}', 'off')
        new_state = 'on' if pump_state == 'off' else 'off'
        cache.set(f'pump_state_{user_id}', new_state, timeout=None)
        # Save the control command to the database
        ControlCommand.objects.create(pump_status=(new_state == 'on'), valve_status=False)
        return Response({"pump": new_state})
    elif action == 'toggle_valve':
        valve_state = cache.get(f'valve_state_{user_id}', 'closed')
        new_state = 'open' if valve_state == 'closed' else 'closed'
        cache.set(f'valve_state_{user_id}', new_state, timeout=None)
        # Save the control command to the database
        ControlCommand.objects.create(pump_status=False, valve_status=(new_state == 'open'))
        return Response({"valve": new_state})
    elif action == 'set_threshold':
        threshold = request.data.get('threshold')
        if threshold is not None:
            # Save the threshold to the database
            Threshold.objects.create(threshold=threshold, user=request.user)
            return Response({"threshold": threshold})
        else:
            return Response({"error": "Threshold value is required"}, status=status.HTTP_400_BAD_REQUEST)
    elif action == 'get_state':
        # Return the current state of the pump, valve, and threshold
        pump_state = cache.get(f'pump_state_{user_id}', 'off')
        valve_state = cache.get(f'valve_state_{user_id}', 'closed')
        latest_threshold = Threshold.objects.filter(user=request.user).order_by('-timestamp').first()
        threshold = latest_threshold.threshold if latest_threshold else 30  # Default threshold is 30
        return Response({
            "pump": pump_state,
            "valve": valve_state,
            "threshold": threshold
        })
    else:
        return Response({"error": "Invalid action"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_system_status(request):
    """
    API endpoint to fetch the current system status (pump, valve, moisture level, and threshold).
    """
    user_id = request.user.id
    pump_state = cache.get(f'pump_state_{user_id}', 'off')
    valve_state = cache.get(f'valve_state_{user_id}', 'closed')
    latest_sensor_data = SensorData.objects.filter(user=request.user).order_by('-timestamp').first()
    moisture_level = latest_sensor_data.moisture if latest_sensor_data else 0
    latest_threshold = Threshold.objects.filter(user=request.user).order_by('-timestamp').first()
    threshold = latest_threshold.threshold if latest_threshold else 50  # Default threshold is 50
    return Response({
        "pump": pump_state,
        "valve": valve_state,
        "moisture": moisture_level,
        "threshold": threshold
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_threshold(request):
    """
    Fetch the current moisture threshold for the authenticated user.
    """
    try:
        latest_threshold = Threshold.objects.filter(user=request.user).order_by('-timestamp').first()
        threshold = latest_threshold.threshold if latest_threshold else 30  # Default threshold is 30
        return Response({"threshold": threshold}, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"Error fetching threshold: {e}")
        return Response({"error": "Failed to fetch threshold"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def set_threshold(request):
    """
    Set or update the moisture threshold for the authenticated user.
    """
    try:
        threshold_value = request.data.get('threshold')
        if threshold_value is not None:
            # Save the threshold to the database
            Threshold.objects.create(threshold=threshold_value, user=request.user)
            return Response({"status": "success", "threshold": threshold_value}, status=status.HTTP_201_CREATED)
        else:
            return Response({"error": "Threshold value is required"}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(f"Error setting threshold: {e}")
        return Response({"error": "Failed to set threshold"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
