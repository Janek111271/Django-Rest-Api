from django.contrib.auth import get_user_model, authenticate
from django.utils.translation import gettext as translate
from rest_framework import serializers
from core.models import Address


class AddressSerializer(serializers.ModelSerializer):

    class Meta:
        model = Address
        fields = ['id', 'street', 'house_number', 'city', 'post_code']
        read_only_fields = ['id']


class UserSerializer(serializers.ModelSerializer):
    address = AddressSerializer(many=True, required=False)

    class Meta:
        model = get_user_model()
        fields = ['email', 'password', 'name', 'address']
        extra = {'password': {'write_only': True, 'min_length': 5}}

    def create(self, validated_data):

        return get_user_model().objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        user = super().update(instance, validated_data)

        if password:
            user.set_password(password)
            user.save()

        return user


class AuthTokenSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(
        style={'input_type': 'password'},
        trim_whitespace=True,
    )

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        user = authenticate(
            request=self.context.get('request'),
            username=email,
            password=password,
        )
        if not user:
            msg = translate('Unable to authenticate')
            raise serializers.ValidationError(msg, code='authorization')

        attrs['user'] = user
        return attrs
