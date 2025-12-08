# PixelPet Web App**

## **Purpose**

Create a small but complete web application where a user can adopt and take care of a virtual pixel pet (similar to a Tamagotchi). The pet has needs (hunger, happiness, sleep) that change over time, and the user interacts through simple actions.

The app should feel playful, minimalistic, and fun.

---

## **Requirements**

### **Core Features**

1. **User Authentication**

   * Email/password login
   * Stored sessions
   * Only logged-in users can interact with their pet.

2. **Pet State Machine**

   * Each user has exactly one pet.
   * Pet properties:

     * `name`
     * `species` (from predefined list: otter, cat, dragon, axolotl)
     * `hunger` (0–100)
     * `happiness` (0–100)
     * `energy` (0–100)
   * Values should decay over time (at least every minute).

3. **User Actions**

   * Feed → increases hunger, decreases happiness if overfed
   * Play → increases happiness, decreases energy
   * Sleep → restores energy but user cannot interact while sleeping

4. **Pet Evolution**

   * If all stats stay above 70 for 24 hours → pet evolves into a cooler sprite.

5. **Persistence**

   * All user data and pet state stored in a database.

---

## **Frontend**

* Built as a simple responsive web UI using **FastAPI + Jinja2 templates** or **React (optional)**.
* Show:

  * Pixel art sprite of the pet
  * Bars for hunger, energy, happiness
  * Action buttons (Feed, Play, Sleep)
  * Notifications ("Your pet is hungry!", "Your dragon evolved! 🎉")

---

## **Backend**

* Use **FastAPI** as the web framework.
* Implement separate modules:

  * `auth.py`
  * `pet_model.py`
  * `pet_service.py`
  * `scheduler.py` (responsible for decay ticks)
  * `routes.py`

---

## **Database**

Use **SQLite** with SQLAlchemy ORM.

Tables:

| Table | Fields                                                                   |
| ----- | ------------------------------------------------------------------------ |
| users | id, email, password_hash, created_at                                     |
| pets  | id, user_id, name, species, hunger, happiness, energy, stage, updated_at |

---

## **Testing Requirements**

Write tests using **pytest** for:

* Authentication logic
* Pet state machine (hunger decay, evolution rules, action effects)
* API endpoint behavior (integration tests)
* At least one UI rendering test (if using templating)

Tests should run with an in-memory DB.

---

## **Non-Functional Requirements**

* Code must be modular and documented.
* Use type hints.
* Use linting (`ruff`) and formatting (`black`) if implemented.
* UI should be cute and simple — pixel style is preferred.

---

## **Stretch Goals (if time remains)**

* Real-time updates (WebSockets).
* Multiple pets per user.
* Leaderboard for “happiest pets”.
* Sprite animations.

---

## **Completion Definition**

The project is complete when:

* A user can sign up, get a pet, interact with it, and see stats change.
* Tests pass (`pytest` return code 0).
* The application can be started with a single command, e.g.:

```bash
uvicorn app.main:app --reload
```

---
