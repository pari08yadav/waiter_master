from django.urls import path

from agent.interfaces.http.views import AgentChatView, StaffAgentChatView

urlpatterns = [
    path("table/<uuid:table_uid>/chat/", AgentChatView.as_view(), name="agent-chat"),
    path("dashboard/restaurant/<uuid:uid>/agent/", StaffAgentChatView.as_view(), name="staff-agent-chat"),
]
