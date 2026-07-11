from django.shortcuts import render
from rest_framework import status, generics, permissions, filters, mixins
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.token_blacklist.models import (
    BlacklistedToken,
    OutstandingToken,
)
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from drf_spectacular.utils import extend_schema, extend_schema_view
from django_filters.rest_framework import DjangoFilterBackend
from .models import User, UserProfile, HostVerification, UserActivity, Favorite
from .permissions import (
    IsHost,
    IsGuest,
    IsApprovedHost,
    IsHostOrAdmin,
    IsOwnerOrSuperAdmin,
    IsSuperAdmin,
    IsOwner,
    IsGuestOrHost,
)
from .serializers import (
    UserRegistrationSerializer,
    UserLoginSerializer,
    UserSerializer,
    UserProfileSerializer,
    UserUpdateSerializer,
    PasswordChangeSerializer,
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer,
    EmailVerificationSerializer,
    SwitchToHostSerializer,
    HostVerificationSerializer,
    HostApprovalSerializer,
    UserActivitySerializer,
    AdminUserSerializer,
    UserDetailSerializer,
    FavoriteSerializer,
)
from utils.response import api_response
import structlog

logger = structlog.get_logger(__name__)


@extend_schema_view(
    post=extend_schema(
        summary="User Registration",
        description="Register a new user account (guest or host)",
    )
)
class UserRegistrationView(generics.CreateAPIView):
    """User registration endpoint"""

    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        logger.info(
            "user_registered",
            user_id=str(user.pk),
            role=user.role,
            email=user.email,
        )

        # Log activity
        UserActivity.objects.create(
            user=user,
            activity_type="registration",
            description=f"User registered as {user.get_role_display()}",
            ip_address=request.META.get("REMOTE_ADDR"),
            user_agent=request.META.get("HTTP_USER_AGENT", ""),
        )

        return api_response(
            success=True,
            data={"user": UserDetailSerializer(user).data},
            status_code=status.HTTP_201_CREATED,
        )


@extend_schema_view(
    post=extend_schema(
        summary="User Login", description="Authenticate user and return token"
    )
)
class UserLoginView(generics.GenericAPIView):
    """User login endpoint"""

    serializer_class = UserLoginSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]

        logger.info("user_login", user_id=str(user.pk), email=user.email)

        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        access_token = refresh.access_token

        # Log activity
        UserActivity.objects.create(
            user=user,
            activity_type="login",
            description="User logged in",
            ip_address=request.META.get("REMOTE_ADDR"),
            user_agent=request.META.get("HTTP_USER_AGENT", ""),
        )

        return api_response(
            success=True,
            data={
                "user": UserDetailSerializer(user).data,
                "access": str(access_token),
                "refresh": str(refresh),
            },
        )


class LogoutView(generics.GenericAPIView):
    """User logout endpoint"""

    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        summary="User Logout",
        description="Logout user and blacklist refresh token",
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "refresh": {
                        "type": "string",
                        "description": "Refresh token to blacklist",
                    }
                },
                "required": ["refresh"],
            }
        },
    )
    def post(self, request, *args, **kwargs):
        try:
            refresh_token = request.data.get("refresh")
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()

            # Log activity
            UserActivity.objects.create(
                user=request.user,
                activity_type="logout",
                description="User logged out",
                ip_address=request.META.get("REMOTE_ADDR"),
                user_agent=request.META.get("HTTP_USER_AGENT", ""),
            )

            logger.info("user_logout", user_id=str(request.user.pk))
            return api_response(success=True, data={})
        except Exception as e:
            logger.warning(
                "user_logout_failed",
                user_id=str(request.user.pk),
                error=str(e),
            )
            return api_response(
                success=False,
                errors={"error": "Logout failed"},
                status_code=status.HTTP_400_BAD_REQUEST,
            )


@extend_schema_view(
    get=extend_schema(
        summary="Get Current User Profile",
        description="Get authenticated user's profile information",
    ),
    put=extend_schema(
        summary="Update Current User Profile",
        description="Update authenticated user's profile information",
    ),
    patch=extend_schema(
        summary="Partially Update Current User Profile",
        description="Partially update authenticated user's profile information",
    ),
)
class UserProfileView(generics.RetrieveUpdateAPIView):
    """Current user profile view"""

    serializer_class = UserDetailSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


@extend_schema_view(
    list=extend_schema(summary="List Users", description="List all users (admin only)"),
    create=extend_schema(
        summary="Create User", description="Create a new user (admin only)"
    ),
    retrieve=extend_schema(
        summary="Get User Details", description="Get user details by ID"
    ),
    update=extend_schema(summary="Update User", description="Update user information"),
    partial_update=extend_schema(
        summary="Partially Update User", description="Partially update user information"
    ),
    destroy=extend_schema(
        summary="Delete User", description="Soft delete user account"
    ),
)
class UserViewSet(ModelViewSet):
    """User management viewset"""

    queryset = User.objects.all()
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = [
        "role",
        "is_verified_host",
        "host_approval_status",
        "country",
        "city",
    ]
    search_fields = ["first_name", "last_name", "email", "username"]
    ordering_fields = ["date_joined", "first_name", "last_name"]
    ordering = ["-date_joined"]

    def get_serializer_class(self):
        if self.request.user and self.request.user.is_superuser:
            return AdminUserSerializer
        return UserDetailSerializer

    def get_permissions(self):
        """Set permissions based on action"""
        if self.action in ["list", "create"]:
            permission_classes = [IsSuperAdmin]
        elif self.action in ["retrieve"]:
            permission_classes = [IsOwnerOrSuperAdmin]
        elif self.action in ["update", "partial_update", "destroy"]:
            permission_classes = [IsOwnerOrSuperAdmin]
        else:
            permission_classes = [permissions.IsAuthenticated]

        return [permission() for permission in permission_classes]

    def get_queryset(self):
        """Filter queryset based on user permissions"""
        if self.request.user.is_superuser:
            return User.objects.all()
        elif self.action == "list":
            # Non-admins can't list users
            return User.objects.none()
        else:
            # Users can only access their own profile
            return User.objects.filter(id=self.request.user.id)

    @action(
        detail=False, methods=["get"], permission_classes=[permissions.IsAuthenticated]
    )
    def me(self, request):
        """Get current user profile"""
        serializer = self.get_serializer(request.user)
        return api_response(success=True, data=serializer.data)

    @action(detail=True, methods=["post"], permission_classes=[IsSuperAdmin])
    def approve_host(self, request, pk=None):
        """Approve or reject host application"""
        user = self.get_object()

        if user.role != User.HOST:
            return api_response(
                success=False,
                errors={"error": "User is not a host"},
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        serializer = HostApprovalSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()

            # Log activity
            UserActivity.objects.create(
                user=user,
                activity_type="host_approval",
                description=f"Host approval status changed to {user.host_approval_status}",
                metadata={"approved_by": request.user.id},
            )

            return api_response(
                success=True, data={"user": AdminUserSerializer(user).data}
            )

        return api_response(
            success=False,
            errors=serializer.errors,
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    @action(detail=False, methods=["get"], permission_classes=[IsSuperAdmin])
    def pending_hosts(self, request):
        """Get list of pending host applications"""
        pending_hosts = User.objects.filter(
            role=User.HOST, host_approval_status="pending"
        )
        serializer = AdminUserSerializer(pending_hosts, many=True)
        return api_response(success=True, data=serializer.data)

    @action(detail=False, methods=["get"], permission_classes=[IsSuperAdmin])
    def stats(self, request):
        """Get user management statistics"""
        from django.utils import timezone
        from datetime import timedelta

        today = timezone.now().date()
        month_start = today.replace(day=1)

        stats = {
            "total_users": User.objects.count(),
            "active_users": User.objects.filter(is_active=True).count(),
            "pending_hosts": User.objects.filter(
                role=User.HOST, host_approval_status="pending"
            ).count(),
            "approved_hosts": User.objects.filter(
                role=User.HOST, host_approval_status="approved"
            ).count(),
            "new_registrations_today": User.objects.filter(
                date_joined__date=today
            ).count(),
            "new_registrations_this_month": User.objects.filter(
                date_joined__date__gte=month_start
            ).count(),
        }

        return api_response(success=True, data=stats)

    @action(detail=True, methods=["post"], permission_classes=[IsSuperAdmin])
    def toggle_status(self, request, pk=None):
        """Toggle user active status"""
        user = self.get_object()
        user.is_active = not user.is_active
        user.save()

        # Log activity
        UserActivity.objects.create(
            user=user,
            activity_type="status_change",
            description=f'User status changed to {"active" if user.is_active else "inactive"}',
            metadata={"changed_by": request.user.id},
        )

        return api_response(success=True, data={"user": AdminUserSerializer(user).data})

    @action(detail=True, methods=["post"], permission_classes=[IsOwnerOrSuperAdmin])
    def switch_to_host(self, request, pk=None):
        """Switch user from guest to host"""
        user = self.get_object()

        if user.role == User.HOST:
            return api_response(
                success=False,
                errors={"error": "User is already a host"},
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        success = user.switch_to_host()
        if success:
            # Create host verification
            HostVerification.objects.get_or_create(user=user)

            # Log activity
            UserActivity.objects.create(
                user=user,
                activity_type="role_change",
                description="User switched to host role",
            )

            return api_response(
                success=True, data={"user": UserDetailSerializer(user).data}
            )

        return api_response(
            success=False,
            errors={"error": "Failed to switch to host role"},
            status_code=status.HTTP_400_BAD_REQUEST,
        )


@extend_schema_view(
    list=extend_schema(summary="List User Profiles", description="List user profiles"),
    retrieve=extend_schema(
        summary="Get User Profile", description="Get user profile by ID"
    ),
    update=extend_schema(
        summary="Update User Profile", description="Update user profile"
    ),
    partial_update=extend_schema(
        summary="Partially Update User Profile",
        description="Partially update user profile",
    ),
)
class UserProfileViewSet(ModelViewSet):
    """User profile management viewset"""

    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Filter profiles based on user permissions"""
        if self.request.user.is_superuser:
            return UserProfile.objects.all()
        else:
            return UserProfile.objects.filter(user=self.request.user)

    def get_permissions(self):
        """Set permissions based on action"""
        if self.action in ["retrieve", "update", "partial_update"]:
            permission_classes = [IsOwnerOrSuperAdmin]
        else:
            permission_classes = [permissions.IsAuthenticated]

        return [permission() for permission in permission_classes]


@extend_schema_view(
    list=extend_schema(
        summary="List Host Verifications",
        description="List host verifications (admin only)",
    ),
    retrieve=extend_schema(
        summary="Get Host Verification", description="Get host verification details"
    ),
    update=extend_schema(
        summary="Update Host Verification",
        description="Update host verification documents",
    ),
    partial_update=extend_schema(
        summary="Partially Update Host Verification",
        description="Partially update host verification documents",
    ),
)
class HostVerificationViewSet(ModelViewSet):
    """Host verification management viewset"""

    queryset = HostVerification.objects.all()
    serializer_class = HostVerificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Filter verifications based on user permissions"""
        if self.request.user.is_superuser:
            return HostVerification.objects.all()
        else:
            return HostVerification.objects.filter(user=self.request.user)

    def get_permissions(self):
        """Set permissions based on action"""
        if self.action in ["list"]:
            permission_classes = [IsSuperAdmin]
        elif self.action in ["retrieve", "update", "partial_update"]:
            permission_classes = [IsOwnerOrSuperAdmin]
        else:
            permission_classes = [permissions.IsAuthenticated]

        return [permission() for permission in permission_classes]

    @action(detail=True, methods=["post"], permission_classes=[IsSuperAdmin])
    def verify_document(self, request, pk=None):
        """Verify specific document"""
        verification = self.get_object()
        document_type = request.data.get("document_type")
        verified = request.data.get("verified", False)

        if document_type == "identity":
            verification.identity_verified = verified
        elif document_type == "address":
            verification.address_verified = verified
        elif document_type == "business":
            verification.business_verified = verified
        else:
            return Response(
                {"error": "Invalid document type"}, status=status.HTTP_400_BAD_REQUEST
            )

        verification.verified_by = request.user
        verification.save()

        # Update user verification status if fully verified
        if verification.is_fully_verified():
            verification.user.is_verified_host = True
            verification.user.save()

        logger.info(
            "host_document_verification_updated",
            verification_id=str(verification.pk),
            user_id=str(verification.user_id),
            document_type=document_type,
            verified=verified,
            actor_id=str(request.user.pk),
        )

        return api_response(
            success=True,
            data={"verification": HostVerificationSerializer(verification).data},
        )


@extend_schema_view(
    list=extend_schema(
        summary="List User Activities", description="List user activities"
    ),
    retrieve=extend_schema(
        summary="Get User Activity", description="Get user activity details"
    ),
)
class UserActivityViewSet(ModelViewSet):
    """User activity viewset (read-only)"""

    queryset = UserActivity.objects.all()
    serializer_class = UserActivitySerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ["get"]  # Read-only
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["activity_type", "user"]
    ordering_fields = ["created_at"]
    ordering = ["-created_at"]

    def get_queryset(self):
        """Filter activities based on user permissions"""
        if self.request.user.is_superuser:
            return UserActivity.objects.all()
        else:
            return UserActivity.objects.filter(user=self.request.user)


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def user_profile_status(request):
    """Get user profile completion status"""
    user = request.user
    profile = getattr(user, "profile", None)

    # Calculate profile completion percentage
    required_fields = ["first_name", "last_name", "phone", "country", "city"]
    completed_fields = sum(1 for field in required_fields if getattr(user, field))

    profile_fields = ["bio"] if profile else []
    if profile:
        completed_fields += sum(
            1 for field in profile_fields if getattr(profile, field)
        )

    total_fields = len(required_fields) + len(profile_fields)
    completion_percentage = (
        (completed_fields / total_fields) * 100 if total_fields > 0 else 0
    )

    return api_response(
        success=True,
        data={
            "completion_percentage": round(completion_percentage, 2),
            "email_verified": user.email_verified,
            "missing_fields": [
                field for field in required_fields if not getattr(user, field)
            ],
        },
    )


@api_view(["DELETE"])
@permission_classes([permissions.IsAuthenticated])
def deactivate_account(request):
    """Deactivate user account (soft delete)"""
    user = request.user
    user.is_active = False
    user.save()

    # Blacklist all outstanding JWT refresh tokens for this user
    for outstanding in OutstandingToken.objects.filter(user=user):
        BlacklistedToken.objects.get_or_create(token=outstanding)

    logger.info("user_account_deactivated", user_id=str(user.pk))
    return api_response(success=True, data={})


# Role-Based Views


class SwitchToHostView(APIView):
    """API view for switching from guest to host"""

    permission_classes = [permissions.IsAuthenticated, IsGuest]

    def post(self, request):
        serializer = SwitchToHostSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        return api_response(success=True, data={"user": UserSerializer(user).data})


class HostVerificationView(generics.RetrieveUpdateAPIView):
    """API view for host verification"""

    serializer_class = HostVerificationSerializer
    permission_classes = [permissions.IsAuthenticated, IsHost]

    def get_object(self):
        verification, created = HostVerification.objects.get_or_create(
            user=self.request.user
        )
        return verification


class HostApprovalView(generics.UpdateAPIView):
    """API view for admin host approval"""

    queryset = User.objects.filter(role=User.HOST)
    serializer_class = HostApprovalSerializer
    permission_classes = [permissions.IsAdminUser]

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        user = self.get_object()

        # Log admin activity
        UserActivity.objects.create(
            user=user,
            activity_type="host_approval_changed",
            description=f"Host approval status changed to {user.host_approval_status}",
            metadata={"approved_by": request.user.id},
        )

        return response


class HostListView(generics.ListAPIView):
    """API view for listing hosts (admin only)"""

    queryset = User.objects.filter(role=User.HOST)
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_queryset(self):
        queryset = super().get_queryset()
        status = self.request.query_params.get("status")

        if status:
            queryset = queryset.filter(host_approval_status=status)

        return queryset


class GuestListView(generics.ListAPIView):
    """API view for listing guests (admin only)"""

    queryset = User.objects.filter(role=User.GUEST)
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]


class UserActivityListView(generics.ListAPIView):
    """API view for user activity (own activities or admin)"""

    serializer_class = UserActivitySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_admin_user():
            return UserActivity.objects.all()
        return UserActivity.objects.filter(user=self.request.user)


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def user_role_info(request):
    """Get user role information and capabilities"""
    user = request.user

    role_info = {
        "role": user.role,
        "role_display": user.get_role_display(),
        "is_guest": user.is_guest(),
        "is_host": user.is_host(),
        "is_admin": user.is_admin_user(),
        "can_list_properties": user.can_list_properties(),
        "can_book_properties": user.can_book_properties(),
        "capabilities": [],
    }

    # Add capabilities based on role
    if user.is_guest():
        role_info["capabilities"] = [
            "book_properties",
            "write_reviews",
            "manage_bookings",
            "switch_to_host",
        ]
    elif user.is_host():
        role_info["capabilities"] = [
            "book_properties",
            "write_reviews",
            "manage_bookings",
        ]

        if user.can_list_properties():
            role_info["capabilities"].extend(
                [
                    "list_properties",
                    "manage_properties",
                    "respond_to_bookings",
                    "view_analytics",
                ]
            )
        else:
            role_info["capabilities"].append("pending_approval")

        # Add host-specific information
        role_info["host_info"] = {
            "is_verified": user.is_verified_host,
            "approval_status": user.host_approval_status,
            "business_name": user.business_name,
        }

    # Add admin capabilities if user is staff/superuser
    if user.is_admin_user():
        role_info["capabilities"].extend(
            [
                "manage_users",
                "approve_hosts",
                "verify_documents",
                "view_analytics",
                "system_administration",
            ]
        )
        role_info["admin_info"] = {
            "is_staff": user.is_staff,
            "is_superuser": user.is_superuser,
        }

    return api_response(success=True, data=role_info)


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated, IsHost])
def host_dashboard_stats(request):
    """Get host dashboard statistics"""
    user = request.user

    stats = {
        "total_properties": 0,
        "active_bookings": 0,
        "total_revenue": 0,
        "guest_reviews": 0,
        "verification_status": {
            "is_verified": user.is_verified_host,
            "approval_status": user.host_approval_status,
        },
    }

    if hasattr(user, "host_verification"):
        verification = user.host_verification
        stats["verification_completion"] = (
            verification.verification_completion_percentage()
        )

    return api_response(success=True, data=stats)


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated, IsGuest])
def guest_dashboard_stats(request):
    """Get guest dashboard statistics"""
    user = request.user

    stats = {
        "total_bookings": 0,
        "upcoming_trips": 0,
        "favorite_properties": 0,
        "reviews_written": 0,
        "travel_preferences": (
            user.profile.travel_preferences if hasattr(user, "profile") else {}
        ),
    }

    return api_response(success=True, data=stats)


class FavoriteView(
    mixins.ListModelMixin, mixins.CreateModelMixin, generics.GenericAPIView
):
    """Manage user favorites (list, add, remove)"""

    serializer_class = FavoriteSerializer
    permission_classes = [permissions.IsAuthenticated, IsGuestOrHost]

    def get_queryset(self):
        return Favorite.objects.filter(user=self.request.user).select_related("listing")

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return api_response(success=True, data=serializer.data)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        item = serializer.save()
        return api_response(
            success=True,
            data=FavoriteSerializer(item, context={"request": request}).data,
            status_code=status.HTTP_201_CREATED,
        )

    def delete(self, request, *args, **kwargs):
        listing_id = request.data.get("listing_id") or request.query_params.get("listing_id")
        if not listing_id:
            return api_response(
                success=False,
                errors={"listing_id": "listing_id is required"},
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        deleted, _ = Favorite.objects.filter(
            user=request.user, listing_id=listing_id
        ).delete()

        if not deleted:
            return api_response(
                success=False,
                errors={"detail": "Favorite not found"},
                status_code=status.HTTP_404_NOT_FOUND,
            )

        return api_response(success=True, data={})


# Password Management Views


class PasswordChangeView(generics.GenericAPIView):
    """API view for changing password"""

    serializer_class = PasswordChangeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Log activity
        UserActivity.objects.create(
            user=user,
            activity_type="password_change",
            description="User changed password",
            ip_address=request.META.get("REMOTE_ADDR"),
            user_agent=request.META.get("HTTP_USER_AGENT", ""),
        )

        return api_response(success=True, data={})


class PasswordResetRequestView(generics.GenericAPIView):
    """API view for requesting password reset"""

    serializer_class = PasswordResetRequestSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return api_response(success=True, data={})


class PasswordResetConfirmView(generics.GenericAPIView):
    """API view for confirming password reset"""

    serializer_class = PasswordResetConfirmSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Log activity
        UserActivity.objects.create(
            user=user,
            activity_type="password_reset",
            description="User reset password",
            ip_address=request.META.get("REMOTE_ADDR"),
            user_agent=request.META.get("HTTP_USER_AGENT", ""),
        )

        return api_response(success=True, data={})


# Email Verification Views


class EmailVerificationView(generics.GenericAPIView):
    """API view for email verification"""

    serializer_class = EmailVerificationSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Log activity
        UserActivity.objects.create(
            user=user,
            activity_type="email_verification",
            description="User verified email address",
            ip_address=request.META.get("REMOTE_ADDR"),
            user_agent=request.META.get("HTTP_USER_AGENT", ""),
        )

        return api_response(success=True, data={})


class ResendVerificationEmailView(generics.GenericAPIView):
    """API view for resending verification email"""

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user

        if user.email_verified:
            return api_response(
                success=False,
                errors={"error": "Email is already verified"},
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        # Generate new verification token
        from django.utils.crypto import get_random_string

        user.email_verification_token = get_random_string(50)
        user.save()

        # Send verification email (implement email sending logic)
        # self.send_verification_email(user)

        return api_response(success=True, data={})
