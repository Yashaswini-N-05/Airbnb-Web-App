from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

# Create router for ViewSets
router = DefaultRouter()
router.register(r'users', views.UserViewSet, basename='user')
router.register(r'profiles', views.UserProfileViewSet, basename='userprofile')
router.register(r'host-verifications', views.HostVerificationViewSet, basename='hostverification')
router.register(r'activities', views.UserActivityViewSet, basename='useractivity')

app_name = 'users'

urlpatterns = [
    # Authentication endpoints
    path('auth/register/', views.UserRegistrationView.as_view(), name='user-register'),
    path('auth/login/', views.UserLoginView.as_view(), name='user-login'),
    path('auth/logout/', views.LogoutView.as_view(), name='user-logout'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    
    # Profile endpoints
    path('profile/', views.UserProfileView.as_view(), name='user-profile'),
    path('profile/status/', views.user_profile_status, name='profile-status'),
    
    # Password management
    path('password/change/', views.PasswordChangeView.as_view(), name='password-change'),
    path('password/reset/', views.PasswordResetRequestView.as_view(), name='password-reset'),
    path('password/reset/confirm/', views.PasswordResetConfirmView.as_view(), name='password-reset-confirm'),
    
    # Email verification
    path('email/verify/', views.EmailVerificationView.as_view(), name='email-verify'),
    path('email/verify/resend/', views.ResendVerificationEmailView.as_view(), name='email-verify-resend'),
    
    # Account management
    path('account/deactivate/', views.deactivate_account, name='account-deactivate'),
    
    # Role-based endpoints
    path('role/info/', views.user_role_info, name='role-info'),
    path('role/switch-to-host/', views.SwitchToHostView.as_view(), name='switch-to-host'),
    path('switch-to-host/', views.SwitchToHostView.as_view(), name='switch-to-host-legacy'),
    
    # Host endpoints
    path('host/dashboard/', views.host_dashboard_stats, name='host-dashboard'),
    path('host/list/', views.HostListView.as_view(), name='host-list'),
    path('host/<uuid:pk>/approve/', views.HostApprovalView.as_view(), name='host-approval'),
    path('host/verification/', views.HostVerificationView.as_view(), name='host-verification'),
    
    # Guest endpoints
    path('guest/dashboard/', views.guest_dashboard_stats, name='guest-dashboard'),
    path('guest/list/', views.GuestListView.as_view(), name='guest-list'),
    
    # Favorites endpoints
    path('favorites/', views.FavoriteView.as_view(), name='favorites'),
    
    # Activity endpoints
    path('activity/', views.UserActivityListView.as_view(), name='user-activity'),
    
    # Include router URLs
    path('', include(router.urls)),
] 