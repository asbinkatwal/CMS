from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from .serializers import RegisterSerializer, LoginSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from canteen.models import User

@api_view(['POST'])
@permission_classes([AllowAny])  
def register_user(request):
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "User registered successfully"}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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
        }, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])  
def logout_user(request):
    try:
        request.user.auth_token.delete()
    except:
        pass
    return Response({"message": "Logged out successfully"}, status=status.HTTP_200_OK)


##this is fro forgot password 
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.contrib.auth import get_user_model





User = get_user_model()

@api_view(['POST'])
@permission_classes([IsAuthenticated])  
def request_reset_email(request):
    email = request.data.get('email')
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=404)

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



from .models import menu
from .serializers import MenuSerializer
from rest_framework.permissions import IsAuthenticated
from .permissions import IsCanteenAdmin

@api_view(['POST'])
@permission_classes([IsAuthenticated,IsCanteenAdmin])
def create_menu(request):

    serializer = MenuSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsCanteenAdmin])
def list_menus(request):
    print("User:", request.user.username)
    print("User Role:", request.user.role)

    menus = menu.objects.all()
    serializer = MenuSerializer(menus, many=True)
    return Response(serializer.data)

@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated, IsCanteenAdmin])
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
    return Response(serializer.errors, status=400)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated, IsCanteenAdmin])
def delete_menu(request, menu_id):
    try:
        menu_instance = menu.objects.get(pk=menu_id)
    except menu.DoesNotExist:
        return Response({'error': 'Menu not found'}, status=404)

    menu_instance.delete()
    return Response({'message': 'Menu deleted successfully'}, status=204)



from datetime import datetime, time
from .models import Vote, menu
from .serializers import VoteSerializer

VOTING_DEADLINE = time(17, 0)  # 5 PM this is the dedline of that voting  day 

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_vote(request):
    user = request.user
    menu_id = request.data.get('menu')

    if Vote.objects.filter(user=user, menu_id=menu_id).exists():
        return Response({'message': 'You have already voted for this menu.'}, status=status.HTTP_200_OK)

    serializer = VoteSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(user=user)  # Assign the logged-in user to the vote
        return Response({'message': 'Vote submitted successfully.', 'data': serializer.data}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])  
def check_votes(request):
    # Check for the 'date' parameter in query params
    date_str = request.GET.get('date')

    # If the date isn't in query params, try to get it from the request body
    if not date_str:
        date_str = request.data.get('date')

    if not date_str:
        return Response({'error': 'Date is required'}, status=400)

    try:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return Response({'error': 'Invalid date format. Use YYYY-MM-DD.'}, status=400)

    menu_obj = menu.objects.filter(date=date_obj).first()
    if not menu_obj:
        return Response({'error': 'No menu found for that date'}, status=404)

    votes = Vote.objects.filter(user=request.user, menu=menu_obj)
    serializer = VoteSerializer(votes, many=True)
    return Response(serializer.data)

## for export csv and pdf file 
import pandas as pd
from django.http import HttpResponse
from io import BytesIO
from reportlab.pdfgen import canvas

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def report_view(request):
    from_date = request.GET.get('from')
    to_date = request.GET.get('to')
    export = request.GET.get('export')  # options: 'csv', 'pdf'

    if not from_date or not to_date:
        return Response({'error': 'from and to dates are required. Format: YYYY-MM-DD'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        from_date_obj = datetime.strptime(from_date, '%Y-%m-%d').date()
        to_date_obj = datetime.strptime(to_date, '%Y-%m-%d').date()
    except ValueError:
        return Response({'error': 'Invalid date format. Use YYYY-MM-DD'}, status=status.HTTP_400_BAD_REQUEST)

    votes = Vote.objects.filter(voted_at__date__gte=from_date_obj, voted_at__date__lte=to_date_obj)

    df = pd.DataFrame.from_records(votes.values('voted_at'))
    if df.empty:
        return Response({'message': 'No votes found in the given date range.'})

    df['date'] = pd.to_datetime(df['voted_at']).dt.date
    report = df.groupby('date').size().reset_index(name='vote_count')

    if export == 'csv':
        csv_data = report.to_csv(index=False)
        response = HttpResponse(csv_data, content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="vote_report_{from_date}_to_{to_date}.csv"'
        return response

    elif export == 'pdf':
        buffer = BytesIO()
        p = canvas.Canvas(buffer)
        p.setFont("Helvetica", 12)
        p.drawString(50, 800, f"Vote Report from {from_date} to {to_date}")

        y = 770
        for index, row in report.iterrows():
            p.drawString(50, y, f"Date: {row['date']}, Votes: {row['vote_count']}")
            y -= 20
            if y < 50:
                p.showPage()
                y = 800

        p.save()
        buffer.seek(0)
        return HttpResponse(buffer, content_type='application/pdf')

    return Response(report.to_dict(orient='records'))
