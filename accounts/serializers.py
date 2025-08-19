from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import User


class UserSerializer(serializers.ModelSerializer):
	class Meta:
		model = User
		fields = [
			'id', 'username', 'email', 'first_name', 'last_name',
			'headline', 'bio', 'location', 'industry',
			'profile_photo', 'cover_photo',
			'skills', 'experiences', 'educations', 'websites', 'contact',
			'date_joined', 'created_at',
		]
		read_only_fields = ['id', 'date_joined', 'created_at', 'username', 'email']


class RegistrationSerializer(serializers.ModelSerializer):
	password = serializers.CharField(write_only=True, required=True, validators=[validate_password])

	class Meta:
		model = User
		fields = ['id', 'username', 'email', 'password', 'first_name', 'last_name']
		read_only_fields = ['id']

	def create(self, validated_data):
		user = User.objects.create_user(
			username=validated_data['username'],
			email=validated_data.get('email', ''),
			password=validated_data['password'],
			first_name=validated_data.get('first_name', ''),
			last_name=validated_data.get('last_name', ''),
		)
		return user


class PasswordChangeSerializer(serializers.Serializer):
	old_password = serializers.CharField(write_only=True)
	# new_password = serializers.CharField(write_only=True, validators=[validate_password])