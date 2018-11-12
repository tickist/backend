#-*- coding: utf-8 -*-
from datetime import datetime
from django.conf import settings
from django.contrib.auth import login
from django.utils.translation import ugettext as _
from django.db import IntegrityError, transaction
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.http import HttpRequest
from rest_framework import status, viewsets
from rest_framework.views import APIView
from rest_framework.decorators import detail_route, renderer_classes, parser_classes
from rest_framework.response import Response
from rest_framework.parsers import FileUploadParser
from rest_framework.renderers import JSONRenderer, MultiPartRenderer
from rest_framework.permissions import AllowAny
from social_django.views import complete
from social_django.utils import psa, load_strategy
from social_django.views import _do_login
from social_django.models import UserSocialAuth
from emails.utils import async_send_email
from users.serializers import UserSerializer, SimpleUserSerializer, SimpleUserWithListsSerializer
from users.models import User
from users.forms import AddingTeamMate, DeleteTeamMate, ChangePasswordForm, ChangeUserDetailsForm, \
    SendMessegaToBoardForm, ChangeAvatarForm, ForgotPasswordForm
from dashboard.tasks.models import Tag
from dashboard.tasks.serializers import TagSerializer, SimpleTagSerializer
from dashboard.tasks.forms import TagForm
from commons.utils import send_email_to_admins, gen_passwd
from calendar import timegm


class UserViewSet(viewsets.ModelViewSet):
    """

    """
    model = User
    queryset = User.objects.filter(is_active=True)
    #renderer_classes = [MultiPartRenderer, JSONRenderer]
    #parser_classes = [FileUploadParser, JSONParser]

    def get_object(self):
        return self.request.user

    def get_serializer_class(self):
        if self.request.method.lower() in ["post", "get"]:
            return UserSerializer
        else:
            return SimpleUserSerializer

    @detail_route(methods=["put"])
    def changepassword(self, request, pk=None):
        data = request.data.copy()
        form = ChangePasswordForm(data, user=request.user)
        if form.is_valid():
            request.user.set_password(form.cleaned_data['new_password'])
            request.user.save()
            return Response({'message': _('The password has been changed.')}, status=status.HTTP_200_OK)
        return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk, format=None):
        data = request.data.copy()
        form = ChangeUserDetailsForm(data, instance=request.user)
        if form.is_valid():
            user = form.save()
            data = UserSerializer(user).data
            data['message'] = _("User details have been changed.")
            return Response(data, status=status.HTTP_200_OK)
        return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)

    @detail_route(methods=["get"])
    def teamlist(self, request, pk=None):
        data = SimpleUserWithListsSerializer(self.request.user.all_team_mates(), many=True, context={"user_lists_pk": request.user.all_lists_pk}).data
        return Response(data, status=status.HTTP_200_OK, content_type="application/json")

    @parser_classes(FileUploadParser)
    @renderer_classes((MultiPartRenderer))
    @detail_route(methods=["post"])
    def changeavatar(self, request, pk=None):
        data = request.data
        files = request.FILES
        form = ChangeAvatarForm(data=data, files=files)

        if form.is_valid():
            request.user.avatar_save(form.cleaned_data['file'])
            return Response({'message': "Avatar has been changed."}, status=status.HTTP_200_OK)
        return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)

    @detail_route(methods=["post"])
    def checkteammember(self, request, pk=None):
        data = request.data.copy()
        try:
            if 'email' in data and 'email' in data['email']:
                email = data['email']['email']
            elif 'email' in data:
                email = data['email']
            else:
                email = ""
            validate_email(email)
        except ValidationError as e:
            data = {"errors": "Email is invalid" }
            my_status = status.HTTP_400_BAD_REQUEST
        else:
            try:
                user = User.objects.get(email=email, is_active=True)
                data = SimpleUserWithListsSerializer(user).data
            except (User.DoesNotExist, KeyError):
                data = {"email": data['email'], "username": data['email'], "avatar_url": "/" + settings.DEFAULT_AVATAR,
                        "avatar": "", "status": "pending"}
            my_status = status.HTTP_200_OK
        return Response(data, status=my_status)




class UserTagsViewSet(viewsets.ModelViewSet):
    """
        Class view to list members of Team
    """
    model = Tag
    base_name = "tag"

    def get_serializer_class(self):
        if self.request.method.lower() in ["post", "get"]:
            return TagSerializer
        else:
            return SimpleTagSerializer

    def get_queryset(self):
        return Tag.objects.filter(author=self.request.user)

    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        user = User.objects.get(id=self.request.user.pk)
        form = TagForm(data, user=user.pk)
        if form.is_valid():
            try:
                 with transaction.atomic():
                     tag = form.save()
            except IntegrityError:
                tag = Tag.objects.get(name=form.cleaned_data['name'], author=self.request.user)
            data = TagSerializer(tag).data
            return Response(data, status=status.HTTP_201_CREATED)
        return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk, format=None):
        data = request.data
        form = TagForm(data, user=request.user.pk, instance=self.get_object())
        if form.is_valid():
            tag = form.save()
            data = TagSerializer(tag).data
            return Response(data, status=status.HTTP_200_OK)

        return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        data = {"name": self.get_object().name}

        form = TagForm(data, user=request.user.pk, instance=self.get_object())
        if form.is_valid():
            form.instance.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)


class SendMessageToBoard(APIView):
    renderer_classes = [JSONRenderer]

    def put(self, request):
        data = request.data
        data['user'] = request.user.id
        form = SendMessegaToBoardForm(data)
        if form.is_valid():
            message = form.save()
            send_email_to_admins(topic="Message from user", template="users/email/email_to_administrator.html",
                                                                data={"user": message.user,
                                                                      "message": message.message})
            return Response({"message": "Message has been send successfully."}, status=status.HTTP_200_OK)
        return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)


class ForgotPassword(APIView):
    renderer_classes = [JSONRenderer]
    authentication_classes = []
    permission_classes = (AllowAny,)

    def post(self, request):
        data = request.data
        form = ForgotPasswordForm(data=data)
        if form.is_valid():
            user = User.objects.get(email=form.cleaned_data['email'], is_active=True)
            new_password = gen_passwd(length=15)
            user.set_password(new_password)
            user.save()
            async_send_email.apply_async(kwargs={"topic": _("Forgotten password"), "template": "login/emails/remember_password.html",
                   "email": user.email, "data_email": {"user": user, "new_password": new_password},
                   "user": user})

            return Response({'message': "You will shortly receive an email with your new password. After logging in, you can set a new password in user settings. Please be sure to check your spam folder if you don't see the password reset email after a few minutes."}, status=status.HTTP_200_OK)
        return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)


class Complete_login_user_google_plus(APIView):
    #USUN
    renderer_classes = [JSONRenderer]
    authentication_classes = []
    permission_classes = (AllowAny,)

    def post(self, request):
        data = request.data
        backend = "google-plus"
        req = HttpRequest()
        req.method = 'POST'
        req.session = request.session

        req.META = request.META
        req.user = request.user

        req.POST = {'access_token': data['access_token'], 'code': data['code']}
        req.REQUEST = req.POST
        response = complete(req, backend=backend)
        return response


@psa()
def auth_by_token(request, backend):
    backend = request.backend
    user=request.user
    user = backend.do_auth(
        access_token=request.data.get('access_token'),
        user=user.is_authenticated and user or None
        )
    if user and user.is_active:
        return user# Return anything that makes sense here
    else:
        return None


class SocialLogin(APIView):
    renderer_classes = [JSONRenderer]
    authentication_classes = []
    permission_classes = (AllowAny,)

    def post(self, request):
        auth_token = request.data.get('access_token', None)
        backend = request.data.get('backend', None)
        if auth_token and backend:
            if backend == "facebook":
                try:
                    user = auth_by_token(request, backend)
                except Exception as err:
                    return Response(str(err), status=400)
                if user:
                    strategy = load_strategy(request=request)
                    _do_login(request.backend, user, UserSocialAuth.objects.get(user=user))
                    # JWT login
                    # @TODO Change it to the new JWT plugin
                    #payload = jwt_payload_handler(user)
                    # Include original issued at time for a brand new token,
                    # to allow token refresh
                    if api_settings.JWT_ALLOW_REFRESH:
                        payload['orig_iat'] = timegm(
                            datetime.utcnow().utctimetuple()
                        )

                    user.backend = 'django.contrib.auth.backends.ModelBackend'
                    login(request, user)
                    return Response({'token': 'None', 'user_id': user.id}, status=status.HTTP_201_CREATED)
                    #return Response({'token':jwt_encode_handler(payload), 'user_id': user.id}, status=status.HTTP_201_CREATED)

                else:
                    return Response("Bad Credentials", status=403)
            elif backend == "google-plus":
                data = request.data
                req = HttpRequest()
                req.method = 'POST'
                req.session = request.session

                req.META = request.META
                req.user = request.user

                req.POST = {'access_token': data['access_token'], 'code': data['code']}
                req.REQUEST = req.POST
                #response = complete(req, backend=backend)
                try:
                    user = auth_by_token(request, backend)
                except Exception as err:
                    return Response(str(err), status=400)
                if user:
                    strategy = load_strategy(request=request)
                    _do_login(request.backend, user, UserSocialAuth.objects.get(user=user))
                    # JWT login
                    # @TODO Change it to the new JWT plugin
                    #payload = jwt_payload_handler(user)
                    # Include original issued at time for a brand new token,
                    # to allow token refresh
                    if api_settings.JWT_ALLOW_REFRESH:
                        payload['orig_iat'] = timegm(
                            datetime.utcnow().utctimetuple()
                        )

                    user.backend = 'django.contrib.auth.backends.ModelBackend'
                    login(request, user)
                    return Response({'token':'None', 'user_id': user.id}, status=status.HTTP_201_CREATED)
                    #return Response({'token':jwt_encode_handler(payload), 'user_id': user.id}, status=status.HTTP_201_CREATED)
        else:
            return Response("Bad request", status=400)
