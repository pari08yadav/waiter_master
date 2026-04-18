from agent.agent import customer_chat, staff_chat


class GeminiCustomerChatGateway:
    def reply(
        self, *, user_message: str, session_uid: str, restaurant_id: int, table_uid: str, session
    ) -> str:
        return customer_chat(
            user_message=user_message,
            session_uid=session_uid,
            restaurant_id=restaurant_id,
            table_uid=table_uid,
            session=session,
        )


class GeminiStaffChatGateway:
    def reply(self, *, user_message: str, restaurant_id: int, session) -> str:
        return staff_chat(
            user_message=user_message, restaurant_id=restaurant_id, session=session
        )
