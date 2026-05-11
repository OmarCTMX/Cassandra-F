import json
import uuid
from datetime import datetime

# ── helpers ──────────────────────────────────────────────────────────────────

def serialize(rows):
    """convierte filas de Cassandra a lista de dicts imprimibles"""
    result = []
    for row in rows:
        d = {}
        for k, v in row._asdict().items():
            if isinstance(v, uuid.UUID):
                d[k] = str(v)
            elif isinstance(v, datetime):
                d[k] = v.isoformat()
            else:
                d[k] = v
        result.append(d)
    return result

def print_result(title, rows):
    data = serialize(rows)
    print(f"\n--- {title} ---")
    print(json.dumps(data, indent=2, ensure_ascii=False))
    return data

# ── C1 — Interacciones de un usuario ─────────────────────────────────────────

def get_user_interactions(session, user_id: str, limit: int = 20):
    """
    Historial de likes, shares, reposts y follows de un usuario.
    Ordenado por created_at DESC automáticamente por el clustering key.
    """
    rows = session.execute(
        "SELECT * FROM user_interactions WHERE user_id = %s LIMIT %s",
        (uuid.UUID(user_id), limit)
    )
    return print_result("C1 — Interacciones del usuario", rows)

# ── C3 — Notificaciones de un usuario ────────────────────────────────────────

def get_user_notifications(session, user_id: str, limit: int = 20):
    """
    Últimas notificaciones de un usuario (like_received, new_follower, etc.)
    Ordenado por created_at DESC.
    """
    rows = session.execute(
        "SELECT * FROM user_notifications WHERE user_id = %s LIMIT %s",
        (uuid.UUID(user_id), limit)
    )
    return print_result("C3 — Notificaciones del usuario", rows)

# ── C4 — Tendencias de hashtags ───────────────────────────────────────────────

def get_hashtag_trend(session, hashtag: str, hour_bucket: str):
    """
    Uso de un hashtag en una hora específica.
    hour_bucket formato: YYYY-MM-DD-HH
    """
    rows = session.execute(
        "SELECT * FROM hashtag_trends WHERE hashtag = %s AND hour_bucket = %s",
        (hashtag, hour_bucket)
    )
    return print_result(f"C4 — Tendencia de {hashtag} en {hour_bucket}", rows)

# ── C5 — Historial de cambios de cuenta ──────────────────────────────────────

def get_account_changes(session, user_id: str):
    """
    Todos los cambios de identidad de una cuenta (nombre, bio, email, etc.)
    Ordenado por changed_at DESC. Registro permanente, sin TTL.
    """
    rows = session.execute(
        "SELECT * FROM account_changes WHERE user_id = %s",
        (uuid.UUID(user_id),)
    )
    return print_result("C5 — Historial de cambios de cuenta", rows)

# ── C6 — Afinidad de contenido ───────────────────────────────────────────────

def get_user_affinity(session, user_id: str, limit: int = 10):
    """
    Cuentas con las que más interactúa un usuario, ordenadas por interaction_score DESC.
    Alimenta el feed y la sección 'Lo que ves'.
    """
    rows = session.execute(
        """
        SELECT * FROM user_affinity
        WHERE user_id = %s
        LIMIT %s
        """,
        (uuid.UUID(user_id), limit)
    )
    # ordenamos en Python porque COUNTER no soporta ORDER BY en Cassandra
    data = serialize(rows)
    data.sort(key=lambda x: x.get("interaction_score", 0), reverse=True)
    print(f"\n--- C6 — Afinidad de contenido (top {limit}) ---")
    print(json.dumps(data, indent=2, ensure_ascii=False))
    return data

# ── C7 — Eventos de sesión por día ───────────────────────────────────────────

def get_session_events(session, date: str, session_id: str):
    """
    Eventos de una sesión específica en un día dado.
    Ordenado por event_at ASC para reconstruir la línea de tiempo.
    date formato: YYYY-MM-DD
    """
    rows = session.execute(
        "SELECT * FROM session_events WHERE date = %s AND session_id = %s",
        (date, uuid.UUID(session_id))
    )
    return print_result(f"C7 — Sesión {session_id} del {date}", rows)


# ── ejecutar todas las consultas ─────────────────────────────────────────────

def execute_all_queries(session):
    # IDs de prueba que coinciden con populate.py
    USER_1 = "00000000-0000-0000-0000-000000000001"
    USER_2 = "00000000-0000-0000-0000-000000000002"
    SESSION_1 = "00000000-0000-0000-0000-000000000201"
    today = datetime.utcnow().strftime("%Y-%m-%d")

    get_user_interactions(session, USER_1)
    get_user_notifications(session, USER_1)
    get_hashtag_trend(session, "#reels", f"{today[:10].replace('-', '-')[:7]}-15-11"
                      if False else "2025-07-15-11")
    get_account_changes(session, USER_1)
    get_user_affinity(session, USER_1)
    get_session_events(session, today, SESSION_1)
