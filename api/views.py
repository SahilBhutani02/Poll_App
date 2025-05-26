from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from .models import PollModel
from .serializers import PollSerializer
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate, login, logout

class SignupView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        if not username or not password:
            return Response({"error": "Username and password are required."}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(username=username).exists():
            return Response({"error": "Username already exists."}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.create_user(username=username, password=password)
        return Response({"message": "User created successfully."}, status=status.HTTP_201_CREATED)


class SigninView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)  # Enables session-based login for DRF UI

            # Also return JWT for frontend use
            refresh = RefreshToken.for_user(user)
            return Response({
                "message": "Login successful",
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            }, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Invalid credentials."}, status=status.HTTP_401_UNAUTHORIZED)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            logout(request)  # session logout for DRF UI
            if "refresh" in request.data:
                token = RefreshToken(request.data["refresh"])
                token.blacklist()  # optional: only if blacklisting is enabled
            return Response({"message": "Logged out successfully."}, status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class PollAPIView(APIView):

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated()]
        return [AllowAny()]

    def get(self, request):
        polls = PollModel.objects.all()

        # Manually apply pagination
        paginator = PageNumberPagination()  
        paginated_queryset = paginator.paginate_queryset(polls, request)
        serializer = PollSerializer(paginated_queryset, many=True)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request):
        serializer = PollSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(created_by=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PollIdAPIView(APIView):
    def get_permissions(self):
        if self.request.method == 'DELETE':
            return [IsAuthenticated()]
        return [AllowAny()]

    def get(self, request, pk):
        poll = get_object_or_404(PollModel, pk=pk)
        serializer = PollSerializer(poll)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # def put(self, request, pk):
    #     poll = get_object_or_404(PollModel, pk=pk)
    #     serializer = PollSerializer(poll, data=request.data)
    #     if serializer.is_valid():
    #         serializer.save()
    #         return Response(serializer.data, status=status.HTTP_200_OK)
    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        poll = get_object_or_404(PollModel, pk=pk)
        if request.user != poll.created_by and not request.user.is_superuser:
            return Response({"error": "You do not have permission to delete this poll."},
                        status=status.HTTP_403_FORBIDDEN)

        poll.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class VoteAPIView(APIView):
    permission_classes = [AllowAny]
    def post(self, request, pk):
        poll = get_object_or_404(PollModel, pk=pk)
        option = request.data.get("option")

        if option == "option_one":
            poll.option_one_count += 1
        elif option == "option_two":
            poll.option_two_count += 1
        elif option == "option_three":
            poll.option_three_count += 1
        else:
            return Response({"error": "Invalid option"}, status=status.HTTP_400_BAD_REQUEST)
    
        poll.save()
        serializer = PollSerializer(poll)
        return Response(serializer.data, status=status.HTTP_200_OK)


class PollResultAPIView(APIView):
    permission_classes = [AllowAny]
    def get(self, request, pk):
        poll = get_object_or_404(PollModel, pk=pk)
        serializer = PollSerializer(poll)
        return Response(serializer.data)
