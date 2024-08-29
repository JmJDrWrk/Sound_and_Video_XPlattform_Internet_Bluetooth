# **Sound and Video**

Este proyecto que ha sido emprendido y desarrollado en unos días atiende a una necesidad, estaba en mi ordenador de torre cuando **de pronto mi headset dejó de funcionar**, no quería comprar unos cascos cualquiera corriendo y quería poder utilizar unos bluetooth que ya tenía. Pero para mi sorpresa, **mi ordenador no trae bluetooth** y AUNQUE se puede comprar una tarjeta o un adaptador, pensé que podría **enviar por sockets de Python el audio a otro dispositivo que si tenga conexión**.

PLATAFORMAS

He probado y adaptado un poco el código de servidor y cliente para poder finalmente tener **soporte para 3 plataformas** siendo el orden servidor -> cliente
`Windows -> Windows` (Esta es la forma más sencilla de conseguir que funcione)
`Windows -> Android` (La más sencilla de usar pero más difícil de solucionar errores)
`Windows -> Raspberry PI 3B` (con archivos.service, definitivamente solo para usuarios de linux, avanzados)

En resumen el funcionamiento del repositorio es sencillo, **en cada rama se encuentra y da soporte a cada forma de conexión**, mi consejo es si tenéis 2 ordenadores utilizar la rama `windows-windows`, pero si no es el caso y tenéis un movil ANDROID, entonces usad `windows-android`.

LO CHUNGO

Para encontrar instrucciones de como proceder en cada caso, debeis ir al repositorio de esa plataforma

