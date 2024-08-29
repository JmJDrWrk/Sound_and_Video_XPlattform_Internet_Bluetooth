# [Spanish]

Esta utilidad permite bien por medio de python para sistemas que no sean WINDOWS o por ficheros ejecutables exe, hacer un envío de la pantalla con la menor latencia posible.


Se compone de los siguientes socketServers

**videoServer** es encargado de lanzar la imagen al cliente

**videoMouseServer** es encargado de ESCUCHAR al cliente para poder refrescar la posicion del raton o recrear la interacción por teclado del usuario

**audioServerv2** es el encargado de enviar el audio segun de que dispositivo etc

**serverRunv2** Se encarga de lanzar el servidor de audio a la vez que escucha por otro socket udp ordenes para poder relanzar el script y poder desde el cliente actualizar el config.ini

El config ini es un fichero que envíe el cliente al ejecutar ClientAudiov2,
el usuario a ese lado de la conexion puede cambiar libremente ese fichero ya que es el que indica al servidor que puertos e ips utilzar para la transmision de audio y video.

En el lado del cliente se pueden ejecutar los 2 scripts por separado o solo 1 de ellos en función del interés.


# EJECUTAR

Yo recomiendo tener instalado VCABLE como salida virtual, podeis probar a utilizar cualquier otro dispositivo.

en el fichero de configuracion del cliente, uno de los parametros en deviceIndex, este le indica al servidor que dispositivo debe de usar de la lista de dispositivos de audio.

El cliente cada vez que intenta conectarse, SIEMPRE QUE EL SERVIDOR ESTE DEBIDAMENTE LEVANTADO, recive la lista de dispositivos de audio admitidos , su nombre y la cantidad máxima de canales que soporta.

Lo normal es que con vcable instalado y reemplazando en el config.ini del cliente deviceautotarget=CABLE Output automaticamente el cliente identifique el dispositivo. recomiendo dejar el numero de canales y demás parametros por defecto a no ser que se tenga un entendimiento mayor de su funcionamiento e implicaciones.
 

