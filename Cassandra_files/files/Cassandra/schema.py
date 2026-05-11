TABLES = [
    """
    CREATE TABLE IF NOT EXISTS user_interactions (
        user_id          UUID,
        created_at       TIMEUUID,
        content_id       UUID,
        interaction_type TEXT,
        target_user_id   UUID,
        PRIMARY KEY (user_id, created_at, content_id)
    ) WITH CLUSTERING ORDER BY (created_at DESC, content_id ASC)
    AND default_time_to_live = 7776000
    """,
    """
    CREATE TABLE IF NOT EXISTS post_interactions (
        post_id          UUID,
        interaction_type TEXT,
        total            COUNTER,
        PRIMARY KEY (post_id, interaction_type)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS user_notifications (
        user_id           UUID,
        created_at        TIMEUUID,
        notification_id   UUID,
        notification_type TEXT,
        actor_id          UUID,
        content_id        UUID,
        is_read           BOOLEAN,
        PRIMARY KEY (user_id, created_at)
    ) WITH CLUSTERING ORDER BY (created_at DESC)
    AND default_time_to_live = 2592000
    """,
    """
    CREATE TABLE IF NOT EXISTS hashtag_trends (
        hashtag     TEXT,
        hour_bucket TEXT,
        usage_count COUNTER,
        PRIMARY KEY (hashtag, hour_bucket)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS account_changes (
        user_id        UUID,
        changed_at     TIMEUUID,
        field_changed  TEXT,
        previous_value TEXT,
        new_value      TEXT,
        PRIMARY KEY (user_id, changed_at)
    ) WITH CLUSTERING ORDER BY (changed_at DESC)
    """,
    """
    CREATE TABLE IF NOT EXISTS user_affinity (
        user_id           UUID,
        target_user_id    UUID,
        likes_given       COUNTER,
        shares_made       COUNTER,
        reposts_made      COUNTER,
        interaction_score COUNTER,
        PRIMARY KEY (user_id, target_user_id)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS session_events (
        date        TEXT,
        session_id  UUID,
        event_at    TIMEUUID,
        user_id     UUID,
        event_type  TEXT,
        ip_address  TEXT,
        user_agent  TEXT,
        PRIMARY KEY ((date, session_id), event_at)
    ) WITH CLUSTERING ORDER BY (event_at ASC)
    AND default_time_to_live = 7776000
    """,
]

def create_tables(session):
    for table in TABLES:
        session.execute(table)
    print("[Cassandra] Tablas creadas correctamente.")
