
# [Spanish]

  

Esta utilidad permite bien por medio de Python para sistemas que no sean WINDOWS o por ficheros ejecutables exe, hacer un envío de la pantalla con la menor latencia posible.

  
  

Se compone de los siguientes socketServers

  

**videoServer** es encargado de lanzar la imagen al cliente

  

**videoMouseServer** es encargado de ESCUCHAR al cliente para poder refrescar la posición del ratón o recrear la interacción por teclado del usuario

  

**audioServerv2** es el encargado de enviar el audio según de que dispositivo etc

  

**serverRunv2** Se encarga de lanzar el servidor de audio a la vez que escucha por otro socket udp ordenes para poder relanzar el script y poder desde el cliente actualizar el config.ini

  

El config.ini es un fichero que envíe el cliente al ejecutar ClientAudiov2,

el usuario a ese lado de la conexión puede cambiar libremente ese fichero ya que es el que indica al servidor que puertos e ips utilzar para la transmisión de audio y video.

  

En el lado del cliente se pueden ejecutar los 2 scripts por separado o solo 1 de ellos en función del interés.

  
  

# EJECUTAR

  

Yo recomiendo tener instalado VCABLE como salida virtual, podéis probar a utilizar cualquier otro dispositivo.

  

~~En el fichero de configuración del cliente, uno de los parámetros en deviceIndex, este le indica al servidor que dispositivo debe de usar de la lista de dispositivos de audio.~~

  

El cliente cada vez que intenta conectarse, SIEMPRE QUE EL SERVIDOR ESTE DEBIDAMENTE LEVANTADO, recibe la lista de dispositivos de audio admitidos , su nombre y la cantidad máxima de canales que soporta.

  

~~Lo normal es que con vcable instalado y reemplazando en el config.ini del cliente deviceautotarget=CABLE Output automaticamente el cliente identifique el dispositivo. recomiendo dejar el numero de canales y demás parametros por defecto a no ser que se tenga un entendimiento mayor de su funcionamiento e implicaciones.~~

Todavía no se soporta configuración en el dispositivo Android, y estamos trabajando para unificar el código en un único código de servidor multiplataforma, pero para eso habrá en cada rama una versión especifica primero y luego se hará un código que englobe todas las ideas que surjan de las necesidades de cada desarrollo concreto.