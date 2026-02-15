"""
Hotel Intel — App Catalog.

Comprehensive catalog of hotel software integrations with JSON configuration schemas.
"""

APP_CATEGORIES = {
    "pms": {"name": "Property Management", "icon": "🏨", "order": 1},
    "spa": {"name": "Spa & Wellness", "icon": "💆", "order": 2},
    "fb": {"name": "Food & Beverage", "icon": "🍽️", "order": 3},
    "incidents": {"name": "Incidents & Operations", "icon": "⚠️", "order": 4},
    "concierge": {"name": "Concierge", "icon": "🛎️", "order": 5},
    "villas": {"name": "Villas & Rentals", "icon": "🏡", "order": 6},
    "finance": {"name": "Finance & Accounting", "icon": "💰", "order": 7},
    "payments": {"name": "Payments", "icon": "💳", "order": 8},
    "communications": {"name": "Communications", "icon": "📧", "order": 9},
    "hr": {"name": "HR & Scheduling", "icon": "👥", "order": 10},
}

APP_CATALOG = [
    # ── PMS ───────────────────────────────────
    {
        "id": "opera-pms",
        "name": "Oracle OPERA PMS",
        "category": "pms",
        "description": "Oracle Hospitality OPERA Property Management System — the industry standard for luxury hotel operations. Connects via OHIP (Oracle Hospitality Integration Platform) APIs.",
        "icon": "🏨",
        "website": "https://www.oracle.com/hospitality/hotel-property-management/",
        "config_schema": {
            "fields": [
                {"key": "ohip_endpoint", "label": "OHIP API Endpoint", "type": "url", "required": True, "placeholder": "https://your-hotel.opera-cloud.com/ohip/v1", "description": "Oracle Hospitality Integration Platform base URL"},
                {"key": "client_id", "label": "Client ID", "type": "text", "required": True, "placeholder": "app-xxxxxxxx", "description": "OAuth2 client identifier from Oracle"},
                {"key": "client_secret", "label": "Client Secret", "type": "password", "required": True, "placeholder": "", "description": "OAuth2 client secret"},
                {"key": "hotel_id", "label": "Hotel ID", "type": "text", "required": True, "placeholder": "EDENROCK", "description": "OPERA hotel/property code"},
                {"key": "environment", "label": "Environment", "type": "select", "required": True, "options": [{"value": "staging", "label": "Staging"}, {"value": "production", "label": "Production"}], "description": "Target OPERA environment"},
                {"key": "sync_reservations", "label": "Sync Reservations", "type": "toggle", "required": False, "description": "Pull reservation data (arrivals, departures, in-house)"},
                {"key": "sync_profiles", "label": "Sync Guest Profiles", "type": "toggle", "required": False, "description": "Pull guest profile data and preferences"},
                {"key": "sync_cashiering", "label": "Sync Cashiering", "type": "toggle", "required": False, "description": "Pull folio and billing data"},
                {"key": "sync_housekeeping", "label": "Sync Housekeeping", "type": "toggle", "required": False, "description": "Pull room status and housekeeping data"},
            ]
        }
    },
    {
        "id": "mews",
        "name": "Mews",
        "category": "pms",
        "description": "Cloud-native property management system for modern hospitality. API-first approach with real-time data sync.",
        "icon": "🟢",
        "website": "https://www.mews.com/",
        "config_schema": {
            "fields": [
                {"key": "platform_url", "label": "Platform URL", "type": "url", "required": True, "placeholder": "https://api.mews.com", "description": "Mews API base URL"},
                {"key": "client_name", "label": "Client Name", "type": "text", "required": True, "placeholder": "HotelIntel", "description": "Integration client name registered with Mews"},
                {"key": "access_token", "label": "Access Token", "type": "password", "required": True, "placeholder": "", "description": "Mews API access token"},
                {"key": "client_token", "label": "Client Token", "type": "password", "required": True, "placeholder": "", "description": "Mews API client token"},
            ]
        }
    },
    {
        "id": "protel",
        "name": "Protel PMS",
        "category": "pms",
        "description": "Protel hotel management software by Planet. On-premise and cloud PMS with comprehensive API.",
        "icon": "🔵",
        "website": "https://www.protel.net/",
        "config_schema": {
            "fields": [
                {"key": "api_endpoint", "label": "API Endpoint", "type": "url", "required": True, "placeholder": "https://protel.your-hotel.com/api", "description": "Protel API base URL"},
                {"key": "username", "label": "Username", "type": "text", "required": True, "placeholder": "", "description": "Protel API username"},
                {"key": "password", "label": "Password", "type": "password", "required": True, "placeholder": "", "description": "Protel API password"},
                {"key": "hotel_code", "label": "Hotel Code", "type": "text", "required": True, "placeholder": "HTL001", "description": "Protel property code"},
            ]
        }
    },

    # ── Spa ───────────────────────────────────
    {
        "id": "tac-spa",
        "name": "TAC (The Assistant Company)",
        "category": "spa",
        "description": "Leading spa management platform for luxury hotels. Handles bookings, treatments, therapist scheduling, and revenue tracking.",
        "icon": "💆",
        "website": "https://www.theassistantcompany.com/",
        "config_schema": {
            "fields": [
                {"key": "api_endpoint", "label": "API Endpoint", "type": "url", "required": True, "placeholder": "https://api.tac-app.com/v2", "description": "TAC API base URL"},
                {"key": "api_key", "label": "API Key", "type": "password", "required": True, "placeholder": "", "description": "TAC API authentication key"},
                {"key": "location_id", "label": "Location ID", "type": "text", "required": True, "placeholder": "LOC-001", "description": "TAC location/property identifier"},
                {"key": "sync_treatments", "label": "Sync Treatments", "type": "toggle", "required": False, "description": "Pull treatment bookings and revenue data"},
                {"key": "sync_therapists", "label": "Sync Therapists", "type": "toggle", "required": False, "description": "Pull therapist schedules and utilization"},
            ]
        }
    },
    {
        "id": "book4time",
        "name": "Book4Time",
        "category": "spa",
        "description": "Cloud-based spa and wellness management software used by top resorts and hotel spas worldwide.",
        "icon": "🕐",
        "website": "https://www.book4time.com/",
        "config_schema": {
            "fields": [
                {"key": "api_endpoint", "label": "API Endpoint", "type": "url", "required": True, "placeholder": "https://api.book4time.com/v1", "description": "Book4Time API base URL"},
                {"key": "api_key", "label": "API Key", "type": "password", "required": True, "placeholder": "", "description": "Book4Time API key"},
                {"key": "site_id", "label": "Site ID", "type": "text", "required": True, "placeholder": "SITE-001", "description": "Book4Time site identifier"},
            ]
        }
    },
    {
        "id": "spasoft",
        "name": "SpaSoft",
        "category": "spa",
        "description": "Amadeus SpaSoft — enterprise spa management with deep OPERA integration. Database-level connectivity.",
        "icon": "🧖",
        "website": "https://www.amadeus-hospitality.com/",
        "config_schema": {
            "fields": [
                {"key": "hostname", "label": "Hostname", "type": "text", "required": True, "placeholder": "spasoft.your-hotel.com", "description": "SpaSoft database server hostname"},
                {"key": "port", "label": "Port", "type": "number", "required": True, "placeholder": "1433", "description": "Database port number"},
                {"key": "database", "label": "Database Name", "type": "text", "required": True, "placeholder": "SpaSoft_DB", "description": "SpaSoft database name"},
                {"key": "username", "label": "Username", "type": "text", "required": True, "placeholder": "", "description": "Database username"},
                {"key": "password", "label": "Password", "type": "password", "required": True, "placeholder": "", "description": "Database password"},
            ]
        }
    },

    # ── F&B ───────────────────────────────────
    {
        "id": "sevenrooms",
        "name": "SevenRooms",
        "category": "fb",
        "description": "Guest experience and retention platform for restaurants and bars. Reservation management, guest profiles, and marketing automation.",
        "icon": "🍽️",
        "website": "https://sevenrooms.com/",
        "config_schema": {
            "fields": [
                {"key": "api_endpoint", "label": "API Endpoint", "type": "url", "required": True, "placeholder": "https://api.sevenrooms.com/v1", "description": "SevenRooms API base URL"},
                {"key": "api_key", "label": "API Key", "type": "password", "required": True, "placeholder": "", "description": "SevenRooms API key"},
                {"key": "api_secret", "label": "API Secret", "type": "password", "required": True, "placeholder": "", "description": "SevenRooms API secret"},
                {"key": "venue_group_id", "label": "Venue Group ID", "type": "text", "required": True, "placeholder": "vg_xxxxxxxx", "description": "SevenRooms venue group identifier"},
                {"key": "venues", "label": "Venue IDs (JSON array)", "type": "text", "required": False, "placeholder": '["v_abc123", "v_def456"]', "description": "Specific venue IDs to sync (leave empty for all)"},
                {"key": "sync_reservations", "label": "Sync Reservations", "type": "toggle", "required": False, "description": "Pull reservation and covers data"},
                {"key": "sync_guest_profiles", "label": "Sync Guest Profiles", "type": "toggle", "required": False, "description": "Pull guest profile and preference data"},
            ]
        }
    },
    {
        "id": "resy",
        "name": "Resy",
        "category": "fb",
        "description": "Restaurant reservation platform popular with high-end dining establishments. Real-time availability and guest data.",
        "icon": "📋",
        "website": "https://resy.com/",
        "config_schema": {
            "fields": [
                {"key": "api_key", "label": "API Key", "type": "password", "required": True, "placeholder": "", "description": "Resy API key"},
                {"key": "venue_id", "label": "Venue ID", "type": "text", "required": True, "placeholder": "12345", "description": "Resy venue identifier"},
            ]
        }
    },
    {
        "id": "zenchef",
        "name": "Zenchef",
        "category": "fb",
        "description": "All-in-one restaurant management platform — reservations, reviews, marketing. Popular in European luxury hotels.",
        "icon": "👨‍🍳",
        "website": "https://www.zenchef.com/",
        "config_schema": {
            "fields": [
                {"key": "api_token", "label": "API Token", "type": "password", "required": True, "placeholder": "", "description": "Zenchef API authentication token"},
                {"key": "restaurant_id", "label": "Restaurant ID", "type": "text", "required": True, "placeholder": "rest_001", "description": "Zenchef restaurant identifier"},
            ]
        }
    },

    # ── Incidents / Operations ────────────────
    {
        "id": "unifocus",
        "name": "Unifocus (Knowcross)",
        "category": "incidents",
        "description": "Workforce management and hotel operations platform. Tracks maintenance requests, guest complaints, and housekeeping tasks.",
        "icon": "⚠️",
        "website": "https://unifocus.com/",
        "config_schema": {
            "fields": [
                {"key": "api_endpoint", "label": "API Endpoint", "type": "url", "required": True, "placeholder": "https://api.unifocus.com/v1", "description": "Unifocus API base URL"},
                {"key": "api_key", "label": "API Key", "type": "password", "required": True, "placeholder": "", "description": "Unifocus API key"},
                {"key": "property_id", "label": "Property ID", "type": "text", "required": True, "placeholder": "PROP-001", "description": "Unifocus property identifier"},
                {"key": "sync_maintenance", "label": "Sync Maintenance", "type": "toggle", "required": False, "description": "Pull maintenance/engineering requests"},
                {"key": "sync_complaints", "label": "Sync Complaints", "type": "toggle", "required": False, "description": "Pull guest complaint tickets"},
                {"key": "sync_housekeeping", "label": "Sync Housekeeping", "type": "toggle", "required": False, "description": "Pull housekeeping task data"},
            ]
        }
    },
    {
        "id": "hotsos",
        "name": "HotSOS",
        "category": "incidents",
        "description": "Amadeus HotSOS — service optimization system for hotel operations. Work orders, dispatch, and preventive maintenance.",
        "icon": "🔧",
        "website": "https://www.amadeus-hospitality.com/",
        "config_schema": {
            "fields": [
                {"key": "hostname", "label": "Hostname", "type": "text", "required": True, "placeholder": "hotsos.your-hotel.com", "description": "HotSOS server hostname"},
                {"key": "username", "label": "Username", "type": "text", "required": True, "placeholder": "", "description": "HotSOS API username"},
                {"key": "password", "label": "Password", "type": "password", "required": True, "placeholder": "", "description": "HotSOS API password"},
                {"key": "property_code", "label": "Property Code", "type": "text", "required": True, "placeholder": "HTL001", "description": "HotSOS property code"},
            ]
        }
    },
    {
        "id": "quore",
        "name": "Quore",
        "category": "incidents",
        "description": "Hotel operations management platform — maintenance, housekeeping, inspections, and guest requests in one system.",
        "icon": "📝",
        "website": "https://quore.com/",
        "config_schema": {
            "fields": [
                {"key": "api_key", "label": "API Key", "type": "password", "required": True, "placeholder": "", "description": "Quore API key"},
                {"key": "property_id", "label": "Property ID", "type": "text", "required": True, "placeholder": "PROP-001", "description": "Quore property identifier"},
            ]
        }
    },

    # ── Concierge ─────────────────────────────
    {
        "id": "concierge-organizer",
        "name": "Concierge Organizer",
        "category": "concierge",
        "description": "Digital concierge management platform. Track guest requests, restaurant reservations, transportation, and activity bookings.",
        "icon": "🛎️",
        "website": "https://www.conciergeorganizer.com/",
        "config_schema": {
            "fields": [
                {"key": "api_endpoint", "label": "API Endpoint", "type": "url", "required": True, "placeholder": "https://api.conciergeorganizer.com/v1", "description": "Concierge Organizer API base URL"},
                {"key": "api_key", "label": "API Key", "type": "password", "required": True, "placeholder": "", "description": "API authentication key"},
                {"key": "property_id", "label": "Property ID", "type": "text", "required": True, "placeholder": "PROP-001", "description": "Property identifier in Concierge Organizer"},
            ]
        }
    },
    {
        "id": "alice",
        "name": "ALICE",
        "category": "concierge",
        "description": "Hospitality operations platform combining concierge, maintenance, housekeeping, and guest messaging.",
        "icon": "🤖",
        "website": "https://www.aliceplatform.com/",
        "config_schema": {
            "fields": [
                {"key": "api_endpoint", "label": "API Endpoint", "type": "url", "required": True, "placeholder": "https://api.aliceplatform.com/v2", "description": "ALICE API base URL"},
                {"key": "api_token", "label": "API Token", "type": "password", "required": True, "placeholder": "", "description": "ALICE API bearer token"},
                {"key": "property_id", "label": "Property ID", "type": "text", "required": True, "placeholder": "PROP-001", "description": "ALICE property identifier"},
            ]
        }
    },

    # ── Villas / Rentals ──────────────────────
    {
        "id": "ervr",
        "name": "ERVR",
        "category": "villas",
        "description": "Villa and rental property management via Google Calendar integration. Tracks bookings, availability, and revenue for individual units.",
        "icon": "🏡",
        "website": "",
        "config_schema": {
            "fields": [
                {"key": "calendar_ids", "label": "Google Calendar IDs (JSON)", "type": "text", "required": True, "placeholder": '["cal1@group.calendar.google.com", "cal2@group.calendar.google.com"]', "description": "JSON array of Google Calendar IDs, one per villa/unit"},
                {"key": "sync_interval", "label": "Sync Interval (minutes)", "type": "number", "required": False, "placeholder": "30", "description": "How often to sync calendar data (default: 30 min)"},
            ]
        }
    },
    {
        "id": "guesty",
        "name": "Guesty",
        "category": "villas",
        "description": "Property management platform for short-term and vacation rentals. Multi-channel distribution and unified inbox.",
        "icon": "🔑",
        "website": "https://www.guesty.com/",
        "config_schema": {
            "fields": [
                {"key": "api_token", "label": "API Token", "type": "password", "required": True, "placeholder": "", "description": "Guesty API bearer token"},
                {"key": "account_id", "label": "Account ID", "type": "text", "required": True, "placeholder": "acc_xxxxxxxx", "description": "Guesty account identifier"},
            ]
        }
    },
    {
        "id": "lodgify",
        "name": "Lodgify",
        "category": "villas",
        "description": "Vacation rental software with channel management, website builder, and booking engine.",
        "icon": "🏠",
        "website": "https://www.lodgify.com/",
        "config_schema": {
            "fields": [
                {"key": "api_key", "label": "API Key", "type": "password", "required": True, "placeholder": "", "description": "Lodgify API key"},
                {"key": "property_ids", "label": "Property IDs (comma-separated)", "type": "text", "required": False, "placeholder": "12345,67890", "description": "Specific Lodgify property IDs to sync (leave empty for all)"},
            ]
        }
    },

    # ── Finance ───────────────────────────────
    {
        "id": "sage",
        "name": "Sage",
        "category": "finance",
        "description": "Cloud accounting and financial management. Automate revenue posting, AP/AR, and financial reporting.",
        "icon": "💰",
        "website": "https://www.sage.com/",
        "config_schema": {
            "fields": [
                {"key": "api_endpoint", "label": "API Endpoint", "type": "url", "required": True, "placeholder": "https://api.sage.com/v3.1", "description": "Sage API base URL"},
                {"key": "client_id", "label": "Client ID", "type": "text", "required": True, "placeholder": "", "description": "Sage OAuth client ID"},
                {"key": "client_secret", "label": "Client Secret", "type": "password", "required": True, "placeholder": "", "description": "Sage OAuth client secret"},
                {"key": "company_id", "label": "Company ID", "type": "text", "required": True, "placeholder": "comp_xxxxxxxx", "description": "Sage company/business identifier"},
                {"key": "environment", "label": "Environment", "type": "select", "required": True, "options": [{"value": "sandbox", "label": "Sandbox"}, {"value": "production", "label": "Production"}], "description": "Target Sage environment"},
            ]
        }
    },
    {
        "id": "sap",
        "name": "SAP",
        "category": "finance",
        "description": "SAP ERP for enterprise financial management. Direct RFC/BAPI connectivity for revenue and expense posting.",
        "icon": "📊",
        "website": "https://www.sap.com/",
        "config_schema": {
            "fields": [
                {"key": "hostname", "label": "Hostname", "type": "text", "required": True, "placeholder": "sap.your-hotel.com", "description": "SAP application server hostname"},
                {"key": "client", "label": "Client", "type": "text", "required": True, "placeholder": "100", "description": "SAP client number"},
                {"key": "system_number", "label": "System Number", "type": "text", "required": True, "placeholder": "00", "description": "SAP system number"},
                {"key": "username", "label": "Username", "type": "text", "required": True, "placeholder": "", "description": "SAP user account"},
                {"key": "password", "label": "Password", "type": "password", "required": True, "placeholder": "", "description": "SAP user password"},
            ]
        }
    },
    {
        "id": "xero",
        "name": "Xero",
        "category": "finance",
        "description": "Cloud-based accounting platform for small to mid-size businesses. Bank reconciliation, invoicing, and reporting.",
        "icon": "📒",
        "website": "https://www.xero.com/",
        "config_schema": {
            "fields": [
                {"key": "client_id", "label": "Client ID", "type": "text", "required": True, "placeholder": "", "description": "Xero OAuth2 client ID"},
                {"key": "client_secret", "label": "Client Secret", "type": "password", "required": True, "placeholder": "", "description": "Xero OAuth2 client secret"},
                {"key": "tenant_id", "label": "Tenant ID", "type": "text", "required": True, "placeholder": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx", "description": "Xero organization tenant ID"},
            ]
        }
    },

    # ── Payments ──────────────────────────────
    {
        "id": "adyen",
        "name": "Adyen",
        "category": "payments",
        "description": "Global payment platform for hospitality. Handles in-person terminals, online payments, and multi-currency processing.",
        "icon": "💳",
        "website": "https://www.adyen.com/",
        "config_schema": {
            "fields": [
                {"key": "api_key", "label": "API Key", "type": "password", "required": True, "placeholder": "", "description": "Adyen API key"},
                {"key": "merchant_account", "label": "Merchant Account", "type": "text", "required": True, "placeholder": "EdenRockHotel", "description": "Adyen merchant account name"},
                {"key": "environment", "label": "Environment", "type": "select", "required": True, "options": [{"value": "test", "label": "Test"}, {"value": "live", "label": "Live"}], "description": "Adyen environment"},
                {"key": "terminal_ids", "label": "Terminal IDs (comma-separated)", "type": "text", "required": False, "placeholder": "P400Plus-123456789,V400m-987654321", "description": "POS terminal identifiers"},
            ]
        }
    },
    {
        "id": "stripe",
        "name": "Stripe",
        "category": "payments",
        "description": "Developer-friendly payment infrastructure. Online payments, subscriptions, and financial reporting.",
        "icon": "💜",
        "website": "https://stripe.com/",
        "config_schema": {
            "fields": [
                {"key": "api_key", "label": "Secret Key", "type": "password", "required": True, "placeholder": "sk_live_...", "description": "Stripe secret API key"},
                {"key": "webhook_secret", "label": "Webhook Secret", "type": "password", "required": False, "placeholder": "whsec_...", "description": "Stripe webhook signing secret"},
            ]
        }
    },
    {
        "id": "sumup",
        "name": "SumUp",
        "category": "payments",
        "description": "Mobile and in-store payment solution. Card readers, POS, and payment links for hospitality.",
        "icon": "📱",
        "website": "https://www.sumup.com/",
        "config_schema": {
            "fields": [
                {"key": "api_key", "label": "API Key", "type": "password", "required": True, "placeholder": "", "description": "SumUp API key"},
                {"key": "merchant_code", "label": "Merchant Code", "type": "text", "required": True, "placeholder": "MXXXXXXXX", "description": "SumUp merchant code"},
            ]
        }
    },

    # ── Communications ────────────────────────
    {
        "id": "microsoft-365",
        "name": "Microsoft 365",
        "category": "communications",
        "description": "Microsoft 365 integration — monitor shared mailboxes, sync calendars, and access OneDrive documents via Microsoft Graph API.",
        "icon": "📧",
        "website": "https://www.microsoft.com/microsoft-365",
        "config_schema": {
            "fields": [
                {"key": "tenant_id", "label": "Tenant ID", "type": "text", "required": True, "placeholder": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx", "description": "Azure AD tenant identifier"},
                {"key": "client_id", "label": "Client ID", "type": "text", "required": True, "placeholder": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx", "description": "Azure AD application (client) ID"},
                {"key": "client_secret", "label": "Client Secret", "type": "password", "required": True, "placeholder": "", "description": "Azure AD client secret"},
                {"key": "monitored_mailboxes", "label": "Monitored Mailboxes (JSON)", "type": "text", "required": False, "placeholder": '["reception@hotel.com", "reservations@hotel.com"]', "description": "JSON array of mailbox addresses to monitor"},
                {"key": "onedrive_paths", "label": "OneDrive Paths", "type": "text", "required": False, "placeholder": "/Shared Documents/Reports", "description": "OneDrive/SharePoint paths to monitor"},
                {"key": "sync_email", "label": "Sync Email", "type": "toggle", "required": False, "description": "Monitor and process incoming emails"},
                {"key": "sync_calendar", "label": "Sync Calendar", "type": "toggle", "required": False, "description": "Sync calendar events and meetings"},
                {"key": "sync_files", "label": "Sync Files", "type": "toggle", "required": False, "description": "Monitor OneDrive/SharePoint files"},
            ]
        }
    },
    {
        "id": "google-workspace",
        "name": "Google Workspace",
        "category": "communications",
        "description": "Google Workspace integration — Gmail, Google Calendar, and Google Drive via service account with domain-wide delegation.",
        "icon": "🔷",
        "website": "https://workspace.google.com/",
        "config_schema": {
            "fields": [
                {"key": "service_account_json", "label": "Service Account JSON", "type": "password", "required": True, "placeholder": "", "description": "Google service account credentials JSON (paste full content)"},
                {"key": "delegated_user", "label": "Delegated User", "type": "text", "required": True, "placeholder": "admin@hotel.com", "description": "User to impersonate with domain-wide delegation"},
                {"key": "monitored_calendars", "label": "Monitored Calendars (JSON)", "type": "text", "required": False, "placeholder": '["primary", "hotel-events@hotel.com"]', "description": "JSON array of calendar IDs to sync"},
                {"key": "sync_email", "label": "Sync Email", "type": "toggle", "required": False, "description": "Monitor Gmail inbox"},
                {"key": "sync_calendar", "label": "Sync Calendar", "type": "toggle", "required": False, "description": "Sync Google Calendar events"},
                {"key": "sync_drive", "label": "Sync Drive", "type": "toggle", "required": False, "description": "Monitor Google Drive files"},
            ]
        }
    },

    # ── HR / Scheduling ───────────────────────
    {
        "id": "unifocus-scheduling",
        "name": "Unifocus Scheduling",
        "category": "hr",
        "description": "Workforce management and labor scheduling for hospitality. Forecasting, scheduling, and time & attendance.",
        "icon": "📅",
        "website": "https://unifocus.com/",
        "config_schema": {
            "fields": [
                {"key": "api_endpoint", "label": "API Endpoint", "type": "url", "required": True, "placeholder": "https://api.unifocus.com/scheduling/v1", "description": "Unifocus Scheduling API base URL"},
                {"key": "api_key", "label": "API Key", "type": "password", "required": True, "placeholder": "", "description": "Unifocus Scheduling API key"},
                {"key": "property_id", "label": "Property ID", "type": "text", "required": True, "placeholder": "PROP-001", "description": "Unifocus property identifier"},
            ]
        }
    },
    {
        "id": "deputy",
        "name": "Deputy",
        "category": "hr",
        "description": "Workforce management platform — scheduling, timesheets, tasking, and communication for hospitality teams.",
        "icon": "👤",
        "website": "https://www.deputy.com/",
        "config_schema": {
            "fields": [
                {"key": "api_endpoint", "label": "API Endpoint", "type": "url", "required": True, "placeholder": "https://once.deputy.com/api/v1", "description": "Deputy API base URL (includes your subdomain)"},
                {"key": "api_token", "label": "API Token", "type": "password", "required": True, "placeholder": "", "description": "Deputy permanent access token"},
                {"key": "location_id", "label": "Location ID", "type": "text", "required": True, "placeholder": "12345", "description": "Deputy location identifier"},
            ]
        }
    },
    {
        "id": "planday",
        "name": "Planday",
        "category": "hr",
        "description": "Employee scheduling and workforce management. Shift planning, time tracking, and payroll integration.",
        "icon": "📆",
        "website": "https://www.planday.com/",
        "config_schema": {
            "fields": [
                {"key": "client_id", "label": "Client ID", "type": "text", "required": True, "placeholder": "", "description": "Planday API client ID"},
                {"key": "client_secret", "label": "Client Secret", "type": "password", "required": True, "placeholder": "", "description": "Planday API client secret"},
                {"key": "department_id", "label": "Department ID", "type": "text", "required": True, "placeholder": "12345", "description": "Planday department identifier"},
            ]
        }
    },
]


def get_catalog():
    """Return full catalog with category metadata."""
    return {
        "categories": APP_CATEGORIES,
        "apps": APP_CATALOG,
    }


def get_catalog_by_category(category):
    """Return apps filtered by category."""
    return [a for a in APP_CATALOG if a["category"] == category]


def get_app_by_id(app_id):
    """Return a single app by its ID."""
    for a in APP_CATALOG:
        if a["id"] == app_id:
            return a
    return None
