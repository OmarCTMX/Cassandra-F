import csv
import pydgraph

def load_data(client):
    txn = client.txn()
    mutations = []

    try:
        # 1. Load Usuarios
        with open('data/usuarios.csv', mode='r', encoding='utf-8') as f:
            for row in csv.DictReader(f):
                mutations.append({
                    "uid": f"_:{row['username']}",
                    "dgraph.type": "Usuario",
                    "username": row['username'],
                    "email": row['email'],
                    "password": row['password'],
                    "bio": row['bio'],
                    "interests": row['interests']
                })

        # 2. Load Posts
        with open('data/posts.csv', mode='r', encoding='utf-8') as f:
            for row in csv.DictReader(f):
                mutations.append({
                    "uid": f"_:{row['post_id']}",
                    "dgraph.type": "Post",
                    "post_id": row['post_id'],
                    "content": row['content'],
                    "hashtags": row['hashtags'],
                    "timestamp": row['timestamp']
                })

        # 3. Load Interacciones
        # Pre-group Comentario rows so each comment becomes ONE complete mutation object
        comment_map = {}  # { source_id: { ...node data... } }
        standard_edges = []

        with open('data/interacciones.csv', mode='r', encoding='utf-8') as f:
            for row in csv.DictReader(f):
                rel = row['relation']
                source_uid = f"_:{row['source_id']}"
                target_uid = f"_:{row['target_id']}"

                if row['source_type'] == 'Comentario':
                    # Merge all edges for the same comment into one node
                    if source_uid not in comment_map:
                        comment_map[source_uid] = {
                            "uid": source_uid,
                            "dgraph.type": "Comentario",
                        }
                    comment_map[source_uid][rel] = {"uid": target_uid}
                    # Add timestamp if present and not already set
                    if row.get('timestamp') and 'timestamp' not in comment_map[source_uid]:
                        comment_map[source_uid]['timestamp'] = row['timestamp']
                else:
                    standard_edges.append({
                        "uid": source_uid,
                        rel: [{"uid": target_uid}]
                    })

        mutations.extend(comment_map.values())
        mutations.extend(standard_edges)

        response = txn.mutate(set_obj=mutations)
        txn.commit()
        print(f"Data populated! Entities created: {len(response.uids)}")

    except Exception as e:
        print(f"Error populating data: {e}")
    finally:
        txn.discard()