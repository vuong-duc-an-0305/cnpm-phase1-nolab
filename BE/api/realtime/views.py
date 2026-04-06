"""
Dashboard Statistics API
Phase 4: Real-time dashboard metrics
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from api.realtime.notifications import get_online_users_count
from datetime import datetime


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_realtime_stats(request):
    """
    Lấy real-time statistics cho dashboard
    
    GET /api/dashboard/realtime-stats/
    
    Returns:
    - online_users: Số users đang online
    - server_time: Thời gian server
    """
    try:
        data = {
            'online_users': get_online_users_count(),
            'server_time': datetime.now().isoformat(),
        }
        
        return Response(data, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
