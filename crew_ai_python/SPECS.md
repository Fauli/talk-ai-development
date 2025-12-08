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

     * `name` (can be given by the user)
     * `species` (from predefined list: otter, cat, dragon, axolotl)
     * `hunger` (0–100)
     * `happiness` (0–100)
     * `energy` (0–100)
   * Values should decay over time (at least every minute).

3. **User Actions**

   * Home screen → Nice welcome page, show pet if user has one, otherwise register/login
   * Feed → `hunger += 20`, if hunger > 90 then `happiness -= 10` (overfed penalty)
   * Play → `happiness += 15`, `energy -= 10`
   * Sleep → pet sleeps for **2 minutes**, cannot interact while sleeping
     * When waking up: `energy += 30`

   **Stat Decay** (every minute while not sleeping):
   * `hunger -= 1`
   * `happiness -= 1`
   * `energy -= 1`

   **Initial Stats**: All stats start at 50 when pet is created.

4. **Pet Evolution**

   * If all stats stay above 50 for 5 minutes → pet evolves into a cooler sprite.

5. **Persistence**

   * All user data and pet state stored in a database.

---

## **Frontend**

* Built as a simple responsive web UI using **FastAPI + Jinja2 templates** or **React (optional)**.
* The site should be reachable under "/"
* It should provide at least the pet page and a login/register page
* The game screen shows:

  * Pixel art sprite of the pet (with emoji fallback if images don't exist)
  * Bars for hunger, energy, happiness
  * Action buttons (Feed, Play, Sleep)
  * Notifications ("Your pet is hungry!", "Your dragon evolved!")

### **CRITICAL: Frontend Implementation Requirements**

1. **HTML Page Routes (not JSON)**:
   * Routes like `/`, `/login`, `/game` MUST render Jinja2 templates returning `HTMLResponse`
   * Do NOT return JSON from page routes - use `templates.TemplateResponse()`
   * Create a separate `routes/pages.py` for HTML page routes

2. **Form-Based Authentication with Cookies**:
   * Login/register forms should POST to `/login` and `/register` (not `/auth/login`)
   * On successful auth, set an HTTP-only cookie: `response.set_cookie(key="access_token", value=token, httponly=True)`
   * Redirect to `/game` after login (use `RedirectResponse(url="/game", status_code=303)`)
   * Page routes should read auth from cookies, not headers

3. **JavaScript Must Use Cookies**:
   * All fetch() calls MUST include `credentials: 'include'` to send cookies
   * Do NOT use localStorage for tokens when using cookie-based auth
   * Example:
     ```javascript
     fetch('/pets/', {
         method: 'POST',
         credentials: 'include',  // REQUIRED for cookies
         headers: { 'Content-Type': 'application/json' },
         body: JSON.stringify(data)
     })
     ```

4. **API Auth Must Be Flexible**:
   * Create a `get_current_user_flexible()` function that accepts BOTH cookies AND Bearer tokens
   * This allows the same API endpoints to work for web UI (cookies) and API clients (Bearer)
   * Example:
     ```python
     def get_current_user_flexible(request: Request, db: Session = Depends(get_db)) -> User:
         token = request.cookies.get("access_token")  # Try cookie first
         if not token:
             auth_header = request.headers.get("Authorization")
             if auth_header and auth_header.startswith("Bearer "):
                 token = auth_header[7:]
         # ... decode token and return user
     ```

5. **Consistent Route Naming**:
   * JavaScript must call the exact same routes defined in FastAPI
   * If the API route is `GET /pets/`, JS must call `/pets/` (not `/pets/status`)
   * Document all API routes and ensure JS matches them exactly

---

## **Backend**

* Use **FastAPI** as the web framework.
* Implement separate modules:

  * `auth.py` - Password hashing, JWT creation, `get_current_user_flexible()` function
  * `models.py` - SQLAlchemy User and Pet models
  * `pet_service.py` - Pet logic (create, feed, play, sleep, decay, evolution)
  * `scheduler.py` - Background task for stat decay
  * `config.py` - Settings (SECRET_KEY, DATABASE_URL, etc.)
  * `database.py` - Database connection and session
  * `routes/pages.py` - HTML page routes (/, /login, /game, /logout)
  * `routes/auth.py` - JSON API auth routes (/auth/register, /auth/login)
  * `routes/pets.py` - JSON API pet routes (/pets/, /pets/feed, /pets/play, /pets/sleep)

### **Backend Implementation Requirements**

1. **Include pages router FIRST in main.py** so HTML routes take precedence:
   ```python
   app.include_router(pages.router)  # HTML routes first
   app.include_router(auth.router)
   app.include_router(pets.router)
   ```

2. **Static files must be mounted**:
   ```python
   app.mount("/static", StaticFiles(directory="app/static"), name="static")
   ```

3. **Templates directory structure**:
   ```
   app/
   ├── templates/
   │   ├── base.html      # Base template with header/footer
   │   ├── home.html      # Welcome page (/)
   │   ├── login.html     # Login/register forms
   │   └── pet.html       # Game page with pet display
   └── static/
       ├── css/style.css
       └── js/pet.js
   ```

4. **Routes __init__.py must export all routers**:
   ```python
   # app/routes/__init__.py
   from . import auth, pets, pages
   ```

---

## **Database**

Use **SQLite** with SQLAlchemy ORM.

Tables:

| Table | Fields |
| ----- | ------ |
| users | id, email, password_hash, created_at |
| pets  | id, user_id, name, species, hunger, happiness, energy, stage, is_sleeping, sleep_until, last_decay, evolution_eligible_since, created_at, updated_at |

### **Pet Model Details**

```python
class Pet(Base):
    __tablename__ = "pets"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)  # One pet per user
    name = Column(String, nullable=False)
    species = Column(String, nullable=False)  # otter, cat, dragon, axolotl

    # Stats (0-100)
    hunger = Column(Integer, default=50)
    happiness = Column(Integer, default=50)
    energy = Column(Integer, default=50)

    # Evolution
    stage = Column(String, default="baby")  # "baby" or "evolved"
    evolution_eligible_since = Column(DateTime, nullable=True)

    # Sleep
    is_sleeping = Column(Boolean, default=False)
    sleep_until = Column(DateTime, nullable=True)

    # Timestamps
    last_decay = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

---

## **Testing Requirements**

Write tests using **pytest** for:

* Registration logic
* Login logic
* Authentication logic
* Pet state machine (hunger decay, evolution rules, action effects)
* API endpoint behavior (integration tests)
* At least one UI rendering test (if using templating)

Tests should run with an in-memory DB.

### **Testing Notes**

* The root route `/` returns HTML, not JSON. Test it with:
  ```python
  def test_root_endpoint(client):
      response = client.get("/")
      assert response.status_code == 200
      assert "PixelPet" in response.text  # Check HTML content, not JSON
  ```
* API routes (`/pets/`, `/auth/*`) return JSON and can be tested with `response.json()`

---

## **Non-Functional Requirements**

* Code must be modular and documented.
* Use type hints.
* Use linting (`ruff`) and formatting (`black`) if implemented.
* UI should be cute and simple — pixel style is preferred.

---

## **Library Constraints**

* **Do NOT use the `jose` or `python-jose` library** for JWT handling. Use `PyJWT` instead (`pip install PyJWT`). Example:
  ```python
  import jwt
  token = jwt.encode({"user_id": 1}, "secret", algorithm="HS256")
  payload = jwt.decode(token, "secret", algorithms=["HS256"])
  ```
* For password hashing, use simple SHA256 with salt (hashlib) - avoids bcrypt compilation issues:
  ```python
  import hashlib, secrets
  salt = secrets.token_hex(16)
  hashed = hashlib.sha256(f"{password}{salt}".encode()).hexdigest()
  stored = f"{salt}:{hashed}"
  ```

---

## **Required Dependencies**

Create a `requirements.txt` in the workspace with:
```
fastapi>=0.100.0
uvicorn>=0.20.0
sqlalchemy>=2.0.0
PyJWT>=2.0.0
jinja2>=3.0.0
python-multipart>=0.0.5
httpx>=0.24.0
pytest>=7.0.0
pytest-asyncio>=0.20.0
```

**Note**: `python-multipart` is REQUIRED for FastAPI Form() to work.

---

## **Stretch Goals (if time remains)**

* Real-time updates (WebSockets).
* Multiple pets per user.
* Leaderboard for “happiest pets”.
* Sprite animations.

---

## **Completion Definition**

The project is complete when:

* A user can sign up, get a pet, interact with it, and see stats change. (Full game cycle via Frontend with backend integration)
* Routes exist for frontend and backend
* Tests pass (`pytest` return code 0).
* The application can be started with a single command, e.g.:

```bash
uvicorn app.main:app --reload
```

---
