from typing import Protocol


class CustomerChatGateway(Protocol):
    def reply(
        self, *, user_message: str, session_uid: str, restaurant_id: int, table_uid: str, session
    ) -> str: ...


class StaffChatGateway(Protocol):
    def reply(self, *, user_message: str, restaurant_id: int, session) -> str: ...
