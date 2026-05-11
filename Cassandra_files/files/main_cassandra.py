import uuid
from Cassandra.client import get_session
from Cassandra.schema import create_tables
from Cassandra.populate import load_data, USER_IDS, POST_IDS, POST_NAMES, SESSION_IDS

ID_TO_NAME = {v: k for k, v in USER_IDS.items()}

def nombre(uid):
    return f"@{ID_TO_NAME.get(uid, str(uid)[:8])}"

def separador():
    print("\n" + "─" * 50)

def header(titulo):
    separador()
    print(f"  {titulo}")
    separador()

def elegir_usuario():
    print("  Usuarios disponibles:")
    usernames = list(USER_IDS.keys())
    for i, u in enumerate(usernames, 1):
        print(f"    {i}. @{u}")
    opcion = input("\n  Selecciona usuario (1-4): ").strip()
    if not opcion.isdigit() or not (1 <= int(opcion) <= 4):
        print("  Opción inválida.")
        return None, None
    username = usernames[int(opcion) - 1]
    return username, USER_IDS[username]


def c1_interacciones(session):
    header("C1 — Interacciones de un usuario")
    username, user_id = elegir_usuario()
    if not user_id:
        return

    rows = list(session.execute(
        "SELECT * FROM user_interactions WHERE user_id = %s LIMIT 10",
        (user_id,)
    ))
    if not rows:
        print("  Sin interacciones registradas.")
        return

    print(f"\n  Historial de @{username}:\n")
    for r in rows:
        target = nombre(r.target_user_id) if r.target_user_id else "—"
        print(f"    [{r.interaction_type.upper():<8}]  post: {str(r.content_id)[:8]}...  →  {target}")


def c2_interacciones_post(session):
    header("C2 — Interacciones por publicación")
    posts = list(POST_IDS.keys())
    print("  Publicaciones disponibles:")
    for i, p in enumerate(posts, 1):
        print(f"    {i}. {p}  —  {POST_NAMES[p]}")
        print(f"       UUID: {POST_IDS[p]}")

    opcion = input("\n  Selecciona publicación (1-3): ").strip()
    if not opcion.isdigit() or not (1 <= int(opcion) <= 3):
        print("  Opción inválida.")
        return
    post_key = posts[int(opcion) - 1]
    post_id  = POST_IDS[post_key]

    rows = list(session.execute(
        "SELECT * FROM post_interactions WHERE post_id = %s",
        (post_id,)
    ))
    if not rows:
        print("  Sin interacciones registradas.")
        return

    print(f"\n  Interacciones en \"{POST_NAMES[post_key]}\"")
    print(f"  UUID: {post_id}\n")
    total = 0
    for r in rows:
        print(f"    [{r.interaction_type.upper():<8}]  {r.total}")
        total += r.total
    print(f"\n    Total general: {total}")


def c3_notificaciones(session):
    header("C3 — Notificaciones de un usuario")
    username, user_id = elegir_usuario()
    if not user_id:
        return

    rows = list(session.execute(
        "SELECT * FROM user_notifications WHERE user_id = %s LIMIT 20",
        (user_id,)
    ))
    if not rows:
        print("  Sin notificaciones.")
        return

    print(f"\n  Notificaciones de @{username}:\n")
    for r in rows:
        actor    = nombre(r.actor_id) if r.actor_id else "—"
        leido    = "✓" if r.is_read else "✗"
        contenido = str(r.content_id)[:8] + "..." if r.content_id else "—"
        print(f"    [{r.notification_type:<20}]  de: {actor:<15}  post: {contenido}  leído: {leido}")


def c4_hashtags(session):
    header("C4 — Tendencias de hashtags por hora")
    hashtags = ["#AmericaELIMINADO", "#Baños", "#Michael", "#Vibecodeo", "#NoTengoTrabajo", "#Mamá"]
    print("  Hashtags disponibles:")
    for i, h in enumerate(hashtags, 1):
        print(f"    {i}. {h}")

    opcion = input("\n  Selecciona hashtag (1-6): ").strip()
    if not opcion.isdigit() or not (1 <= int(opcion) <= 6):
        print("  Opción inválida.")
        return
    hashtag = hashtags[int(opcion) - 1]

    buckets = [
        "2026-05-10-10", "2026-05-10-11",
        "2026-05-10-12", "2026-05-10-13", "2026-05-10-14"
    ]

    resultados = []
    for bucket in buckets:
        rows = list(session.execute(
            "SELECT usage_count FROM hashtag_trends WHERE hashtag = %s AND hour_bucket = %s",
            (hashtag, bucket)
        ))
        if rows and rows[0].usage_count:
            resultados.append((bucket, rows[0].usage_count))

    if not resultados:
        print("  Sin datos para este hashtag.")
        return

    resultados.sort(key=lambda x: x[1], reverse=True)

    print(f"\n  Uso de {hashtag} (ordenado por mayor actividad):\n")
    for bucket, count in resultados:
        barra = "█" * min(int(count / 5000) + 1, 20)
        print(f"    {bucket}  →  {count:>8} usos  {barra}")


def c5_cambios(session):
    header("C5 — Historial de cambios de cuenta")
    username, user_id = elegir_usuario()
    if not user_id:
        return

    rows = list(session.execute(
        "SELECT * FROM account_changes WHERE user_id = %s",
        (user_id,)
    ))
    if not rows:
        print("  Sin cambios registrados.")
        return

    print(f"\n  Historial de cambios de @{username}:\n")
    for r in rows:
        prev = f'"{r.previous_value}"' if r.previous_value else "vacío"
        print(f"    [{r.field_changed:<18}]  {prev}  →  \"{r.new_value}\"")


def c6_afinidad(session):
    header("C6 — Afinidad de contenido (Lo que ves)")
    username, user_id = elegir_usuario()
    if not user_id:
        return

    rows = list(session.execute(
        "SELECT * FROM user_affinity WHERE user_id = %s",
        (user_id,)
    ))
    if not rows:
        print("  Sin datos de afinidad.")
        return

    rows.sort(key=lambda r: r.interaction_score, reverse=True)

    print(f"\n  Cuentas priorizadas en el feed de @{username}:\n")
    for r in rows:
        target = nombre(r.target_user_id)
        print(f"    {target:<20}  score: {r.interaction_score}  "
              f"(likes: {r.likes_given}  shares: {r.shares_made}  reposts: {r.reposts_made})")


def c7_sesiones(session):
    header("C7 — Eventos de sesión por día")
    nombres_sesion = {"s_001": "arantxa_af", "s_002": "cesar_ss", "s_003": "doritoo"}
    sesiones = list(SESSION_IDS.keys())
    print("  Sesiones disponibles (2026-05-10):")
    for i, s in enumerate(sesiones, 1):
        print(f"    {i}. {s}  (@{nombres_sesion[s]})")

    opcion = input("\n  Selecciona sesión (1-3): ").strip()
    if not opcion.isdigit() or not (1 <= int(opcion) <= 3):
        print("  Opción inválida.")
        return
    sid_key = sesiones[int(opcion) - 1]
    sid     = SESSION_IDS[sid_key]

    rows = list(session.execute(
        "SELECT * FROM session_events WHERE date = %s AND session_id = %s",
        ("2026-05-10", sid)
    ))
    if not rows:
        print("  Sin eventos.")
        return

    print(f"\n  Eventos de {sid_key} (@{nombres_sesion[sid_key]}):\n")
    for r in rows:
        print(f"    [{r.event_type.upper():<8}]  ip: {r.ip_address:<15}  dispositivo: {r.user_agent}")


def menu():
    session = get_session()
    create_tables(session)

    while True:
        print("\n" + "═" * 50)
        print("   Instagram Clone — Cassandra")
        print("═" * 50)
        print("   1. Poblar la base de datos")
        print("   2. C1 — Interacciones de un usuario")
        print("   3. C2 — Interacciones por publicación")
        print("   4. C3 — Notificaciones de un usuario")
        print("   5. C4 — Tendencias de hashtags por hora")
        print("   6. C5 — Historial de cambios de cuenta")
        print("   7. C6 — Afinidad de contenido (Lo que ves)")
        print("   8. C7 — Eventos de sesión por día")
        print("   0. Salir")
        print("─" * 50)

        opcion = input("   Selecciona una opción: ").strip()

        if opcion == "1":
            load_data(session)
        elif opcion == "2":
            c1_interacciones(session)
        elif opcion == "3":
            c2_interacciones_post(session)
        elif opcion == "4":
            c3_notificaciones(session)
        elif opcion == "5":
            c4_hashtags(session)
        elif opcion == "6":
            c5_cambios(session)
        elif opcion == "7":
            c6_afinidad(session)
        elif opcion == "8":
            c7_sesiones(session)
        elif opcion == "0":
            print("\n  Hasta luego.\n")
            break
        else:
            print("\n  Opción no válida, intenta de nuevo.")


if __name__ == "__main__":
    menu()
