import pydgraph

def get_client():
    client_stub = pydgraph.DgraphClientStub('localhost:9080')
    return pydgraph.DgraphClient(client_stub)

def set_schema(client):
    # Strict schema following exact attributes + edge relations
    schema = """
    username: string @index(exact) .
    email: string @index(exact) .
    password: string .
    bio: string .
    interests: string .
    
    post_id: string @index(exact) .
    content: string .
    hashtags: string .
    timestamp: dateTime .
    
    sigue_a: [uid] @reverse .
    dio_like: [uid] @reverse .
    posteo: [uid] @reverse .
    repostea: [uid] @reverse .
    escrito_por: uid @reverse .
    pertenece_a: uid @reverse .

    type Usuario {
        username
        email
        password
        bio
        interests
        sigue_a
        dio_like
        posteo
        repostea
    }

    type Post {
        post_id
        content
        hashtags
        timestamp
    }

    type Comentario {
        timestamp
        escrito_por
        pertenece_a
    }
    """
    op = pydgraph.Operation(schema=schema)
    client.alter(op)
    print("✅ Schema defined successfully with required attributes.")