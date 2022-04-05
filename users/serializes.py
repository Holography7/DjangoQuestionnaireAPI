from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.contrib.auth.password_validation import validate_password
from users.models import UserAnswer, User, AnonymousUserAnswer, UserStatusInSurveys, AnonymousUserStatusInSurveys


class UserRegistrationSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )

    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'email', 'age', 'password', 'password2')

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})

        return attrs

    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            age=validated_data['age']
        )

        user.set_password(validated_data['password'])
        user.save()

        return user


class UserLoginSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('username', 'password')


class AnonymousUserStatusInSurveysSerializer(serializers.ModelSerializer):

    class Meta:
        model = AnonymousUserStatusInSurveys
        fields = ('survey',)


class UserStatusInSurveysSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserStatusInSurveys
        fields = ('user', 'survey')


class UserCompleteSurveySerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('completed_surveys',)


class UserAnswerSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserAnswer
        fields = ('survey', 'question', 'user', 'answer_text', 'answer_choose')


class AnonymousUserAnswerSerializer(serializers.ModelSerializer):

    class Meta:
        model = AnonymousUserAnswer
        fields = ('survey', 'question', 'user_anonymous_id', 'answer_text', 'answer_choose')


class QuestionForUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserAnswer
        fields = ('question', 'answer_text', 'answer_choose')


class UserAnswerShortSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserAnswer
        fields = ('question', 'answer_text', 'answer_choose')


class PlugSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('username',)


class CompleteSurveySerializer(serializers.ModelSerializer):
    class Meta:
        model = UserStatusInSurveys
        fields = ('user', 'survey', 'completed')
