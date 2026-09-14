from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers.file import *
from django.http import FileResponse

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


class FileListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        files = StoredFile.objects.filter(
            owner=request.user
        ).order_by("-uploaded_at")

        serializer = FileListSerializer(files, many=True)

        return Response(
            {
                "status": "success",
                "files": serializer.data,
            },
            status=status.HTTP_200_OK,
        )





class FileDownloadView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, file_id):
        try:
            stored_file = StoredFile.objects.get(
                id=file_id,
                owner=request.user,
            )
        except StoredFile.DoesNotExist:
            return Response(
                {
                    "status": "error",
                    "message": "File not found",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        return FileResponse(
            stored_file.file.open("rb"),
            as_attachment=True,
            filename=stored_file.original_name,
        )