import uuid
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import AllowAny
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from common.models import Restaurant, Table
from agent.agent import chat, staff_chat


class AgentChatView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request, table_uid):
        message = request.data.get("message", "").strip()
        if not message:
            return Response({"error": "message is required"}, status=HTTP_400_BAD_REQUEST)

        table = get_object_or_404(Table, uid=table_uid)
        session_uid = request.session.get("uid", str(uuid.uuid4()))
        request.session["uid"] = session_uid

        reply = chat(
            user_message=message,
            session_uid=session_uid,
            restaurant_id=table.restaurant_id,
            session=request.session,
        )
        return Response({"reply": reply}, status=HTTP_200_OK)


@method_decorator(login_required, name="dispatch")
class StaffAgentChatView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request, uid):
        message = request.data.get("message", "").strip()
        if not message:
            return Response({"error": "message is required"}, status=HTTP_400_BAD_REQUEST)

        restaurant = get_object_or_404(Restaurant, uid=uid, chain=request.chain)

        reply = staff_chat(
            user_message=message,
            restaurant_id=restaurant.id,
            session=request.session,
        )
        return Response({"reply": reply}, status=HTTP_200_OK)
