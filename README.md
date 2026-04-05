
# 🍽️ Waiter

A contactless restaurant ordering system with a built-in GenAI agent. Customers scan a QR code on their table, browse the menu, place an order, and track it live — all from their phone. Staff see new orders instantly on their dashboard and can manage them via an AI assistant.

🔗 Live Demo: [waiterrr.onrender.com](https://waiterrr.onrender.com/)

---

## How it works

1. Restaurant owner creates a restaurant, adds tables and a menu
2. Each table gets an auto-generated QR code
3. Customer scans the QR → browses menu → asks AI assistant → adds to cart → places order
4. Staff dashboard receives the order instantly via WebSocket
5. Staff updates the order status manually or via AI assistant ("accept table 3")
6. Customer sees the status update live on their screen

---

## Tech Stack

|                  | Technology                       |
| ---------------- | -------------------------------- |
| Backend          | Django 5.1                       |
| Real-time        | Django Channels 4 + WebSocket    |
| ASGI Server      | Daphne                           |
| REST API         | Django REST Framework            |
| Database         | SQLite (dev) / PostgreSQL (prod) |
| Channel Layer    | In-Memory (dev) / Redis (prod)   |
| Frontend         | Django Templates + Vite          |
| Static Files     | Whitenoise                       |
| Media Storage    | Local / AWS S3 / Cloudinary      |
| Background Tasks | Celery                           |
| QR Codes         | qrcode                           |
| AI Agent         | Google Gemini 1.5 Flash          |

---

## Project Structure

```
waiter-master/
├── waiter/
│   ├── asgi.py         # Routes HTTP vs WebSocket traffic
│   ├── settings.py     # All configuration
│   └── urls.py         # Root URL config
├── common/
│   ├── models.py       # All database models
│   ├── views.py        # Page views + REST API views
│   ├── consumers.py    # WebSocket handler (real-time orders)
│   ├── routing.py      # WebSocket URL routing + middleware
│   ├── serializers.py  # Model → JSON converters
│   ├── taxonomies.py   # Enums (OrderStatus, MenuType, PriceType)
│   ├── urls.py         # All HTTP URL patterns
│   ├── signals.py      # Auto-clears chat history on menu change
│   └── templates/      # HTML templates
├── agent/
│   ├── prompts.py      # System prompts for customer and staff agents
│   ├── tools.py        # DB query and write functions
│   ├── agent.py        # Gemini agentic loop — customer and staff chat
│   └── views.py        # REST API endpoints for agent chat
```

---

## Getting Started

1. Clone and install dependencies

```bash
git clone <repo-url>
cd waiter-master
pip install -r requirements.txt
```

2. Set up environment variables

```bash
cp .env.template .env
# Fill in the values in .env
```

3. Run migrations and start the server

```bash
python manage.py migrate
daphne waiter.asgi:application
```

Visit `http://localhost:8000` — log in at `/login/` to access the dashboard.

---

## Environment Variables

| Variable              | Description                              |
| --------------------- | ---------------------------------------- |
| `DJANGO_SECRET_KEY` | Django secret key                        |
| `DEBUG`             | `True` for dev, `False` for prod     |
| `ALLOWED_HOSTS`     | Comma-separated allowed hostnames        |
| `BASE_URL`          | Used to generate QR code URLs            |
| `AWS_STORAGE_*`     | S3 credentials (only if `USE_S3=True`) |
| `GEMINI_API_KEY`    | Google Gemini API key (get free at [aistudio.google.com](https://aistudio.google.com)) |

---

## Key Pages

| URL                                        | Who uses it | What it does              |
| ------------------------------------------ | ----------- | ------------------------- |
| `/`                                      | Everyone    | Home page                 |
| `/login/`                                | Staff       | Login                     |
| `/dashboard/`                            | Staff       | List of restaurants       |
| `/dashboard/restaurant/<uid>/`           | Staff       | Tables + categories       |
| `/dashboard/order/<uid>/`                | Staff       | Live order feed + AI chat |
| `/table/<uid>/`                          | Customer    | Browse menu + AI chat     |
| `/table/<uid>/order/`                    | Customer    | View & place order        |
| `/table/<uid>/chat/`                     | Customer    | AI agent API endpoint     |
| `/dashboard/restaurant/<uid>/agent/`     | Staff       | Staff AI agent API endpoint |

---

## Real-Time Orders (WebSocket)

The app uses Django Channels to push order updates to the browser without any page refresh.

Connection URL: `ws/order/<uid>/`

- Staff connects with a restaurant UID → watches all orders for that restaurant
- Customer connects with their session UID → watches their own orders

What happens when a customer places an order:

```
Customer submits order
    → Order saved to DB
    → WebSocket push to customer's session group  (customer sees their order)
    → WebSocket push to restaurant group          (staff dashboard updates)
```

What happens when staff updates an order status:

```
Staff clicks "Accept" on dashboard (or tells AI assistant)
    → WebSocket message sent to server
    → Order status updated in DB
    → WebSocket push to customer's session group  (customer sees "Accepted")
    → WebSocket push to restaurant group          (dashboard reflects change)
```

---

## AI Agent

The app has two AI assistants powered by Google Gemini 1.5 Flash.

### Customer Agent

Accessible via the chat widget on the menu page (`/table/<uid>/`).

- Answers any question about the menu — prices, ingredients, veg/non-veg, comparisons
- Tracks customer order status
- Stateful — remembers conversation context across messages
- Full menu JSON sent only on the first message, follow-ups send only the question
- Chat history auto-clears when menu items are added or removed

```
Customer: "show me veg items under ₹150"
    → Gemini reads full menu JSON → filters and replies
Customer: "which one has paneer?"
    → Gemini remembers previous context → answers without re-sending menu
```

### Staff Agent

Accessible via the chat widget on the order dashboard (`/dashboard/order/<uid>/`).

- Summarizes pending, accepted, making or completed orders
- Answers questions about current orders by table or status
- **Can update order status directly** — staff says "accept table 3" → DB updated → customer notified via WebSocket
- Fresh orders fetched on every message since orders change frequently

```
Staff: "accept the order from table 3"
    → Gemini identifies order UID from orders data
    → Calls update_order_status(uid, "ACCEPTED")
    → DB updated + WebSocket pushed to customer
    → "Order from Table 3 accepted. Customer has been notified."
```

### Agent Tools

| Tool | Used by | What it does |
| ---- | ------- | ------------ |
| `get_full_menu` | Customer agent | Fetches all menu items from DB |
| `get_order_status` | Customer agent | Fetches customer's current orders |
| `get_all_orders` | Staff agent | Fetches last 20 orders for restaurant |
| `update_order_status` | Staff agent | Updates order in DB + pushes WebSocket |

For full AI implementation details see [AI_DOCUMENTATION.md](./AI_DOCUMENTATION.md).

---

## Future Improvements

### Must-have

- Switch channel layer to Redis — the current in-memory layer doesn't work across multiple server processes, so it will break in any real production deployment
- Switch database to PostgreSQL — SQLite is not suitable for production; it doesn't handle concurrent writes well
- Online payment integration — currently there's no way to pay; adding Razorpay or Stripe would complete the ordering flow
- Proper customer authentication — right now customers are tracked only by session cookie, which breaks if they clear cookies or switch browsers

### Should-have

- Order history for customers — customers have no way to see past orders after their session ends
- Push notifications — notify staff on mobile when a new order arrives, even if the dashboard tab is in the background
- Menu item images — the model supports images but the upload flow in the dashboard needs improvement
- Table-level bill splitting — allow multiple customers at the same table to split the bill
- Estimated wait time — show customers an approximate time before their order is ready
- Store AI chat history in DB — currently lost if customer clears cookies

### Nice-to-have

- Multi-language support — Gemini handles this automatically, just needs prompt update
- Analytics dashboard — most ordered items, peak hours, revenue per day
- Printer integration — auto-print order tickets in the kitchen when an order is placed
- Dark mode for the customer-facing menu
- Accessibility improvements — better screen reader support and keyboard navigation
- Switch to Qdrant vector search — when menu grows beyond 500+ items for efficient semantic search

---

## Documentation

- For architecture, models, WebSocket flow and API endpoints see [DOCUMENTATION.md](./DOCUMENTATION.md)
- For AI agent structure, flow, tools and automation details see [AI_DOCUMENTATION.md](./AI_DOCUMENTATION.md)
