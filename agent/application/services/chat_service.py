import uuid

from django.shortcuts import get_object_or_404

from agent.domain.ports import CustomerChatGateway, StaffChatGateway
from agent.infrastructure.gemini_chat_gateway import (
    GeminiCustomerChatGateway,
    GeminiStaffChatGateway,
)
from restaurants.models import Restaurant, Table


class ChatService:
    """Application service for customer/staff chat orchestration."""

    @staticmethod
    def customer_reply(
        *,
        request,
        table_uid,
        message: str,
        gateway: CustomerChatGateway | None = None,
    ) -> str:
        table = get_object_or_404(Table, uid=table_uid)
        session_uid = request.session.get("uid", str(uuid.uuid4()))
        request.session["uid"] = session_uid
        client = gateway or GeminiCustomerChatGateway()
        return client.reply(
            user_message=message,
            session_uid=session_uid,
            restaurant_id=table.restaurant_id,
            table_uid=str(table_uid),
            session=request.session,
        )

    @staticmethod
    def staff_reply(
        *,
        request,
        restaurant_uid,
        message: str,
        gateway: StaffChatGateway | None = None,
    ) -> str:
        restaurant = get_object_or_404(
            Restaurant, uid=restaurant_uid, chain=request.chain
        )
        client = gateway or GeminiStaffChatGateway()
        return client.reply(
            user_message=message,
            restaurant_id=restaurant.id,
            session=request.session,
        )
