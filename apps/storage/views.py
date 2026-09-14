from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers.file import FileUploadSerializer


class FileUploadView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        serializer = FileUploadSerializer(data=request.data)

        if serializer.is_valid():
            uploaded_file = request.FILES["file"]

            stored_file = serializer.save(
                owner=request.user,
                original_name=uploaded_file.name,
                file_size=uploaded_file.size,
            )

            return Response(
                {
                    "status": "success",
                    "message": "File uploaded successfully",
                    "file": {
                        "id": stored_file.id,
                        "original_name": stored_file.original_name,
                        "file_size": stored_file.file_size,
                        "uploaded_at": stored_file.uploaded_at,
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