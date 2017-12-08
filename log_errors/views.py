from rest_framework.permissions import AllowAny
from rest_framework.renderers import JSONRenderer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .forms import LogErrorForm

class LogError(APIView):
    renderer_classes = [JSONRenderer]
    permission_classes = (AllowAny,)

    def post(self, request):
        form = LogErrorForm(request.data)
        if form.is_valid():
            form.save()
        return Response({"message": "Message has been send successfully."}, status=status.HTTP_200_OK)


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