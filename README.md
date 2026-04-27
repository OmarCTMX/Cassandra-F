# Cassandra-F

-Omar Ramirez Arenas 738049
-Arantxa Angulo Flores 751976
-Cesar Adrian Santos Santacruz 750578

# Descripcion del proyecto

Es una herramienta que analiza datos de una red social. Guarda usuarios y publicaciones, y usa diferentes bases de datos para manejar información, interacciones y relaciones. Con eso se pueden detectar tendencias y entender cómo interactúan los usuarios.

Para nuestra "Herramienta de Analítica para Redes Sociales", Dgraph es la pieza clave para entender cómo interactúan los usuarios. Mientras MongoDB guarda los perfiles y Cassandra los logs inmutables, Dgraph nos permitirá ejecutar consultas de recorrido profundo (deep traversal) para identificar influencers, clústeres de comunidades y la viralidad del contenido, tareas en las que un modelo de grafos supera ampliamente en rendimiento a otros modelos.


# Flujo de trabajo

Cassandra actúa como la capa de eventos en tiempo real — cada like, follow, sesión o cambio de cuenta se escribe ahí primero por su velocidad de escritura masiva. 

MongoDB almacena los documentos base del sistema: el perfil del usuario, las publicaciones, stories y reels con todos sus metadatos, siendo la fuente de verdad que se lee cuando se carga cualquier pantalla.

DGraph maneja exclusivamente las relaciones entre entidades — quién sigue a quién, qué contenido le gustó a quién, cómo se propagó una publicación — y es el motor que alimenta el feed y las recomendaciones.

Las tres bases se conectan mediante UUIDs compartidos: cuando un usuario da like,Cassandra registra el evento y actualiza el counter, DGraph crea la arista entre usuario y publicación, y MongoDB no se toca — sus documentos se mantienen limpios de contadores para evitar contención en escrituras concurrentes. El resultado es una arquitectura donde cada base hace únicamente lo que hace mejor, sin duplicar responsabilidades.

