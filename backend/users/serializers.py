from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.utils.crypto import get_random_string
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from .models import User, UserProfile, HostVerification, UserActivity, Favorite


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration"""
    password = serializers.CharField(
        write_only=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    password_confirm = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'}
    )
    
    class Meta:
        model = User
        fields = (
            'email', 'username', 'first_name', 'last_name', 
            'phone', 'date_of_birth', 'country', 'city',
            'preferred_currency', 'preferred_language',
            'role', 'password', 'password_confirm'
        )
        extra_kwargs = {
            'email': {'required': True},
            'username': {'required': True},
            'first_name': {'required': True},
            'last_name': {'required': True},
            'role': {'required': False},  # Optional, defaults to GUEST
        }
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords don't match.")
        return attrs
    
    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value
    
    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("A user with this username already exists.")
        return value
    
    def validate_role(self, value):
        if value and value not in [User.GUEST, User.HOST]:
            raise serializers.ValidationError("Invalid role. Must be 'guest' or 'host'.")
        return value or User.GUEST
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        
        # Generate email verification token
        email_verification_token = get_random_string(50)
        validated_data['email_verification_token'] = email_verification_token
        
        # Set host approval status if role is host
        if validated_data.get('role') == User.HOST:
            validated_data['host_approval_status'] = 'pending'
        
        user = User.objects.create_user(
            password=password,
            **validated_data
        )
        
        # Create user profile
        UserProfile.objects.create(user=user)
        
        # Create host verification if user is host
        if user.is_host():
            HostVerification.objects.create(user=user)
        
        # Send verification email (you'll need to implement email backend)
        self.send_verification_email(user)
        
        return user
    
    def send_verification_email(self, user):
        """Send email verification email"""
        # Implementation depends on your email configuration
        pass


class UserLoginSerializer(serializers.Serializer):
    """Serializer for user login"""
    email = serializers.EmailField()
    password = serializers.CharField(style={'input_type': 'password'})
    
    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        
        if email and password:
            user = authenticate(
                request=self.context.get('request'),
                username=email,
                password=password
            )
            
            if not user:
                raise serializers.ValidationError(
                    'Unable to log in with provided credentials.'
                )
            
            if not user.is_active:
                raise serializers.ValidationError(
                    'User account is disabled.'
                )
            
            attrs['user'] = user
            return attrs
        else:
            raise serializers.ValidationError(
                'Must include "email" and "password".'
            )


class UserSerializer(serializers.ModelSerializer):
    """Basic user serializer for public information"""
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 'full_name',
            'phone', 'country', 'city', 'avatar', 'role', 'role_display',
            'date_joined', 'is_verified_host'
        ]
        read_only_fields = ['id', 'username', 'date_joined', 'is_verified_host']


class UserProfileSerializer(serializers.ModelSerializer):
    """User profile serializer"""
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = UserProfile
        fields = '__all__'
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']


class UserDetailSerializer(serializers.ModelSerializer):
    """Detailed user serializer for authenticated users"""
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    profile = UserProfileSerializer(read_only=True)
    can_list_properties = serializers.BooleanField(read_only=True)
    can_book_properties = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 'full_name',
            'phone', 'date_of_birth', 'country', 'city', 'avatar', 'role', 'role_display',
            'preferred_currency', 'preferred_language', 'email_verified',
            'is_verified_host', 'host_approval_status', 'business_name',
            'business_license', 'tax_id', 'date_joined', 'profile',
            'can_list_properties', 'can_book_properties', 'is_superuser'
        ]
        read_only_fields = [
            'id', 'username', 'date_joined', 'email_verified', 'is_verified_host',
            'host_approval_status', 'can_list_properties', 'can_book_properties',
            'is_superuser'
        ]


class UserUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating user details"""
    
    class Meta:
        model = User
        fields = (
            'first_name', 'last_name', 'phone', 'date_of_birth',
            'country', 'city', 'avatar', 'preferred_currency',
            'preferred_language', 'business_name', 'business_license', 'tax_id'
        )
    
    def validate(self, attrs):
        user = self.instance or self.context['request'].user
        
        # Only allow host-specific fields for hosts
        if not user.is_host():
            attrs.pop('business_name', None)
            attrs.pop('business_license', None)
            attrs.pop('tax_id', None)
        
        return attrs


class SwitchToHostSerializer(serializers.Serializer):
    """Serializer for switching from guest to host"""
    business_name = serializers.CharField(max_length=200, required=False)
    business_license = serializers.CharField(max_length=100, required=False)
    tax_id = serializers.CharField(max_length=50, required=False)
    hosting_experience = serializers.CharField(required=False)
    property_types = serializers.ListField(required=False)
    
    def validate(self, attrs):
        user = self.context['request'].user
        
        if not user.is_guest():
            raise serializers.ValidationError("Only guests can switch to host role.")
        
        return attrs
    
    def save(self, **kwargs):
        user = self.context['request'].user
        
        # Switch role
        user.switch_to_host()
        
        # Update business information
        if self.validated_data.get('business_name'):
            user.business_name = self.validated_data['business_name']
        if self.validated_data.get('business_license'):
            user.business_license = self.validated_data['business_license']
        if self.validated_data.get('tax_id'):
            user.tax_id = self.validated_data['tax_id']
        
        user.save()
        
        # Update profile
        profile = user.profile
        if self.validated_data.get('hosting_experience'):
            profile.hosting_experience = self.validated_data['hosting_experience']
        if self.validated_data.get('property_types'):
            profile.property_types = self.validated_data['property_types']
        
        profile.save()
        
        # Create host verification
        HostVerification.objects.get_or_create(user=user)
        
        return user


class HostVerificationSerializer(serializers.ModelSerializer):
    """Host verification serializer"""
    user = UserSerializer(read_only=True)
    verified_by = UserSerializer(read_only=True)
    completion_percentage = serializers.DecimalField(
        source='verification_completion_percentage', 
        max_digits=5, decimal_places=2, read_only=True
    )
    
    class Meta:
        model = HostVerification
        fields = '__all__'
        read_only_fields = [
            'id', 'user', 'identity_verified', 'address_verified', 
            'business_verified', 'verified_by', 'verified_at',
            'completion_percentage', 'created_at', 'updated_at'
        ]


class HostApprovalSerializer(serializers.ModelSerializer):
    """Serializer for host approval actions"""
    approval_notes = serializers.CharField(required=False)
    
    class Meta:
        model = User
        fields = ['host_approval_status', 'approval_notes']
    
    def validate_host_approval_status(self, value):
        if value not in ['approved', 'rejected', 'pending']:
            raise serializers.ValidationError("Invalid approval status")
        return value
    
    def update(self, instance, validated_data):
        status = validated_data.get('host_approval_status')
        
        if status == 'approved':
            instance.is_verified_host = True
            instance.host_approval_status = 'approved'
        elif status == 'rejected':
            instance.is_verified_host = False
            instance.host_approval_status = 'rejected'
        elif status == 'pending':
            instance.is_verified_host = False
            instance.host_approval_status = 'pending'
        
        instance.save()
        return instance


class UserActivitySerializer(serializers.ModelSerializer):
    """User activity serializer"""
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = UserActivity
        fields = '__all__'
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']


class FavoriteSerializer(serializers.ModelSerializer):
    """Serializer for user favorites."""

    listing_id = serializers.UUIDField(write_only=True)
    listing = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Favorite
        fields = ['id', 'listing_id', 'listing', 'notes', 'created_at']
        read_only_fields = ['id', 'listing', 'created_at']

    def get_listing(self, obj):
        return {
            'id': str(obj.listing.id),
            'title': obj.listing.title,
            'city': obj.listing.city,
            'country': obj.listing.country,
            'price_per_night': str(obj.listing.price_per_night),
            'cover_image': obj.listing.cover_image,
        }

    def create(self, validated_data):
        from listings.models import Listing
        request = self.context.get('request')
        user = request.user if request else None
        listing_id = validated_data.pop('listing_id')

        try:
            listing = Listing.objects.get(id=listing_id, is_active=True)
        except Listing.DoesNotExist:
            raise serializers.ValidationError({'listing_id': 'Invalid or inactive listing.'})

        favorite, _created = Favorite.objects.get_or_create(
            user=user,
            listing=listing,
            defaults={'notes': validated_data.get('notes', '')},
        )
        if 'notes' in validated_data:
            favorite.notes = validated_data['notes']
            favorite.save(update_fields=['notes'])
        return favorite


class PasswordChangeSerializer(serializers.Serializer):
    """Serializer for password change"""
    old_password = serializers.CharField(style={'input_type': 'password'})
    new_password = serializers.CharField(
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    new_password_confirm = serializers.CharField(style={'input_type': 'password'})
    
    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is not correct.")
        return value
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError("New passwords don't match.")
        return attrs
    
    def save(self, **kwargs):
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user


class PasswordResetRequestSerializer(serializers.Serializer):
    """Serializer for password reset request"""
    email = serializers.EmailField()
    
    def validate_email(self, value):
        try:
            user = User.objects.get(email=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("No user found with this email address.")
        return value
    
    def save(self, **kwargs):
        email = self.validated_data['email']
        user = User.objects.get(email=email)
        
        # Generate reset token
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        
        # Send reset email (you'll need to implement email backend)
        self.send_reset_email(user, token, uid)
        
        return user
    
    def send_reset_email(self, user, token, uid):
        """Send password reset email"""
        # Implementation depends on your email configuration
        pass


class PasswordResetConfirmSerializer(serializers.Serializer):
    """Serializer for password reset confirmation"""
    uid = serializers.CharField()
    token = serializers.CharField()
    new_password = serializers.CharField(
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    new_password_confirm = serializers.CharField(style={'input_type': 'password'})
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError("Passwords don't match.")
        
        try:
            uid = force_str(urlsafe_base64_decode(attrs['uid']))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            raise serializers.ValidationError("Invalid token.")
        
        if not default_token_generator.check_token(user, attrs['token']):
            raise serializers.ValidationError("Invalid token.")
        
        attrs['user'] = user
        return attrs
    
    def save(self, **kwargs):
        user = self.validated_data['user']
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user


class EmailVerificationSerializer(serializers.Serializer):
    """Serializer for email verification"""
    token = serializers.CharField()
    
    def validate_token(self, value):
        try:
            user = User.objects.get(email_verification_token=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("Invalid verification token.")
        
        if user.email_verified:
            raise serializers.ValidationError("Email is already verified.")
        
        return value
    
    def save(self, **kwargs):
        token = self.validated_data['token']
        user = User.objects.get(email_verification_token=token)
        user.email_verified = True
        user.email_verification_token = None
        user.save()
        return user


# Admin-only serializers
class AdminUserSerializer(serializers.ModelSerializer):
    """Admin user serializer with all fields"""
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    profile = UserProfileSerializer(read_only=True)
    host_verification = HostVerificationSerializer(read_only=True)
    
    class Meta:
        model = User
        fields = '__all__'
        read_only_fields = ['id', 'password', 'date_joined', 'last_login']
    
    def update(self, instance, validated_data):
        # Handle host approval status changes
        if 'host_approval_status' in validated_data:
            status = validated_data['host_approval_status']
            if status == 'approved':
                instance.is_verified_host = True
            elif status == 'rejected':
                instance.is_verified_host = False
        
        return super().update(instance, validated_data) 