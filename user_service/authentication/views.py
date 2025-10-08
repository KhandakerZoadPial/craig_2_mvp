from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from .models import UserProfile
from .serializers import ProfileSerializer
from .utils import generate_response
from django.views.decorators.csrf import csrf_exempt





@csrf_exempt
@api_view(['POST'])
def signup(request):
    data = request.data
    username = data.get('email')
    password = data.get('password')

    if not all([username, password]):
        response = generate_response("failure", 400, {}, "Missing required fields.")
        return Response(response, status=status.HTTP_400_BAD_REQUEST)

    if User.objects.filter(username=username).exists():
        response = generate_response("failure", 400, {}, "Email already in use.")
        return Response(response, status=status.HTTP_400_BAD_REQUEST)

    user = User.objects.create_user(
        username=username,
        email=username,
        password=password
    )

    user_profile = UserProfile()
    user_profile.user = user
    user_profile.save()


    response = generate_response("Success", 201, {"Message": "Succesfully Created User."})


    return Response(response, status=status.HTTP_201_CREATED)


@csrf_exempt
@api_view(['POST'])
def login(request):
    email = request.data.get('email')
    password = request.data.get('password')

    if not all([email, password]):
        return Response({'error': 'Email and password are required.'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        response = generate_response("failure", 400, {}, "Invalid credentials.")
        return Response(response, status=status.HTTP_401_UNAUTHORIZED)

    user = authenticate(username=user.username, password=password)
    if user is None:
        response = generate_response("failure", 400, {}, "Invalid credentials.")
        return Response(response, status=status.HTTP_401_UNAUTHORIZED)

    refresh = RefreshToken.for_user(user)
    access_token = refresh.access_token
    access_token['username'] = user.username
    access_token['email'] = user.email


    response = generate_response("success", 200, {'refresh_token': str(refresh),  'access_token': str(access_token)})

    print('I am hitted')
    return Response(response, status=200)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def me_view(request):
    user = request.user
    profile = user.profile

    data = ProfileSerializer(profile).data

    response = generate_response("success", 200, data)

    return Response(
       response,
        status=200
    )