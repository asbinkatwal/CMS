from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import logout ,get_user_model
from rest_framework.permissions import AllowAny , IsAuthenticated
from .serializers import RegisterSerializer, LoginSerializer, MenuSerializer ,VoteSerializer
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from canteen.models import User
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from datetime import datetime, time , date
from .models import Vote, menu
from .permissions import IsCanteenAdmin , IsSuperUser , IsCanteenAdminOrSuperUser
import pandas as pd
from django.http import HttpResponse, JsonResponse, FileResponse, Http404
from io import BytesIO
from reportlab.pdfgen import canvas
User = get_user_model()
from .tasks import generate_report_task
from canteen_management_system.celery import app
from celery.result import AsyncResult
from django.conf import settings
import os
from django.db.models import Count
from django.db.models.functions import TruncMonth
from django.utils import timezone
from datetime import timedelta
from django.utils.dateparse import parse_date

@api_view(['POST'])
@permission_classes([AllowAny])  
def register_user(request):
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        send_mail(
            subject='Welcome to the Canteen Management System',
            message=f"Hi {user.username},\n\nThank you for registering! Your account has been successfully created.",
            from_email='katwalasbin80@gmail.com', 
            recipient_list=[user.email],
            fail_silently=False,
        )
        return Response({"message": "User registered successfully"}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsSuperUser]) 
def activate_staff_user(request):
    user_id = request.data.get('user_id')
    action = request.data.get('action')  

    if not user_id or action not in ['activate', 'deactivate']:
        return Response(
            {"error": "user_id and action ('activate' or 'deactivate') are required."},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)


    if action == "activate":
        user.is_active = True
        user.is_staff = True
        msg = "User activated and staff status granted."
    else:
        user.is_active = False
        user.is_staff = False
        msg = "User deactivated and staff status revoked."

    user.save()

    return Response({
        "message": msg,
        "user": {
            "id": user.id,
            "username": user.username,
            "is_active": user.is_active,
            "is_staff": user.is_staff
        }
    }, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([AllowAny])
def login_user(request):
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data 
        refresh = RefreshToken.for_user(user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'username': user.username,
            'role': user.get_role_display(),
        }, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_user(request):
    logout(request)  
    return Response({"message": "Logged out successfully."}, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsAuthenticated])  
def request_reset_email(request):
    email = request.data.get('email')
    users = User.objects.filter(email=email)
    if not users.exists():
        return Response({'error': 'User not found'}, status=404)
    user = users.first()
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    reset_link = f"http://localhost:8000/reset-password/{uid}/{token}/"

    send_mail(
        subject="Password Reset Request",
        message=f"Click the link to reset your password: {reset_link}",
        from_email=None,
        recipient_list=[email],
    )
    return Response({"message": "Password reset link sent."})


@api_view(['POST'])
@permission_classes([IsAuthenticated])  
def reset_password(request, uid, token):
    try:
        uid = force_str(urlsafe_base64_decode(uid))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        return Response({'error': 'Invalid link'}, status=400)

    if not default_token_generator.check_token(user, token):
        return Response({'error': 'Token expired or invalid'}, status=400)
    new_password = request.data.get('password')

    if not new_password:
        return Response({'error': 'New password is required'}, status=400)
    user.set_password(new_password)
    user.save()
    return Response({'message': 'Password reset successful'})

@api_view(['POST'])
@permission_classes([IsAuthenticated, IsCanteenAdminOrSuperUser])
def create_menu(request):
    serializer = MenuSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({
            "message": "Menu created successfully",
            "data": serializer.data
        }, status=status.HTTP_201_CREATED)
    return Response({
        "message": "Menu creation failed",
        "errors": serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_menus(request):
    menus = menu.objects.all()
    serializer = MenuSerializer(menus, many=True)
    return Response({"message": "Menus retrieved successfully",
                     "data": serializer.data})

@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated,IsCanteenAdminOrSuperUser])
def update_menu(request, menu_id):
    try:
        menu_instance = menu.objects.get(pk=menu_id)
    except menu.DoesNotExist:
        return Response({'error': 'Menu not found'}, status=404)

    serializer = MenuSerializer(menu_instance, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response({'message': 'Menu updated successfully','updateded': serializer.data
        }, status=status.HTTP_200_OK)
    return Response({
        "message": "upadate manu failed",
        "errors": serializer.errors
    }, status=400)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated,IsCanteenAdminOrSuperUser])
def delete_menu(request, menu_id):
    try:
        menu_instance = menu.objects.get(pk=menu_id)
    except menu.DoesNotExist:
        return Response({'error': 'Menu not found'}, status=404)

    menu_instance.delete()
    return Response({'message': 'Menu deleted successfully'}, status=204)

@api_view(['GET'])
@permission_classes([IsAuthenticated,IsCanteenAdminOrSuperUser])
def menu_vote_count(request, id):
    try:
        menu_obj = menu.objects.get(pk=id)
    except menu.DoesNotExist:
        return Response({'error': 'Menu not found'}, status=status.HTTP_404_NOT_FOUND)

    total_votes = Vote.objects.filter(menu=menu_obj).count()
    return Response({
        'menu_id': menu_obj.id,
        'menu_date': menu_obj.date,
        'total_votes': total_votes
    }, status=status.HTTP_200_OK)

VOTING_DEADLINE = time(17, 0)  
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_vote(request):
    user = request.user
    menu_id = request.data.get('menu')
    if Vote.objects.filter(user=user, menu_id=menu_id).exists():
        return Response({'message': 'You have already voted for this menu.'}, status=status.HTTP_200_OK)
    serializer = VoteSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(user=user)  
        return Response({'message': 'Vote submitted successfully.', 'data': serializer.data}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated ,IsCanteenAdminOrSuperUser])
def check_votes(request):
    specific_date = request.GET.get('date')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    try:
        if specific_date:
            date_obj = datetime.strptime(specific_date, '%Y-%m-%d').date()
            menus = menu.objects.filter(date=date_obj)

        elif start_date and end_date:
            start = datetime.strptime(start_date, '%Y-%m-%d').date()
            end = datetime.strptime(end_date, '%Y-%m-%d').date()
            menus = menu.objects.filter(date__range=(start, end))

        else:
            today = date.today()
            menus = menu.objects.filter(date=today)

        if not menus.exists():
            return Response({'message': 'No menu found in selected date(s)'}, status=404)

        if request.user.role in [2,3]:  
            votes = Vote.objects.filter(menu__in=menus)
        else: 
            votes = Vote.objects.filter(menu__in=menus, user=request.user)
        serializer = VoteSerializer(votes, many=True)

        vote_summary = {}
        if request.user.role in [2,3]:
            for m in menus:
                vote_summary[m.id] = {
                    "menu_date": m.date,
                    "total_votes": votes.filter(menu=m).count()
                }
        return Response({
            "votes": serializer.data,
            "vote_summary": vote_summary if request.user.role in [2,3] else None
        }, status=200)
    except ValueError:
        return Response({'error': 'Invalid date format. Use YYYY-MM-DD.'}, status=400)
    

@api_view(['GET'])
@permission_classes([IsAuthenticated,IsCanteenAdminOrSuperUser])
def report_view(request):
    from_date = request.GET.get('from')
    to_date = request.GET.get('to')
    export = request.GET.get('export')  
    if not from_date or not to_date:
        return Response({'error': 'from and to dates are required'}, status=status.HTTP_400_BAD_REQUEST)

    if export not in ['csv', 'pdf']:
        return Response({'error': 'Invalid export type. Use csv or pdf.'}, status=status.HTTP_400_BAD_REQUEST)
   
    task = generate_report_task.delay(from_date, to_date, export)

    return Response({
        'message': 'Report generation started. Check back later.',
        'task_id': task.id
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated,IsCanteenAdminOrSuperUser])
def check_report_status(request):
    task_id = request.GET.get('task_id')
    if not task_id:
        return JsonResponse({'error': 'task_id is required'}, status=400)
    result = AsyncResult(task_id, app=app)
    response = {
        'task_id': task_id,
        'status': result.status,  
        # 'result': result.result if result.successful() else None
    }
    return JsonResponse(response)

@api_view(['GET'])
@permission_classes([IsAuthenticated ,IsCanteenAdminOrSuperUser])
def download_report(request):
    file_name = request.GET.get('file_name')

    if not file_name:
        return JsonResponse({'error': 'Missing "file_name" parameter'}, status=400)

    file_path = os.path.join(settings.MEDIA_ROOT, 'reports', file_name)

    if os.path.exists(file_path):
        return FileResponse(open(file_path, 'rb'), as_attachment=True, filename=file_name)
    else:
        raise Http404("Report not found.")


@api_view(['GET'])
def dish_order_count_view(request):
    dish_order_counts = (
        Vote.objects.values('menu__dishes') 
        .annotate(order_count=Count('id'))
        .order_by('-order_count')
    )
    return Response(list(dish_order_counts))

from django.db import connection
@api_view(['GET'])
@permission_classes([IsAuthenticated, IsCanteenAdminOrSuperUser])
def dish_votes_last_6_months(request):
    from_raw = request.GET.get('from')
    to_raw = request.GET.get('to')
    from_date = parse_date(from_raw) if from_raw else None
    to_date = parse_date(to_raw) if to_raw else None

    if not from_date:
        today = date.today()
        from_date = today.replace(day=1) - timedelta(days=180)
    if not to_date:
        to_date = date.today()

    query = """
    SELECT
        DATE_TRUNC('month', m.date) AS month,
        m.dishes AS dish,
        COUNT(v.id) AS vote_count
    FROM canteen_vote v
    JOIN canteen_menu m ON v.menu_id = m.id
    WHERE m.date BETWEEN %s AND %s
    GROUP BY month, dish
    ORDER BY month, vote_count DESC;
"""


    with connection.cursor() as cursor:
        cursor.execute(query, [from_date, to_date])
        rows = cursor.fetchall()

    # Format result
    formatted = []
    for month, dish, count in rows:
        formatted.append({
            'month': month.strftime('%B %Y'),
            'dish': dish,
            'vote_count': count
        })

    return Response(formatted)