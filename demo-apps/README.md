# Demo Apps

Mock API services simulating a hotel tech stack for Hotel Intel development.

## Deployment

Each service runs on the sandbox server (51.158.66.245) as a systemd service.

### Quick Setup

```bash
# For each app:
cd /opt/<app-name>
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py  # or use the systemd service
```

### Services

| App | Port | Directory | Systemd Unit |
|-----|------|-----------|-------------|
| Opera PMS | 8080 | /opt/opera-api | opera-api.service |
| TAC Spa | 8081 | /opt/tac-api | tac-api.service |
| SevenRooms | 8082 | /opt/sevenrooms-api | sevenrooms-api.service |
| Unifocus | 8083 | /opt/unifocus-api | unifocus-api.service |
| Concierge Organizer | 8084 | /opt/concierge-api | concierge-api.service |

### Oracle XE (for Opera PMS)

Opera PMS uses Oracle XE 21c in Docker. Schema and seed data in  and .

See [Demo Sandbox docs](../docs/demo-sandbox.md) for full details.
