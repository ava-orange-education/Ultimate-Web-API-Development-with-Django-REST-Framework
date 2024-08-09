import os
import uuid
from typing import Any

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from rest_framework import generics, status
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from api_auth.permissions import CustomDjangoModelPermissions
from movies.models import Movie
from movies.services import add_preference, add_watch_history
from movies.tasks import process_file

from .serializers import (
    AddPreferenceSerializer,
    AddToWatchHistorySerializer,
    GeneralFileUploadSerializer,
    MovieSerializer,
)
from .services import user_preferences, user_watch_history


# For listing all movies and creating a new movie
class MovieListCreateAPIView(generics.ListCreateAPIView):
    permission_classes = (IsAuthenticated, CustomDjangoModelPermissions)
    queryset = Movie.objects.all().order_by("id")
    serializer_class = MovieSerializer


# For retrieving, updating, and deleting a single movie
class MovieDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated, CustomDjangoModelPermissions]
    queryset = Movie.objects.all()
    serializer_class = MovieSerializer


class UserPreferencesView(APIView):
    """
    View to add new user preferences and retrieve them.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request: Request, user_id: int) -> Response:
        serializer = AddPreferenceSerializer(data=request.data)
        if serializer.is_valid():
            add_preference(user_id, serializer.validated_data["new_preferences"])
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request: Request, user_id: int) -> Response:
        data = user_preferences(user_id)
        return Response(data)


# View to retrieve and add movies to the user's watch history
@permission_classes([IsAuthenticated])
class WatchHistoryView(APIView):
    """
    View to retrieve and add movies to the user's watch history.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request: Request, user_id: int) -> Response:
        data = user_watch_history(user_id)
        return Response(data)

    def post(self, request: Request, user_id: int) -> Response:
        serializer = AddToWatchHistorySerializer(data=request.data)
        if serializer.is_valid():
            add_watch_history(
                user_id,
                serializer.validated_data["id"],
            )
            return Response(
                {"message": "Movie added to watch history."},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GeneralUploadView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args: Any, **kwargs: Any) -> Response:
        serializer = GeneralFileUploadSerializer(data=request.data)
        if serializer.is_valid():
            uploaded_file = serializer.validated_data["file"]
            file_type = uploaded_file.content_type

            # Extract the file extension
            file_extension = os.path.splitext(uploaded_file.name)[1]
            # Generate a unique file name using UUID
            unique_file_name = f"{uuid.uuid4()}{file_extension}"

            # Save the file directly to the default storage
            file_name = default_storage.save(
                unique_file_name, ContentFile(uploaded_file.read())
            )
            process_file.delay(file_name, file_type)

            return Response(
                {"message": f"Job enqueued for processing."},
                status=status.HTTP_202_ACCEPTED,
            )
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
