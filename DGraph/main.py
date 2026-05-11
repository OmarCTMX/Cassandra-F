import json
from connect import get_client, set_schema
from populate import load_data

def run_query(client, title, query, variables=None):
    txn = client.txn()
    try:
        res = txn.query(query, variables=variables)
        print(f"\n--- {title} ---")
        print(json.dumps(json.loads(res.json), indent=2))
    finally:
        txn.discard()

def execute_all_queries(client):
    # Req 1: Mapeo de Seguidores y Red de Contactos
    q1 = """
    query follower_mapping($user: string) {
      red_contactos(func: eq(username, $user)) {
        username
        sigue_a { username }
        seguidores: ~sigue_a { username }
      }
    }
    """
    run_query(client, "1. Mapeo de Seguidores (arantxa_af)", q1, {'$user': 'arantxa_af'})

    # Req 2: Interacciones Directas (Likes)
    q2 = """
    query likes_mapping($user: string) {
      likes(func: eq(username, $user)) {
        username
        dio_like {
          post_id
          content
        }
      }
    }
    """
    run_query(client, "2. Interacciones Directas / Likes (cesar_ss)", q2, {'$user': 'cesar_ss'})

    # Req 3: Estructuración de Hilos de Comentarios
    q3 = """
    query comments($post: string) {
      hilo_comentarios(func: eq(post_id, $post)) {
        post_id
        ~pertenece_a {
          timestamp
          escrito_por { username }
        }
      }
    }
    """
    run_query(client, "3. Hilos de Comentarios (p_001)", q3, {'$post': 'p_001'})

    # Req 4: Motor de Recomendación (Amigos de Amigos)
    q4 = """
    query recommendations($user: string) {
      recomendaciones(func: eq(username, $user)) {
        username
        sigue_a {
          sigue_a @filter(NOT eq(username, $user)) {
            username
            bio
          }
        }
      }
    }
    """
    run_query(client, "4. Motor de Recomendación - 2 Hops (arantxa_af)", q4, {'$user': 'arantxa_af'})

    # Req 5: Detección de Nodos de Influencia (Influencers)
    q5 = """
    {
      influencers(func: has(username)) {
        username
        num_seguidores: count(~sigue_a)
      }
    }
    """
    run_query(client, "5. Detección de Influencers", q5)

    # Req 6: Publicación de Contenido
    q6 = """
    query user_posts($user: string) {
      publicaciones(func: eq(username, $user)) {
        username
        posteo {
          post_id
          content
          timestamp
        }
      }
    }
    """
    run_query(client, "6. Publicación de Contenido (arantxa_af)", q6, {'$user': 'arantxa_af'})

    # Req 7: Rastreo de Propagación (Reposts)
    q7 = """
    query propagation($post: string) {
      rastreo_viralidad(func: eq(post_id, $post)) {
        post_id
        content
        reposteado_por: ~repostea {
          username
        }
        total_reposts: count(~repostea)
      }
    }
    """
    run_query(client, "7. Rastreo de Propagación / Reposts (p_001)", q7, {'$post': 'p_001'})


if __name__ == '__main__':
    print("Initializing Social Media Graph Analytics...")
    
    db_client = get_client()
    set_schema(db_client)
    load_data(db_client)
    execute_all_queries(db_client)