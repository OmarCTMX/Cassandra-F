import uuid
import time
from cassandra.util import uuid_from_time

USER_IDS = {
    "arantxa_af": uuid.UUID("00000000-0000-0000-0000-000000000001"),
    "cesar_ss":   uuid.UUID("00000000-0000-0000-0000-000000000002"),
    "omar_oa":    uuid.UUID("00000000-0000-0000-0000-000000000003"),
    "doritoo":    uuid.UUID("00000000-0000-0000-0000-000000000004"),
}

POST_IDS = {
    "p_001": uuid.UUID("00000000-0000-0000-0000-000000000101"),
    "p_002": uuid.UUID("00000000-0000-0000-0000-000000000102"),
    "p_003": uuid.UUID("00000000-0000-0000-0000-000000000103"),
}

POST_NAMES = {
    "p_001": "Just wrapped my Honda Civic!",
    "p_002": "Testing Dgraph traversal queries.",
    "p_003": "Pokémon VGC strategies for this season.",
}

SESSION_IDS = {
    "s_001": uuid.UUID("00000000-0000-0000-0000-000000000201"),
    "s_002": uuid.UUID("00000000-0000-0000-0000-000000000202"),
    "s_003": uuid.UUID("00000000-0000-0000-0000-000000000203"),
}

def tuuid():
    t = uuid_from_time(time.time())
    time.sleep(0.01)
    return t


def populate_interactions(session):
    q = """
        INSERT INTO user_interactions
            (user_id, created_at, content_id, interaction_type, target_user_id)
        VALUES (%s, %s, %s, %s, %s)
    """
    rows = [
        (USER_IDS["arantxa_af"], POST_IDS["p_001"], "like",   USER_IDS["cesar_ss"]),
        (USER_IDS["arantxa_af"], POST_IDS["p_003"], "share",  USER_IDS["doritoo"]),
        (USER_IDS["arantxa_af"], POST_IDS["p_002"], "repost", USER_IDS["omar_oa"]),
        (USER_IDS["cesar_ss"],   POST_IDS["p_002"], "like",   USER_IDS["omar_oa"]),
        (USER_IDS["cesar_ss"],   POST_IDS["p_001"], "share",  USER_IDS["arantxa_af"]),
        (USER_IDS["cesar_ss"],   POST_IDS["p_003"], "repost", USER_IDS["doritoo"]),
        (USER_IDS["omar_oa"],    POST_IDS["p_003"], "like",   USER_IDS["doritoo"]),
        (USER_IDS["omar_oa"],    POST_IDS["p_001"], "share",  USER_IDS["cesar_ss"]),
        (USER_IDS["doritoo"],    POST_IDS["p_001"], "repost", USER_IDS["cesar_ss"]),
        (USER_IDS["doritoo"],    POST_IDS["p_002"], "like",   USER_IDS["omar_oa"]),
        (USER_IDS["doritoo"],    POST_IDS["p_003"], "share",  USER_IDS["arantxa_af"]),
    ]
    for user_id, content_id, itype, target in rows:
        session.execute(q, (user_id, tuuid(), content_id, itype, target))
    print("  [C1] Interacciones insertadas.")


def populate_post_interactions(session):
    q = "UPDATE post_interactions SET total = total + %s WHERE post_id = %s AND interaction_type = %s"
    rows = [
        (POST_IDS["p_001"], "like",   2),
        (POST_IDS["p_001"], "share",  2),
        (POST_IDS["p_001"], "repost", 1),
        (POST_IDS["p_002"], "like",   2),
        (POST_IDS["p_002"], "share",  1),
        (POST_IDS["p_002"], "repost", 1),
        (POST_IDS["p_003"], "like",   1),
        (POST_IDS["p_003"], "share",  2),
        (POST_IDS["p_003"], "repost", 1),
    ]
    for post_id, itype, count in rows:
        session.execute(q, (count, post_id, itype))
    print("  [C2] Interacciones por publicación insertadas.")


def populate_notifications(session):
    q = """
        INSERT INTO user_notifications
            (user_id, created_at, notification_id, notification_type, actor_id, content_id, is_read)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    rows = [
        (USER_IDS["arantxa_af"], uuid.uuid4(), "like_received",   USER_IDS["cesar_ss"],   POST_IDS["p_001"]),
        (USER_IDS["arantxa_af"], uuid.uuid4(), "new_follower",    USER_IDS["doritoo"],    None),
        (USER_IDS["arantxa_af"], uuid.uuid4(), "repost_received", USER_IDS["omar_oa"],    POST_IDS["p_003"]),
        (USER_IDS["cesar_ss"],   uuid.uuid4(), "like_received",   USER_IDS["arantxa_af"], POST_IDS["p_002"]),
        (USER_IDS["cesar_ss"],   uuid.uuid4(), "mentioned",       USER_IDS["doritoo"],    POST_IDS["p_001"]),
        (USER_IDS["omar_oa"],    uuid.uuid4(), "new_follower",    USER_IDS["cesar_ss"],   None),
        (USER_IDS["doritoo"],    uuid.uuid4(), "repost_received", USER_IDS["arantxa_af"], POST_IDS["p_003"]),
    ]
    for user_id, notif_id, ntype, actor, content in rows:
        session.execute(q, (user_id, tuuid(), notif_id, ntype, actor, content, False))
    print("  [C3] Notificaciones insertadas.")


def populate_hashtag_trends(session):
    q = "UPDATE hashtag_trends SET usage_count = usage_count + %s WHERE hashtag = %s AND hour_bucket = %s"
    rows = [
        ("#AmericaELIMINADO", "2026-05-10-10", 4200),
        ("#AmericaELIMINADO", "2026-05-10-11", 3800),
        ("#Baños",            "2026-05-10-10", 980),
        ("#Baños",            "2026-05-10-11", 1100),
        ("#Michael",          "2026-05-10-11", 2300),
        ("#Michael",          "2026-05-10-12", 1750),
        ("#Vibecodeo",        "2026-05-10-12", 670),
        ("#Vibecodeo",        "2026-05-10-13", 540),
        ("#NoTengoTrabajo",   "2026-05-10-13", 3100),
        ("#NoTengoTrabajo",   "2026-05-10-14", 2900),
        ("#Mamá",             "2026-05-10-10", 98000),
        ("#Mamá",             "2026-05-10-11", 112000),
        ("#Mamá",             "2026-05-10-12", 134000),
        ("#Mamá",             "2026-05-10-13", 99000),
    ]
    for hashtag, bucket, count in rows:
        session.execute(q, (count, hashtag, bucket))
    print("  [C4] Tendencias de hashtags insertadas.")


def populate_account_changes(session):
    q = """
        INSERT INTO account_changes
            (user_id, changed_at, field_changed, previous_value, new_value)
        VALUES (%s, %s, %s, %s, %s)
    """
    rows = [
        (USER_IDS["arantxa_af"], "account_created", "",                "2024-01-15"),
        (USER_IDS["arantxa_af"], "bio",             "",                "Just a girl who loves cars 🚗"),
        (USER_IDS["arantxa_af"], "username",        "arantxa_old",     "arantxa_af"),
        (USER_IDS["cesar_ss"],   "account_created", "",                "2024-03-10"),
        (USER_IDS["cesar_ss"],   "email",           "viejo@gmail.com", "cesar@gmail.com"),
        (USER_IDS["omar_oa"],    "account_created", "",                "2023-11-20"),
        (USER_IDS["omar_oa"],    "avatar",          "foto_vieja.jpg",  "foto_nueva.jpg"),
        (USER_IDS["doritoo"],    "account_created", "",                "2025-01-05"),
        (USER_IDS["doritoo"],    "bio",             "",                "Pokemon VGC player 🎮"),
    ]
    for user_id, field, prev, new in rows:
        session.execute(q, (user_id, tuuid(), field, prev, new))
    print("  [C5] Cambios de cuenta insertados.")


def populate_affinity(session):
    q = """
        UPDATE user_affinity
        SET likes_given       = likes_given       + %s,
            shares_made       = shares_made       + %s,
            reposts_made      = reposts_made      + %s,
            interaction_score = interaction_score + %s
        WHERE user_id = %s AND target_user_id = %s
    """
    # score: like +1, share +2, repost +2
    # coherente con C1: arantxa le dio like a post de cesar (+1), share a doritoo (+2), repost a omar (+2)
    rows = [
        (USER_IDS["arantxa_af"], USER_IDS["cesar_ss"],   1, 0, 0, 1),
        (USER_IDS["arantxa_af"], USER_IDS["doritoo"],    0, 1, 0, 2),
        (USER_IDS["arantxa_af"], USER_IDS["omar_oa"],    0, 0, 1, 2),
        (USER_IDS["cesar_ss"],   USER_IDS["omar_oa"],    1, 0, 0, 1),
        (USER_IDS["cesar_ss"],   USER_IDS["arantxa_af"], 0, 1, 0, 2),
        (USER_IDS["cesar_ss"],   USER_IDS["doritoo"],    0, 0, 1, 2),
        (USER_IDS["omar_oa"],    USER_IDS["doritoo"],    1, 0, 0, 1),
        (USER_IDS["omar_oa"],    USER_IDS["cesar_ss"],   0, 1, 0, 2),
        (USER_IDS["doritoo"],    USER_IDS["cesar_ss"],   0, 0, 1, 2),
        (USER_IDS["doritoo"],    USER_IDS["omar_oa"],    1, 0, 0, 1),
        (USER_IDS["doritoo"],    USER_IDS["arantxa_af"], 0, 1, 0, 2),
    ]
    for user_id, target, likes, shares, reposts, score in rows:
        session.execute(q, (likes, shares, reposts, score, user_id, target))
    print("  [C6] Afinidad insertada.")


def populate_sessions(session):
    q = """
        INSERT INTO session_events
            (date, session_id, event_at, user_id, event_type, ip_address, user_agent)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    today = "2026-05-10"
    rows = [
        (today, SESSION_IDS["s_001"], USER_IDS["arantxa_af"], "login",   "192.168.1.10", "iPhone 15 / iOS 18"),
        (today, SESSION_IDS["s_001"], USER_IDS["arantxa_af"], "logout",  "192.168.1.10", "iPhone 15 / iOS 18"),
        (today, SESSION_IDS["s_002"], USER_IDS["cesar_ss"],   "login",   "10.0.0.5",     "Chrome / Windows 11"),
        (today, SESSION_IDS["s_002"], USER_IDS["cesar_ss"],   "timeout", "10.0.0.5",     "Chrome / Windows 11"),
        (today, SESSION_IDS["s_003"], USER_IDS["doritoo"],    "login",   "172.16.0.3",   "Safari / macOS"),
        (today, SESSION_IDS["s_003"], USER_IDS["doritoo"],    "logout",  "172.16.0.3",   "Safari / macOS"),
    ]
    for date, sid, uid, etype, ip, ua in rows:
        session.execute(q, (date, sid, tuuid(), uid, etype, ip, ua))
    print("  [C7] Sesiones insertadas.")


def load_data(session):
    print("\nPopulando base de datos...\n")
    populate_interactions(session)
    populate_post_interactions(session)
    populate_notifications(session)
    populate_hashtag_trends(session)
    populate_account_changes(session)
    populate_affinity(session)
    populate_sessions(session)
    print("\nBase de datos lista.\n")
