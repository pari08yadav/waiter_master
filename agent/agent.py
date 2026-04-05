import os
import json
import google.generativeai as genai
from agent.tools import get_all_orders, get_full_menu, get_order_status, update_order_status
from agent.prompts import SYSTEM_PROMPT, STAFF_PROMPT

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))


def chat(user_message, session_uid, restaurant_id=None, session=None):
    model = genai.GenerativeModel(
        model_name="gemini-2.5-flash",
        system_instruction=SYSTEM_PROMPT,
    )

    history = session.get("chat_history", []) if session else []

    convo = model.start_chat(history=history)

    if not history:
        menu = get_full_menu(restaurant_id=restaurant_id)
        menu_json = json.dumps(menu, indent=2)
        first_message = f"Here is the complete restaurant menu:\n{menu_json}\n\nCustomer question: {user_message}"
        response = convo.send_message(first_message)
    else:
        order_context = ""
        if any(word in user_message.lower() for word in ["order", "status", "placed", "my order"]):
            orders = get_order_status(session_uid)
            if orders:
                order_context = f"\n\nCustomer's current orders:\n{json.dumps(orders, indent=2)}"
        response = convo.send_message(user_message + order_context)

    if session is not None:
        updated_history = []
        for msg in convo.history:
            updated_history.append({
                "role": msg.role,
                "parts": [p.text for p in msg.parts],
            })
        session["chat_history"] = updated_history

    return response.text



# def staff_chat(user_message, restaurant_id, session=None):
#     model = genai.GenerativeModel(
#         model_name="gemini-2.5-flash",
#         system_instruction="""You are a smart restaurant staff assistant.
#                 You have access to all current orders for the restaurant.
#                 You can help staff with:
#                 - Summarizing pending, accepted, making or completed orders
#                 - Finding specific orders by table number or status
#                 - Updating order status when staff asks to accept, reject, or complete an order
#                 - Answering any question about current orders

#                 When staff asks to update an order status, extract the order uid and new status from their message and call update_order_status.
#                 Always be concise and professional.""",
#             )

#     history = session.get("staff_chat_history", []) if session else []
#     convo = model.start_chat(history=history)

#     if not history:
#         orders = get_all_orders(restaurant_id=restaurant_id)
#         import json
#         orders_json = json.dumps(orders, indent=2)
#         first_message = f"Here are all current orders for the restaurant:\n{orders_json}\n\nStaff question: {user_message}"
#         response = convo.send_message(first_message)
#     else:
#         # refresh orders on every follow up — orders change frequently
#         orders = get_all_orders(restaurant_id=restaurant_id)
#         orders_json = json.dumps(orders, indent=2)
#         message_with_context = f"Latest orders:\n{orders_json}\n\nStaff question: {user_message}"
#         response = convo.send_message(message_with_context)

#     if session is not None:
#         updated_history = []
#         for msg in convo.history:
#             updated_history.append({
#                 "role": msg.role,
#                 "parts": [p.text for p in msg.parts],
#             })
#         session["staff_chat_history"] = updated_history

#     return response.text



def staff_chat(user_message, restaurant_id, session=None):
    
    staff_tools = [
        {
            "function_declarations": [
                {
                    "name": "update_order_status",
                    "description": "Update the status of an order. Use this when staff asks to accept, reject, start making or complete an order.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "order_uid": {
                                "type": "string",
                                "description": "The UID of the order to update"
                            },
                            "status": {
                                "type": "string",
                                "enum": ["PENDING", "ACCEPTED", "REJECTED", "MAKING", "COMPLETED", "CANCELLED"],
                                "description": "The new status to set"
                            }
                        },
                        "required": ["order_uid", "status"]
                    }
                }
            ]
        }
    ]

    model = genai.GenerativeModel(
        model_name="gemini-2.5-flash",
        system_instruction=STAFF_PROMPT,
        tools=staff_tools,
    )

    history = session.get("staff_chat_history", []) if session else []
    convo = model.start_chat(
        history=history,
        enable_automatic_function_calling=False
    )

    # always send fresh orders with every message
    orders = get_all_orders(restaurant_id=restaurant_id)
    orders_json = json.dumps(orders, indent=2)

    if not history:
        message = f"Here are all current orders:\n{orders_json}\n\nStaff question: {user_message}"
    else:
        message = f"Latest orders:\n{orders_json}\n\nStaff question: {user_message}"

    convo.send_message(message)

    # agentic loop
    while True:
        response = convo.last
        candidate = response.candidates[0].content.parts[0]

        if candidate.function_call.name:
            fn_name = candidate.function_call.name
            fn_args = dict(candidate.function_call.args)

            if fn_name == "update_order_status":
                result = update_order_status(**fn_args)

            convo.send_message(
                genai.protos.Content(
                    parts=[genai.protos.Part(
                        function_response=genai.protos.FunctionResponse(
                            name=fn_name,
                            response={"result": result},
                        )
                    )]
                )
            )
        else:
            break

    if session is not None:
        updated_history = []
        for msg in convo.history:
            updated_history.append({
                "role": msg.role,
                "parts": [p.text for p in msg.parts],
            })
        session["staff_chat_history"] = updated_history

    return candidate.text
