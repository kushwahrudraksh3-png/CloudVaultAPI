from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated


from .serializers.auth import *


class HealthCheckView(APIView):
    def get(self, request):
        return Response({
            "status": "success",
            "message": "CloudVault API is running"
        })


class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()

            return Response(
                {
                    "status": "success",
                    "message": "User registered successfully",
                    "user": {
                        "id": user.id,
                        "username": user.username,
                        "email": user.email,
                    },
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(
            {
                "status": "error",
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )



class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        return Response({
            "status": "success",
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
            }
        })

class ProfileUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request):
        user = request.user

        serializer = ProfileUpdateSerializer(
            user,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():
            serializer.save()

            return Response({
                "status": "success",
                "message": "Profile updated successfully",
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                }
            }, status=status.HTTP_200_OK)

        return Response({
            "status": "error",
            "errors": serializer.errors,
        }, status=status.HTTP_400_BAD_REQUEST)