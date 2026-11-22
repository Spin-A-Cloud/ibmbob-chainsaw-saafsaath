# SaafSaath — Scrap Pickup Marketplace

> Connecting Bengaluru households with scrap collectors for large-item pickups.

---

## Overview

SaafSaath is a two-sided marketplace that lets end customers schedule a pickup of large unwanted household items (beds, cots, sofas, wardrobes, etc.) and receive a price quotation from a registered scrap collection company. The customer reviews the quote, pays online, and the company arrives to collect the items.

---

## Actors

| Actor | Description |
|---|---|
| **Customer** | A Bengaluru resident who wants to dispose of large household items |
| **Scrap Company** | A registered scrap collector who reviews listings, raises quotations, and collects items |

---

## Core User Journeys

### Customer Journey

1. **Register / Log in** — create an account or sign in.
2. **Create a Pickup Request**
   - Select a **preferred date and time** for pickup.
   - Enter or pin a **location in Bengaluru** (address + map pin).
   - Add one or more **items**:
     - Upload one or more **photos** of the item.
     - Choose **item type** (e.g. bed, sofa, cot, wardrobe, refrigerator, other).
     - Set **condition**: `Ready to use` | `Needs repair` | `Not usable`.
     - Optional free-text description.
   - Submit the request.
3. **Receive Quotation** — get notified when the scrap company posts a price.
4. **Review & Accept** — view the itemised quote and accept or decline.
5. **Pay** — complete payment via the in-app payment flow.
6. **Await Pickup** — company arrives at the scheduled slot *(collection is out of scope)*.

### Scrap Company Journey

1. **Log in** to the company dashboard.
2. **Browse open requests** — view submitted pickup requests with photos, condition, location, and preferred timeslot.
3. **Raise a quotation** — enter a price per item or a total amount with optional notes.
4. **Track status** — see when the customer accepts and payment is confirmed.

---

## Functional Requirements

### Authentication
- Customer and company accounts are separate roles.
- Email + password login; optional OTP/social login (future).

### Pickup Request
- Date & time picker (must be a future slot).
- Location input: text address + optional map pin (Bengaluru area only for MVP).
- Multi-item support: add / remove items within a single request.
- Per-item: photo upload (multiple images), item type, condition.
- Request status lifecycle: `Draft` → `Submitted` → `Quoted` → `Accepted` → `Paid` → `Scheduled for Pickup`.

### Quotation
- Company can submit one quotation per request.
- Quotation contains: price breakdown per item, total, validity period, optional notes.
- Customer receives in-app notification + email when a quote is posted.
- Customer can **Accept** or **Decline** the quote.
  - On decline, request returns to `Submitted` state (company may revise).

### Payment
- Customer pays the quoted amount online (payment gateway integration required).
- Payment confirmation updates request status to `Paid`.
- Receipts sent via email.

### Notifications
- Customer: quote received, payment confirmed.
- Company: new request submitted, payment confirmed.

---

## Out of Scope (MVP)

- Physical item collection / logistics tracking.
- Multiple competing quotations from different companies.
- In-app chat between customer and company.
- Dynamic pricing / AI-based valuation.
- Areas outside Bengaluru.

---

## Data Model (High-Level)

```
User
  id, name, email, password_hash, role (customer | company), phone, created_at

PickupRequest
  id, customer_id, preferred_date, preferred_time, address, lat, lng
  status (draft | submitted | quoted | accepted | paid)
  created_at, updated_at

Item  (belongs to PickupRequest)
  id, request_id, item_type, condition (ready | needs_repair | not_usable)
  description, created_at

ItemPhoto  (belongs to Item)
  id, item_id, url, uploaded_at

Quotation  (belongs to PickupRequest)
  id, request_id, company_id, total_amount, notes, valid_until
  status (pending | accepted | declined), created_at

QuotationLineItem  (belongs to Quotation)
  id, quotation_id, item_id, price, notes

Payment
  id, quotation_id, customer_id, amount, gateway_ref, status, paid_at
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React (TypeScript) |
| Backend | FastAPI (Python) |
| Database | PostgreSQL |
| File Storage | S3-compatible object store (photos) |
| Payment Gateway | Razorpay (India) |
| Maps | Google Maps / Mapbox |
| Notifications | Email via SMTP; in-app via WebSocket or polling |

---

## Project Structure

```
ibmbob-chainsaw-saafsaath/
├── backend/          # FastAPI application
│   ├── main.py
│   ├── requirements.txt
│   └── ...
├── frontend/         # React application
│   ├── src/
│   └── ...
└── PROJECT.md        # This file
```

---

## Milestones

| # | Milestone | Scope |
|---|---|---|
| 1 | Auth & Skeleton | Login/register for both roles, basic routing |
| 2 | Pickup Request Flow | Create request, add items, upload photos |
| 3 | Quotation Flow | Company raises quote, customer accepts/declines |
| 4 | Payment | Payment gateway integration, status updates |
| 5 | Notifications | Email + in-app alerts |
| 6 | Polish & Launch | UI polish, error handling, production deployment |
