# from account import models
# from account.email import send_otp_to_email
# from rest_framework import serializers


# class UserSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = models.User
#         fields = [
#             "id",
#             "address",
#             "avatar",
#             "email",
#             "gender",
#             "is_active",
#             "is_verified",
#             "phone_number",
#             "total_completed_booking",
#             "username",
#             "is_salon",
#             "is_superuser",
#             "first_name",
#             "last_name",
#         ]
#         depth = 2


# class UserBaseViewSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = models.User
#         fields = [
#             "id",
#             "address",
#             "gender",
#             "phone_number",
#             "username",
#             "first_name",
#             "last_name",
#             "avatar",
#         ]
#         depth = 1


# class UserUpdateSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = models.User
#         fields = [
#             "avatar",
#             "first_name",
#             "last_name",
#             "gender",
#             "phone_number",
#             "first_name",
#             "last_name",
#             "username",
#         ]


# class UserRegisterInputSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = models.User
#         fields = [
#             "email",
#             "password",
#         ]

#     def save(self, **kwargs):
#         super().save(**kwargs)

#         password = self.validated_data["password"]
#         instance = self.instance
#         instance.set_password(password)
#         instance.save()
#         email = self.validated_data["email"]
#         send_otp_to_email(instance, email)


# class UserRegisterSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = models.User
#         fields = [
#             "id",
#             "address",
#             "avatar",
#             "email",
#             "gender",
#             "is_active",
#             "phone_number",
#             "total_completed_booking",
#             "username",
#             "is_verified",
#             "is_salon",
#             "is_superuser",
#             "first_name",
#             "last_name",
#         ]
