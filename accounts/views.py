from django_filters.rest_framework.backends import DjangoFilterBackend
from rest_framework.response import Response
from rest_framework.decorators import action as action_decorator
from accounts.serializers import *
from rest_framework import viewsets, status, permissions
from drf_yasg.utils import swagger_auto_schema
from .filters import UserFilter

class IsSuperUser(permissions.BasePermission):
    """
    Allows access only to superusers.
    """

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_superuser

class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_class = UserFilter

    def get_permissions(self):
        if self.action in ["list", "retrieve", "update", "partial_update", "delete"]:
            self.permission_classes = [IsSuperUser]
        elif self.action in [
            "create",
            "set_new_password",
            "reset_password",
            "login",
            "check_token",
        ]:
            self.permission_classes = [permissions.AllowAny]
        else:
            self.permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in self.permission_classes]
    
    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return User.objects.none()
        return User.objects.all()

    def get_serializer_class(self):
        if self.action == "create":
            return UserRegisterSerializer
        elif self.action == "update":
            return UserUpdateSerializer
        elif self.action == "retrieve":
            return UserRetrieveSerializer
        elif self.action == "login":
            return LoginSerializer
        elif self.action == "set_new_password":
            return SetNewPasswordSerializer
        elif self.action == "reset_password":
            return PasswordResetRequestSerializer
        elif self.action == "change_password":
            return ChangePasswordSerializer
        elif self.action == "change_email":
            return ChangeEmailSerializer
        elif self.action == "check_token":
            return CheckTokenSerializer
        elif self.action == "list":
            return UserListSerializer
        elif self.action == "me":
            return UserMeSerializer
        return UserSerializer

    @swagger_auto_schema(
        operation_description="User login",
        operation_summary="login",
    )
    @action_decorator(
        detail=False,
        methods=["post"],
        url_path="login",
        permission_classes=[permissions.AllowAny],
    )
    def login(self, request):
        serializer = LoginSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_description="Changement de mot de passe",
        operation_summary="Changement de mot de passe",
    )
    @action_decorator(
        detail=False,
        methods=["post"],
        url_path="set_new_password",
        permission_classes=[permissions.AllowAny],
    )
    def set_new_password(self, request):
        serializer = SetNewPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(
            {"message": "password reset successfully"},
            status=status.HTTP_200_OK,
        )

    @swagger_auto_schema(
        operation_description="Check le token avant le rest du mot de passe",
        operation_summary="Check le token avant le rest du mot de passe",
    )
    @action_decorator(
        detail=False,
        methods=["post"],
        url_path="check_token",
        permission_classes=[permissions.AllowAny],
    )
    def check_token(self, request):
        serializer = CheckTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({"message": "token is valid"}, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_description="Reinitialisation du mot de passe",
        operation_summary="Reinitialisation du mot de passe",
    )
    @action_decorator(
        detail=False,
        methods=["post"],
        url_path="reset_password",
        permission_classes=[permissions.AllowAny],
    )
    def reset_password(self, request):
        serializer = PasswordResetRequestSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        return Response(
            {"message": "we have sent you a link to reset your password"},
            status=status.HTTP_200_OK,
        )

    @swagger_auto_schema(
        operation_description="Changement de mot de passe",
        operation_summary="Changement de mot de passe",
    )
    @action_decorator(
        detail=False,
        methods=["post"],
        url_path="change-password",
        url_name="change_password",
        permission_classes=[permissions.IsAuthenticated],
        serializer_class=ChangePasswordSerializer,
    )
    def change_password(self, request):
        serializer = ChangePasswordSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        return Response(
            {"message": "password changed successfully"}, status=status.HTTP_200_OK
        )

    @swagger_auto_schema(
        operation_description="Changement du mail",
        operation_summary="Changement du mail",
    )
    @action_decorator(
        detail=False,
        methods=["post"],
        url_path="change-email",
        url_name="change_email",
        permission_classes=[permissions.IsAuthenticated],
        serializer_class=ChangeEmailSerializer,
    )
    def change_email(self, request):
        serializer = ChangeEmailSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        return Response(
            {"message": "email changed successfully"}, status=status.HTTP_200_OK
        )

    @swagger_auto_schema(
        operation_description="Validation de l'email",
        operation_summary="Validation de l'email",
    )
    @action_decorator(
        detail=False,
        methods=["get"],
        url_path="validate_mail",
        permission_classes=[permissions.AllowAny],
        serializer_class=ValidateEmailSerializer,
    )
    def validate_mail(self, request):
        user_id = request.query_params.get("uidb64", "")
        confirmation_token = request.query_params.get("token", "")
        data = {"uidb64": user_id, "token": confirmation_token}
        serializer = ValidateEmailSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        return Response("Email successfully confirmed")

    @swagger_auto_schema(
        operation_description="Retourne les informations d'un utilisateur",
        operation_summary="Retourne les informations d'un utilisateur",
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Liste des utilisateurs",
        operation_summary="Liste des utilisateurs",
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="update the user",
        operation_summary="Update user",
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Partial user update",
        operation_summary="Partial user update",
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Suppression d'un utilisateur",
        operation_summary="Suppression d'un utilisateur",
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Register user",
        operation_summary="Register user",
    )
    def create(self, request, *args, **kwargs):
        data = request.data
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    @swagger_auto_schema(
        operation_description="Retrieve the connected user information",
        operation_summary="Retrieve user",
    )
    @action_decorator(
        detail=False,
        methods=["get"],
        url_path="me",
        permission_classes=[permissions.IsAuthenticated],
    )
    def me(self, request, *args, **kwargs):
        serializer = UserMeSerializer(request.user, context={"request": request})
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="update the logged user",
        operation_summary="Update logged user",
    )
    @action_decorator(
        detail=False,
        methods=["put"],
        url_path="update-me",
        permission_classes=[permissions.IsAuthenticated],
    )
    def update_me(self, request, *args, **kwargs):
        instance = request.user
        data = request.data.copy()
        serializer = UserMeSerializer(
            instance, data=data, partial=True, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)



