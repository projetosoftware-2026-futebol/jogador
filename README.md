# Player Service

## Overview

The **Player Service** is a REST API responsible for managing player records and market transactions within the Fut Manager ecosystem.

> [!NOTE]
> English aliases (such as `/players`) are supported alongside standard Portuguese route prefixes for full backward compatibility.

---

## Running Locally

1. Install the required project dependencies:

```bash
pip install -r requirements.txt

```

2. Start the development server using FastAPI:

```bash
fastapi dev app/main.py

```

> [!TIP]
> Once the server is running, interactive API documentation is available at `[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)`.

---

## Database Configuration

The API reads player records from an SQL table named `jogadores`. Records are expected to be pre-populated in the database rather than created directly through code.

By default, the application uses SQLite at `sqlite:///./jogadores.db`. To configure a custom database, set the `DATABASE_URL` environment variable before starting the API:

```bash
# On Linux/macOS
export DATABASE_URL="sqlite:///./jogadores.db"

# On Windows (CMD)
set DATABASE_URL=sqlite:///./jogadores.db

fastapi dev app/main.py

```

> [!IMPORTANT]
> Refer to the `schema.sql` file for the expected database table structure, constraints, and data types.

---

## Player Model

```json
{
  "id": 1,
  "nome": "Rafael Nunes",
  "valor": 8500000,
  "rating": 84,
  "posicao": "GOL",
  "status": "DISPONIVEL",
  "clube_id": null
}
```

### Allowed Positions

- **ATA** (Attacker)
- **PD** (Right Winger)
- **PE** (Left Winger)
- **MC** (Midfielder)
- **LD** (Right Back)
- **LE** (Left Back)
- **ZAG** (Center Back)
- **GOL** (Goalkeeper)

---

## API Endpoints Reference

| Method | Endpoint                     | Description                           |
| ------ | ---------------------------- | ------------------------------------- |
| `GET`  | `/jogadores` (or `/players`) | List all players                      |
| `GET`  | `/jogadores/{id}`            | Retrieve a specific player by ID      |
| `POST` | `/jogadores/{id}/buy`        | Purchase a player for a club          |
| `POST` | `/jogadores/{id}/sell`       | Sell or release a player              |
| `GET`  | `/health`                    | Check service health and availability |

### Usage Examples

#### Buy a Player

```bash
curl -X POST http://127.0.0.1:8000/jogadores/1/buy \
  -H "Content-Type: application/json" \
  -d "{\"clube_id\": 42}"

```

#### Sell a Player

```bash
curl -X POST http://127.0.0.1:8000/jogadores/1/sell \
  -H "Content-Type: application/json" \
  -d "{\"clube_id\": 42}"

```
