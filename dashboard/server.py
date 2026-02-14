"""
Hotel Intel — Dashboard Server.

FastAPI backend with SQLite, session auth, and multi-property support.
"""

import json
import os
import sys
import secrets
from pathlib import Path
from datetime import datetime
from typing import Optional
from urllib.parse import urlencode

PROJECT_ROOT = Path(__file__).parent.parent
APP_DIR = PROJECT_ROOT / "app"
sys.path.insert(0, str(APP_DIR))
sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
load_dotenv(Path(__file__).parent / ".env")

import bcrypt
import httpx
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired

from fastapi import FastAPI, HTTPException, status, Request, Response, Depends
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
import uvicorn

import asyncio
from database import get_db, init_db, get_user_by_email, get_user_by_id, \
    get_all_properties, get_property, get_profiles, get_profile, \
    get_recap, get_recap_dates, get_settings, get_modules, \
    get_oauth_configs, get_oauth_config, upsert_oauth_config, \
    get_enabled_oauth_providers, get_all_enabled_oauth_configs, \
    get_app_configs, get_app_config, upsert_app_config, delete_app_config, \
    update_app_config_status
from app_catalog import get_catalog, get_catalog_by_category, get_app_by_id, APP_CATALOG

app = FastAPI(title="Hotel Intel Dashboard", version="2.0.0")

SECRET_KEY = "hotel-intel-secret-change-in-production-2024"
SESSION_MAX_AGE = 86400 * 7  # 7 days
serializer = URLSafeTimedSerializer(SECRET_KEY)

OAUTH_REDIRECT_BASE = os.environ.get("OAUTH_REDIRECT_BASE", "https://loki.hbtn.io")

# In-memory OAuth state store (state -> timestamp)
_oauth_states: dict[str, float] = {}

DOCS_DIR = PROJECT_ROOT / "docs"
DOC_TITLES = {
    "overview": "Overview",
    "architecture": "Architecture",
    "mvp": "MVP Roadmap",
    "daily-recap": "Daily Recap",
    "guest-intelligence": "Guest Intelligence",
    "integrations": "Integrations",
    "delivery": "Delivery Channels",
    "security": "Security",
    "hotel-intel-full": "Full Specification",
    "voice-assistant": "Voice Assistant",
}


# ── Auth Helpers ─────────────────────────────

def create_session_token(user_id: int) -> str:
    return serializer.dumps({"uid": user_id})


def get_current_user(request: Request) -> dict:
    token = request.cookies.get("session")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        data = serializer.loads(token, max_age=SESSION_MAX_AGE)
    except (BadSignature, SignatureExpired):
        raise HTTPException(status_code=401, detail="Session expired")
    conn = get_db()
    user = get_user_by_id(conn, data["uid"])
    conn.close()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user


def get_user_properties(user: dict) -> list:
    """Return list of property IDs the user can access."""
    conn = get_db()
    if user["role"] == "admin":
        props = get_all_properties(conn)
        conn.close()
        return [p["id"] for p in props]
    conn.close()
    return [user["property_id"]] if user["property_id"] else []


def require_property_access(user: dict, property_id: int):
    if user["role"] == "admin":
        return
    if user["property_id"] != property_id:
        raise HTTPException(status_code=403, detail="Access denied to this property")


# ── Auth Endpoints ───────────────────────────

@app.post("/api/login")
async def login(request: Request, response: Response):
    body = await request.json()
    email = body.get("email", "").strip().lower()
    password = body.get("password", "")
    if not email or not password:
        raise HTTPException(status_code=400, detail="Email and password required")

    conn = get_db()
    user = get_user_by_email(conn, email)
    conn.close()
    if not user or not bcrypt.checkpw(password.encode(), user["password_hash"].encode()):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_session_token(user["id"])
    resp = JSONResponse({"ok": True, "user": {"id": user["id"], "email": user["email"], "name": user["name"], "role": user["role"]}})
    resp.set_cookie("session", token, max_age=SESSION_MAX_AGE, httponly=True, samesite="lax", path="/")
    return resp


@app.post("/api/logout")
async def logout():
    resp = JSONResponse({"ok": True})
    resp.delete_cookie("session", path="/")
    return resp


# ── OAuth Endpoints ───────────────────────────

def _get_oauth_client_config(provider: str):
    """Get OAuth client_id/secret — first from any enabled property config, then env fallback."""
    conn = get_db()
    configs = get_all_enabled_oauth_configs(conn, provider)
    conn.close()
    if configs:
        c = configs[0]
        return {
            "client_id": c["client_id"],
            "client_secret": c["client_secret"],
            "tenant_id": c.get("tenant_id"),
            "allowed_domains": [cfg["allowed_domain"] for cfg in configs if cfg.get("allowed_domain")],
        }
    # Env fallback
    if provider == "google":
        cid = os.environ.get("GOOGLE_CLIENT_ID")
        csec = os.environ.get("GOOGLE_CLIENT_SECRET")
        if cid and csec:
            return {"client_id": cid, "client_secret": csec, "tenant_id": None, "allowed_domains": []}
    elif provider == "microsoft":
        cid = os.environ.get("MICROSOFT_CLIENT_ID")
        csec = os.environ.get("MICROSOFT_CLIENT_SECRET")
        tid = os.environ.get("MICROSOFT_TENANT_ID", "common")
        if cid and csec:
            return {"client_id": cid, "client_secret": csec, "tenant_id": tid, "allowed_domains": []}
    return None


@app.get("/api/auth/providers")
async def get_auth_providers():
    """Return which OAuth providers are available (for login page)."""
    conn = get_db()
    enabled = get_enabled_oauth_providers(conn)
    conn.close()
    # Also check env fallbacks
    if os.environ.get("GOOGLE_CLIENT_ID"):
        enabled.add("google")
    if os.environ.get("MICROSOFT_CLIENT_ID"):
        enabled.add("microsoft")
    return {"providers": list(enabled)}


@app.get("/api/auth/google")
async def auth_google():
    cfg = _get_oauth_client_config("google")
    if not cfg:
        raise HTTPException(400, "Google OAuth not configured")
    state = secrets.token_urlsafe(32)
    _oauth_states[state] = datetime.now().timestamp()
    params = {
        "client_id": cfg["client_id"],
        "redirect_uri": f"{OAUTH_REDIRECT_BASE}/api/auth/google/callback",
        "response_type": "code",
        "scope": "openid email profile",
        "state": state,
        "access_type": "offline",
        "prompt": "select_account",
    }
    return RedirectResponse(f"https://accounts.google.com/o/oauth2/v2/auth?{urlencode(params)}")


@app.get("/api/auth/google/callback")
async def auth_google_callback(code: str = "", state: str = "", error: str = ""):
    if error:
        return _oauth_error_page(f"Google login cancelled: {error}")
    if state not in _oauth_states:
        return _oauth_error_page("Invalid OAuth state — please try again")
    del _oauth_states[state]

    cfg = _get_oauth_client_config("google")
    if not cfg:
        return _oauth_error_page("Google OAuth not configured")

    # Exchange code for tokens
    async with httpx.AsyncClient() as client:
        token_res = await client.post("https://oauth2.googleapis.com/token", data={
            "code": code,
            "client_id": cfg["client_id"],
            "client_secret": cfg["client_secret"],
            "redirect_uri": f"{OAUTH_REDIRECT_BASE}/api/auth/google/callback",
            "grant_type": "authorization_code",
        })
    if token_res.status_code != 200:
        return _oauth_error_page("Failed to exchange Google auth code")
    tokens = token_res.json()

    # Get user info
    async with httpx.AsyncClient() as client:
        info_res = await client.get("https://www.googleapis.com/oauth2/v2/userinfo",
                                     headers={"Authorization": f"Bearer {tokens['access_token']}"})
    if info_res.status_code != 200:
        return _oauth_error_page("Failed to get Google user info")
    info = info_res.json()
    email = info.get("email", "").lower()

    return _oauth_login_by_email(email, "google", cfg.get("allowed_domains", []))


@app.get("/api/auth/microsoft")
async def auth_microsoft():
    cfg = _get_oauth_client_config("microsoft")
    if not cfg:
        raise HTTPException(400, "Microsoft OAuth not configured")
    state = secrets.token_urlsafe(32)
    _oauth_states[state] = datetime.now().timestamp()
    tenant = cfg.get("tenant_id") or "common"
    params = {
        "client_id": cfg["client_id"],
        "redirect_uri": f"{OAUTH_REDIRECT_BASE}/api/auth/microsoft/callback",
        "response_type": "code",
        "scope": "openid email profile User.Read",
        "state": state,
        "response_mode": "query",
    }
    return RedirectResponse(f"https://login.microsoftonline.com/{tenant}/oauth2/v2.0/authorize?{urlencode(params)}")


@app.get("/api/auth/microsoft/callback")
async def auth_microsoft_callback(code: str = "", state: str = "", error: str = ""):
    if error:
        return _oauth_error_page(f"Microsoft login cancelled: {error}")
    if state not in _oauth_states:
        return _oauth_error_page("Invalid OAuth state — please try again")
    del _oauth_states[state]

    cfg = _get_oauth_client_config("microsoft")
    if not cfg:
        return _oauth_error_page("Microsoft OAuth not configured")
    tenant = cfg.get("tenant_id") or "common"

    async with httpx.AsyncClient() as client:
        token_res = await client.post(
            f"https://login.microsoftonline.com/{tenant}/oauth2/v2.0/token",
            data={
                "code": code,
                "client_id": cfg["client_id"],
                "client_secret": cfg["client_secret"],
                "redirect_uri": f"{OAUTH_REDIRECT_BASE}/api/auth/microsoft/callback",
                "grant_type": "authorization_code",
                "scope": "openid email profile User.Read",
            }
        )
    if token_res.status_code != 200:
        return _oauth_error_page("Failed to exchange Microsoft auth code")
    tokens = token_res.json()

    async with httpx.AsyncClient() as client:
        info_res = await client.get("https://graph.microsoft.com/v1.0/me",
                                     headers={"Authorization": f"Bearer {tokens['access_token']}"})
    if info_res.status_code != 200:
        return _oauth_error_page("Failed to get Microsoft user info")
    info = info_res.json()
    email = (info.get("mail") or info.get("userPrincipalName") or "").lower()

    return _oauth_login_by_email(email, "microsoft", cfg.get("allowed_domains", []))


def _oauth_login_by_email(email: str, provider: str, allowed_domains: list):
    if not email:
        return _oauth_error_page("No email returned from provider")

    # Check domain restrictions
    domain = email.split("@")[-1]
    if allowed_domains and domain not in allowed_domains:
        return _oauth_error_page(f"Email domain '{domain}' is not allowed for {provider} login")

    conn = get_db()
    user = get_user_by_email(conn, email)
    if not user:
        conn.close()
        return _oauth_error_page(f"No account found for {email}")

    # Optionally update oauth_provider on user
    if not user.get("oauth_provider"):
        conn.execute("UPDATE users SET oauth_provider=? WHERE id=?", (provider, user["id"]))
        conn.commit()
    conn.close()

    token = create_session_token(user["id"])
    resp = RedirectResponse("/", status_code=302)
    resp.set_cookie("session", token, max_age=SESSION_MAX_AGE, httponly=True, samesite="lax", path="/")
    return resp


def _oauth_error_page(message: str):
    html = f"""<!DOCTYPE html><html><head><meta charset="UTF-8">
    <title>Login Error</title>
    <script src="https://cdn.tailwindcss.com"></script>
    </head><body class="bg-[#0d1530] min-h-screen flex items-center justify-center">
    <div class="bg-[#152045] rounded-2xl border border-[#1e2a5e] p-8 max-w-md text-center">
    <h2 class="text-xl font-bold text-[#c9a96e] mb-4">Login Error</h2>
    <p class="text-[#bbc3df] mb-6">{message}</p>
    <a href="/login" class="inline-block bg-[#c9a96e] hover:bg-[#b08a42] text-white font-semibold px-6 py-2.5 rounded-lg transition">
    Back to Login</a></div></body></html>"""
    return HTMLResponse(html)


# ── OAuth Config Management ──────────────────

@app.get("/api/properties/{property_id}/oauth-configs")
async def get_property_oauth_configs(property_id: int, request: Request):
    user = get_current_user(request)
    require_property_access(user, property_id)
    if user["role"] == "staff":
        raise HTTPException(403, "Staff cannot access OAuth settings")
    conn = get_db()
    configs = get_oauth_configs(conn, property_id)
    conn.close()
    # Mask secrets
    for c in configs:
        if c.get("client_secret"):
            c["client_secret"] = "••••••••" + c["client_secret"][-4:] if len(c["client_secret"]) > 4 else "••••••••"
    return {"configs": configs}


@app.post("/api/properties/{property_id}/oauth-configs")
async def save_property_oauth_config(property_id: int, request: Request):
    user = get_current_user(request)
    require_property_access(user, property_id)
    if user["role"] not in ("admin", "manager"):
        raise HTTPException(403, "Insufficient permissions")
    body = await request.json()
    provider = body.get("provider")
    if provider not in ("google", "microsoft"):
        raise HTTPException(400, "Invalid provider")

    conn = get_db()
    # If secret is masked, keep existing
    existing = get_oauth_config(conn, property_id, provider)
    client_secret = body.get("client_secret", "")
    if client_secret.startswith("••••") and existing:
        client_secret = existing["client_secret"]

    upsert_oauth_config(
        conn, property_id, provider,
        body.get("client_id", ""),
        client_secret,
        body.get("tenant_id"),
        body.get("allowed_domain"),
        body.get("enabled", False),
    )
    conn.close()
    return {"ok": True}


@app.get("/api/me")
async def me(request: Request):
    user = get_current_user(request)
    conn = get_db()
    props = []
    if user["role"] == "admin":
        props = get_all_properties(conn)
    elif user["property_id"]:
        p = get_property(conn, user["property_id"])
        if p:
            props = [p]
    conn.close()
    return {
        "id": user["id"],
        "email": user["email"],
        "name": user["name"],
        "role": user["role"],
        "property_id": user["property_id"],
        "properties": props,
    }


# ── Properties ───────────────────────────────

@app.get("/api/properties")
async def list_properties(request: Request):
    user = get_current_user(request)
    conn = get_db()
    if user["role"] == "admin":
        props = get_all_properties(conn)
    elif user["property_id"]:
        p = get_property(conn, user["property_id"])
        props = [p] if p else []
    else:
        props = []
    conn.close()
    return {"properties": props}


# ── Recap ────────────────────────────────────

@app.get("/api/properties/{property_id}/dates")
async def get_dates(property_id: int, request: Request):
    user = get_current_user(request)
    require_property_access(user, property_id)
    conn = get_db()
    dates = get_recap_dates(conn, property_id)
    conn.close()
    return {"dates": dates, "latest": dates[-1] if dates else None}


@app.get("/api/properties/{property_id}/recap/{date}")
async def get_recap_endpoint(property_id: int, date: str, request: Request):
    user = get_current_user(request)
    require_property_access(user, property_id)
    conn = get_db()
    recap = get_recap(conn, property_id, date)
    conn.close()
    if not recap:
        return JSONResponse({"error": "Date not found"}, status_code=404)
    return recap


# ── Guests ───────────────────────────────────

@app.get("/api/properties/{property_id}/guests")
async def get_guests(property_id: int, request: Request):
    user = get_current_user(request)
    require_property_access(user, property_id)
    conn = get_db()
    profiles = get_profiles(conn, property_id)
    conn.close()
    return {"profiles": profiles}


@app.get("/api/properties/{property_id}/guests/{guest_id}")
async def get_guest(property_id: int, guest_id: str, request: Request):
    user = get_current_user(request)
    require_property_access(user, property_id)
    conn = get_db()
    profile = get_profile(conn, property_id, guest_id)
    conn.close()
    if not profile:
        return JSONResponse({"error": "Guest not found"}, status_code=404)
    return profile


# ── Settings & Modules ───────────────────────

@app.get("/api/properties/{property_id}/settings")
async def get_settings_endpoint(property_id: int, request: Request):
    user = get_current_user(request)
    require_property_access(user, property_id)
    if user["role"] == "staff":
        raise HTTPException(status_code=403, detail="Staff cannot access settings")
    conn = get_db()
    settings = get_settings(conn, property_id) or {}
    modules = get_modules(conn, property_id)
    conn.close()
    settings["modules"] = modules
    return settings


# ── Documentation ────────────────────────────

@app.get("/api/docs")
async def get_docs_list(request: Request):
    get_current_user(request)
    docs = []
    for stem, title in DOC_TITLES.items():
        path = DOCS_DIR / f"{stem}.md"
        if path.exists():
            docs.append({"id": stem, "title": title, "size": path.stat().st_size})
    return docs


@app.get("/api/docs/{doc_id}")
async def get_doc(doc_id: str, request: Request):
    get_current_user(request)
    path = DOCS_DIR / f"{doc_id}.md"
    if not path.exists():
        return JSONResponse({"error": "Document not found"}, status_code=404)
    return JSONResponse({"id": doc_id, "title": DOC_TITLES.get(doc_id, doc_id), "content": path.read_text(encoding="utf-8")})


# ── App Catalog Endpoints ─────────────────────

@app.get("/api/app-catalog")
async def get_app_catalog(request: Request):
    get_current_user(request)
    return get_catalog()


@app.get("/api/app-catalog/{category}")
async def get_app_catalog_by_category(category: str, request: Request):
    get_current_user(request)
    apps = get_catalog_by_category(category)
    return {"apps": apps}


@app.get("/api/properties/{property_id}/apps")
async def get_property_apps(property_id: int, request: Request):
    user = get_current_user(request)
    require_property_access(user, property_id)
    conn = get_db()
    configs = get_app_configs(conn, property_id)
    conn.close()
    # Mask secrets
    for c in configs:
        if isinstance(c.get("config"), dict):
            for app in APP_CATALOG:
                if app["id"] == c["app_id"]:
                    for field in app["config_schema"]["fields"]:
                        if field["type"] == "password" and field["key"] in c["config"]:
                            val = c["config"][field["key"]]
                            if val and len(str(val)) > 4:
                                c["config"][field["key"]] = "••••••••" + str(val)[-4:]
                            elif val:
                                c["config"][field["key"]] = "••••••••"
                    break
    return {"apps": configs}


@app.post("/api/properties/{property_id}/apps/{app_id}")
async def save_property_app(property_id: int, app_id: str, request: Request):
    user = get_current_user(request)
    require_property_access(user, property_id)
    if user["role"] not in ("admin", "manager"):
        raise HTTPException(403, "Insufficient permissions")
    catalog_app = get_app_by_id(app_id)
    if not catalog_app:
        raise HTTPException(404, f"App '{app_id}' not found in catalog")
    body = await request.json()
    config = body.get("config", {})
    enabled = body.get("enabled", False)
    status = body.get("status", "disconnected")

    # If secrets are masked, keep existing values
    conn = get_db()
    existing = get_app_config(conn, property_id, app_id)
    if existing and isinstance(config, dict):
        for field in catalog_app["config_schema"]["fields"]:
            if field["type"] == "password" and field["key"] in config:
                val = config[field["key"]]
                if isinstance(val, str) and val.startswith("••••"):
                    config[field["key"]] = existing["config"].get(field["key"], "")

    upsert_app_config(conn, property_id, app_id, config, enabled, status)
    conn.close()
    return {"ok": True}


@app.delete("/api/properties/{property_id}/apps/{app_id}")
async def remove_property_app(property_id: int, app_id: str, request: Request):
    user = get_current_user(request)
    require_property_access(user, property_id)
    if user["role"] not in ("admin", "manager"):
        raise HTTPException(403, "Insufficient permissions")
    conn = get_db()
    delete_app_config(conn, property_id, app_id)
    conn.close()
    return {"ok": True}


@app.post("/api/properties/{property_id}/apps/{app_id}/test")
async def test_property_app(property_id: int, app_id: str, request: Request):
    user = get_current_user(request)
    require_property_access(user, property_id)
    catalog_app = get_app_by_id(app_id)
    if not catalog_app:
        raise HTTPException(404, f"App '{app_id}' not found in catalog")
    # Mock test: wait 1s then return success
    await asyncio.sleep(1)
    conn = get_db()
    update_app_config_status(conn, property_id, app_id, "connected",
                             last_sync=datetime.now().isoformat())
    conn.close()
    return {"ok": True, "status": "connected", "message": f"Successfully connected to {catalog_app['name']}"}


# ── Legacy endpoints (redirect to property-scoped) ──

@app.get("/api/dates")
async def legacy_dates(request: Request):
    user = get_current_user(request)
    prop_ids = get_user_properties(user)
    if not prop_ids:
        return {"dates": [], "latest": None}
    conn = get_db()
    dates = get_recap_dates(conn, prop_ids[0])
    conn.close()
    return {"dates": dates, "latest": dates[-1] if dates else None}


@app.get("/api/recap/{date}")
async def legacy_recap(date: str, request: Request):
    user = get_current_user(request)
    prop_ids = get_user_properties(user)
    if not prop_ids:
        return JSONResponse({"error": "No property"}, status_code=404)
    conn = get_db()
    recap = get_recap(conn, prop_ids[0], date)
    conn.close()
    if not recap:
        return JSONResponse({"error": "Date not found"}, status_code=404)
    return recap


@app.get("/api/guests")
async def legacy_guests(request: Request):
    user = get_current_user(request)
    prop_ids = get_user_properties(user)
    if not prop_ids:
        return {"profiles": []}
    conn = get_db()
    profiles = get_profiles(conn, prop_ids[0])
    conn.close()
    return {"profiles": profiles}


@app.get("/api/settings")
async def legacy_settings(request: Request):
    user = get_current_user(request)
    prop_ids = get_user_properties(user)
    if not prop_ids:
        return {}
    conn = get_db()
    settings = get_settings(conn, prop_ids[0]) or {}
    modules = get_modules(conn, prop_ids[0])
    conn.close()
    settings["modules"] = modules
    return settings


# ── Voice Assistant ───────────────────────────

@app.post("/api/voice/session")
async def create_voice_session(request: Request):
    """Create an ephemeral OpenAI Realtime session token."""
    user = get_current_user(request)
    body = await request.json() if request.headers.get("content-type") == "application/json" else {}
    context = body.get("context", "")
    
    api_key = os.environ.get("OPENAI_API_KEY", "")
    if not api_key:
        raise HTTPException(status_code=500, detail="OpenAI API key not configured")
    
    instructions = f"""You are the voice assistant for Hotel Intel, an AI-powered intelligence platform for luxury hotels.

You have access to today's daily briefing data. Use it to answer questions accurately. Be concise, professional, and warm — like a knowledgeable hotel operations manager giving a briefing.

If asked about something not in the briefing context, say so honestly and suggest where the information might be found (e.g., Opera PMS, the spa system, etc.).

Keep answers short and conversational — this is voice, not a report.

Here is today's briefing data:
{context}"""

    async with httpx.AsyncClient() as client:
        lang = body.get("lang", "en")
        resp = await client.post(
            "https://api.openai.com/v1/realtime/sessions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": "gpt-4o-realtime-preview-2025-06-03",
                "voice": body.get("voice", "ash"),
                "instructions": instructions,
                "input_audio_transcription": {"model": "gpt-4o-mini-transcribe", "language": lang},
            },
        )
    
    if resp.status_code != 200:
        raise HTTPException(status_code=resp.status_code, detail=f"OpenAI error: {resp.text}")
    
    return resp.json()


@app.post("/api/voice/tts")
async def voice_tts(request: Request):
    """Stream speech from text using OpenAI TTS."""
    user = get_current_user(request)
    body = await request.json()
    text = body.get("text", "")
    if not text:
        raise HTTPException(status_code=400, detail="No text provided")

    api_key = os.environ.get("OPENAI_API_KEY", "")
    if not api_key:
        raise HTTPException(status_code=500, detail="OpenAI API key not configured")

    from starlette.responses import StreamingResponse

    lang = body.get("lang", "en")
    tts_text = text

    # Translate if not English
    if lang and lang != "en":
        lang_names = {"fr":"French","es":"Spanish","de":"German","it":"Italian","pt":"Portuguese","zh":"Chinese","ja":"Japanese","ar":"Arabic"}
        target_lang = lang_names.get(lang, lang)
        async with httpx.AsyncClient() as client:
            tr_resp = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                json={
                    "model": "gpt-4o-mini",
                    "messages": [
                        {"role": "system", "content": f"Translate the following text to {target_lang}. Keep it natural and professional. Localize all number formats (e.g. use spaces as thousand separators for French: '1 200' not '1,200', currency after the number: '1 200 €' not '€1,200', percentages with comma decimals where appropriate). The output must read perfectly when spoken aloud by a TTS engine in {target_lang}. Only output the translation, nothing else."},
                        {"role": "user", "content": text[:4096]},
                    ],
                },
                timeout=30,
            )
        if tr_resp.status_code == 200:
            tts_text = tr_resp.json()["choices"][0]["message"]["content"]

    async def generate():
        async with httpx.AsyncClient() as client:
            async with client.stream(
                "POST",
                "https://api.openai.com/v1/audio/speech",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": "tts-1",
                    "input": tts_text[:4096],
                    "voice": body.get("voice", "ash"),
                    "response_format": "mp3",
                },
                timeout=60,
            ) as resp:
                if resp.status_code != 200:
                    return
                async for chunk in resp.aiter_bytes(1024):
                    yield chunk

    return StreamingResponse(generate(), media_type="audio/mpeg")


@app.post("/api/voice/studio")
async def voice_studio(request: Request):
    """Studio mode: Whisper STT → LLM → TTS. Accepts audio, returns audio + transcript."""
    user = get_current_user(request)
    api_key = os.environ.get("OPENAI_API_KEY", "")
    if not api_key:
        raise HTTPException(status_code=500, detail="OpenAI API key not configured")

    form = await request.form()
    audio_file = form.get("audio")
    context = form.get("context", "")
    history_json = form.get("history", "[]")
    lang = form.get("lang", "en")
    voice = form.get("voice", "ash")

    if not audio_file:
        raise HTTPException(status_code=400, detail="No audio provided")

    audio_bytes = await audio_file.read()

    lang_map = {"en":"en","fr":"fr","es":"es","de":"de","it":"it","pt":"pt","zh":"zh","ja":"ja","ar":"ar"}
    whisper_lang = lang_map.get(lang, "en")

    # 1. Whisper STT
    import io
    async with httpx.AsyncClient() as client:
        stt_resp = await client.post(
            "https://api.openai.com/v1/audio/transcriptions",
            headers={"Authorization": f"Bearer {api_key}"},
            files={"file": ("audio.webm", io.BytesIO(audio_bytes), "audio/webm")},
            data={"model": "gpt-4o-mini-transcribe", "language": whisper_lang},
            timeout=30,
        )
    if stt_resp.status_code != 200:
        raise HTTPException(status_code=500, detail=f"Whisper error: {stt_resp.text[:200]}")

    user_text = stt_resp.json().get("text", "").strip()
    if not user_text:
        return JSONResponse({"user_text": "", "assistant_text": "", "audio": None})

    # 2. LLM
    lang_names = {"en":"English","fr":"French","es":"Spanish","de":"German","it":"Italian","pt":"Portuguese","zh":"Chinese","ja":"Japanese","ar":"Arabic"}
    target_lang = lang_names.get(lang, "English")

    history = json.loads(history_json) if history_json else []
    messages = [
        {"role": "system", "content": f"""You are the voice assistant for Hotel Intel, an AI-powered intelligence platform for luxury hotels.

You have access to today's daily briefing data. Use it to answer questions accurately. Be concise, professional, and warm — like a knowledgeable hotel operations manager.

Respond in {target_lang}. Keep answers short and conversational — this is voice, not a report. Localize number formats for {target_lang}.

If asked about something not in the briefing context, say so honestly and suggest where the information might be found.

Here is today's briefing data:
{context}"""},
    ]
    for msg in history[-10:]:
        messages.append({"role": msg.get("role", "user"), "content": msg.get("text", "")})
    messages.append({"role": "user", "content": user_text})

    async with httpx.AsyncClient() as client:
        llm_resp = await client.post(
            "https://api.openai.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json={"model": "gpt-4o-mini", "messages": messages, "max_tokens": 500},
            timeout=30,
        )
    if llm_resp.status_code != 200:
        raise HTTPException(status_code=500, detail=f"LLM error: {llm_resp.text[:200]}")

    assistant_text = llm_resp.json()["choices"][0]["message"]["content"].strip()

    # 3. TTS
    async with httpx.AsyncClient() as client:
        tts_resp = await client.post(
            "https://api.openai.com/v1/audio/speech",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json={"model": "tts-1", "input": assistant_text[:4096], "voice": voice, "response_format": "mp3"},
            timeout=60,
        )
    if tts_resp.status_code != 200:
        raise HTTPException(status_code=500, detail=f"TTS error: {tts_resp.text[:200]}")

    import base64
    audio_b64 = base64.b64encode(tts_resp.content).decode()

    return JSONResponse({
        "user_text": user_text,
        "assistant_text": assistant_text,
        "audio": audio_b64,
    })


# ── Local Voice (Studio Local) ────────────────

# Pre-load Piper voices at startup for speed
_piper_voices = {}

def _get_piper_voice(lang: str):
    if lang not in _piper_voices:
        from piper.voice import PiperVoice
        models_dir = PROJECT_ROOT / "models"
        model_map = {
            "en": models_dir / "piper-en.onnx",
            "fr": models_dir / "piper-fr.onnx",
        }
        model_path = model_map.get(lang, model_map["en"])
        if model_path.exists():
            _piper_voices[lang] = PiperVoice.load(str(model_path))
        else:
            _piper_voices[lang] = _piper_voices.get("en") or PiperVoice.load(str(model_map["en"]))
    return _piper_voices[lang]


def _piper_synthesize(text: str, lang: str = "en") -> bytes:
    """Synthesize text to WAV bytes using Piper."""
    voice = _get_piper_voice(lang)
    import struct
    parts = []
    sr = 22050
    for chunk in voice.synthesize(text):
        parts.append(chunk.audio_int16_bytes)
        sr = chunk.sample_rate
    raw = b''.join(parts)
    # Build WAV
    header = b'RIFF' + struct.pack('<I', 36 + len(raw)) + b'WAVEfmt '
    header += struct.pack('<IHHIIHH', 16, 1, 1, sr, sr * 2, 2, 16)
    header += b'data' + struct.pack('<I', len(raw))
    return header + raw


def _whisper_transcribe(audio_bytes: bytes, lang: str = "en") -> str:
    """Transcribe audio using local whisper-cli."""
    import subprocess, tempfile
    # Write input webm
    with tempfile.NamedTemporaryFile(suffix='.webm', delete=False) as f:
        f.write(audio_bytes)
        webm_path = f.name
    wav_path = webm_path.replace('.webm', '.wav')
    try:
        # Convert to 16kHz mono WAV
        subprocess.run(
            ['ffmpeg', '-i', webm_path, '-ar', '16000', '-ac', '1', wav_path, '-y'],
            capture_output=True, timeout=10
        )
        # Run whisper
        model_path = str(PROJECT_ROOT / "models" / "whisper-base.bin")
        result = subprocess.run(
            ['whisper-cli', '-m', model_path, '-f', wav_path, '--no-timestamps', '-np', '-l', lang],
            capture_output=True, text=True, timeout=30
        )
        return result.stdout.strip()
    finally:
        import os
        for p in [webm_path, wav_path]:
            try: os.unlink(p)
            except: pass


@app.post("/api/voice/local")
async def voice_local(request: Request):
    """Local mode: whisper-cli STT → Ollama LLM → Piper TTS."""
    user = get_current_user(request)
    form = await request.form()
    audio_file = form.get("audio")
    context = form.get("context", "")
    history_json = form.get("history", "[]")
    lang = form.get("lang", "en")

    if not audio_file:
        raise HTTPException(status_code=400, detail="No audio provided")

    audio_bytes = await audio_file.read()

    # 1. Local STT
    import asyncio
    user_text = await asyncio.to_thread(_whisper_transcribe, audio_bytes, lang)
    if not user_text:
        return JSONResponse({"user_text": "", "assistant_text": "", "audio": None})

    # 2. Ollama LLM
    lang_names = {"en":"English","fr":"French","es":"Spanish","de":"German","it":"Italian","pt":"Portuguese","zh":"Chinese","ja":"Japanese","ar":"Arabic"}
    target_lang = lang_names.get(lang, "English")

    history = json.loads(history_json) if history_json else []
    messages = [
        {"role": "system", "content": f"""You are the voice assistant for Hotel Intel. Answer questions about the daily briefing data below. Be concise and conversational. Respond in {target_lang}. Localize number formats.

Briefing data:
{context}"""},
    ]
    for msg in history[-10:]:
        messages.append({"role": msg.get("role", "user"), "content": msg.get("text", "")})
    messages.append({"role": "user", "content": user_text})

    async with httpx.AsyncClient() as client:
        llm_resp = await client.post(
            "http://localhost:11434/api/chat",
            json={"model": "llama3.2", "messages": messages, "stream": False},
            timeout=30,
        )
    if llm_resp.status_code != 200:
        raise HTTPException(status_code=500, detail=f"Ollama error: {llm_resp.text[:200]}")

    assistant_text = llm_resp.json().get("message", {}).get("content", "").strip()

    # 3. Local TTS
    wav_bytes = await asyncio.to_thread(_piper_synthesize, assistant_text, lang)

    import base64
    audio_b64 = base64.b64encode(wav_bytes).decode()

    return JSONResponse({
        "user_text": user_text,
        "assistant_text": assistant_text,
        "audio": audio_b64,
    })


# ── Serve Frontend ───────────────────────────

@app.get("/", response_class=HTMLResponse)
async def serve_dashboard():
    html_path = Path(__file__).parent / "index.html"
    return html_path.read_text(encoding="utf-8")


@app.get("/login", response_class=HTMLResponse)
async def serve_login():
    html_path = Path(__file__).parent / "index.html"
    return html_path.read_text(encoding="utf-8")


# ── Serve Flutter Web App ────────────────────
APP_WEB_DIR = Path(__file__).parent / "app-web"
if APP_WEB_DIR.exists():
    app.mount("/app", StaticFiles(directory=str(APP_WEB_DIR), html=True), name="flutter-app")


if __name__ == "__main__":
    init_db()
    uvicorn.run(app, host="0.0.0.0", port=8000)
