from cassandra.cluster import Cluster

KEYSPACE = "instagram_clone"

def get_client():
    cluster = Cluster(['127.0.0.1'], port=9042)
    session = cluster.connect()
    return session

def setup_keyspace(session):
    session.execute(f"""
        CREATE KEYSPACE IF NOT EXISTS {KEYSPACE}
        WITH replication = {{'class': 'SimpleStrategy', 'replication_factor': '1'}}
    """)
    session.set_keyspace(KEYSPACE)
    print(f"[Cassandra] Keyspace '{KEYSPACE}' listo.")

def get_session():
    session = get_client()
    setup_keyspace(session)
    return session
