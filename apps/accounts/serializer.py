from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate

User = get_user_model()

class CreateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('email', 'phone', 'password', 'first_name', 'last_name')
        extra_kwargs = {'password': {'write_only': True}}
        
    def create(self, validated_data):
        email = validated_data.pop('email')
        password = validated_data.pop('password')
        user = User.objects.create_user(email=email, password=password ,**validated_data)
        return user

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'phone', 'email', 'first_name', 'last_name')

class UpdateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('email', 'phone', 'first_name', 'last_name')

class LoginSerializer(serializers.Serializer):
    email = serializers.CharField()
    password = serializers.CharField(
        style={'input_type': 'password'}, trim_whitespace=False
    )
    
    def validate(self, data):
        email = data.get('email')
        password = data.get('password')
        
        if email and password:
            user = authenticate(request=self.context.get('request'), username=email, password=password)

            if not user:
                raise serializers.ValidationError({
                    'detail': 'Email and password do not match. Try again.',
                    'status': False,
                }, code='authorization')
        
        else:
            raise serializers.ValidationError({
                'detail': 'Email and password must be provided.',
                'status': False,
            }, code='authorization')

        data['user'] = user
        return data    
