# Configuración de MySQL para Tech Solutions

## 1. Instalación de MySQL

1. Descarga MySQL Community Server desde la página oficial:
   - Visita: https://dev.mysql.com/downloads/mysql/
   - Descarga la versión para Windows
   - Elige "MySQL Installer for Windows"

2. Durante la instalación:
   - Selecciona "Developer Default" o "Server only"
   - En la configuración del servidor:
     - Asegúrate de que el puerto sea 3306 (el predeterminado)
     - Establece una contraseña segura para el usuario root
     - **IMPORTANTE**: Guarda esta contraseña, la necesitarás más adelante

## 2. Verificar la instalación

1. Abre el Panel de Control de Windows
2. Busca "Servicios" y ábrelo
3. Busca el servicio "MySQL80" o similar
4. Asegúrate de que esté en estado "En ejecución"
5. Si no está en ejecución, haz clic derecho y selecciona "Iniciar"

## 3. Configurar el archivo .env

Una vez que MySQL esté instalado y funcionando, actualiza el archivo .env con la contraseña correcta que estableciste durante la instalación.

## 4. Crear la base de datos

1. Abre MySQL Workbench (instalado con MySQL)
2. Conéctate con el usuario root y la contraseña que estableciste
3. Copia y ejecuta el contenido del archivo `init_database.sql`

## 5. Verificar la conexión

Una vez completados todos los pasos anteriores, intenta ejecutar el programa nuevamente. Si sigues teniendo problemas, verifica:

1. Que el servicio de MySQL esté en ejecución
2. Que la contraseña en el archivo .env coincida con la que estableciste
3. Que el usuario root tenga permisos para conectarse desde localhost

## Solución de problemas comunes

1. Error "Access denied for user 'root'":
   - Verifica que la contraseña en .env sea correcta
   - Asegúrate de que el usuario tenga permisos para conectarse desde localhost

2. Error "Can't connect to MySQL server":
   - Verifica que el servicio de MySQL esté en ejecución
   - Confirma que el puerto 3306 esté disponible y no bloqueado por el firewall

3. Error "Database does not exist":
   - Asegúrate de haber ejecutado el script init_database.sql
   - Verifica que el nombre de la base de datos en .env coincida con el creado