import cv2
import utiles  # Se importa un módulo personalizado llamado 'utiles'
from flask import Flask, render_template, Response, jsonify  # Se importan clases y funciones de Flask

app = Flask(__name__)

# Se crea un objeto de VideoCapture para acceder a la cámara. Puede ser una cámara física o una transmisión en vivo (en este caso, mediante RTSP)
camara = cv2.VideoCapture("rtsp://192.168.1.3:554/user=admin&password=GadnicSX37&channel=1&stream=0.sdp?")

# Configuraciones de vídeo
FRAMES_VIDEO = 20.0  # Número de frames por segundo
RESOLUCION_VIDEO = (640, 480)  # Resolución del video
UBICACION_FECHA_HORA = (0, 15)  # Posición para la marca de agua de fecha y hora en los frames
FUENTE_FECHA_Y_HORA = cv2.FONT_HERSHEY_PLAIN  # Tipo de fuente para la fecha y hora
ESCALA_FUENTE = 1  # Escala de la fuente
COLOR_FECHA_HORA = (255, 255, 255)  # Color de la fecha y hora (blanco)
GROSOR_TEXTO = 1  # Grosor del texto
TIPO_LINEA_TEXTO = cv2.LINE_AA  # Tipo de línea para el texto
fourcc = cv2.VideoWriter_fourcc(*'XVID')  # Formato de codificación de video XVID
archivo_video = None  # Objeto de VideoWriter para escribir el video
grabando = False  # Bandera para indicar si se está grabando o no

# Función para agregar la fecha y hora a un frame
def agregar_fecha_hora_frame(frame):
    cv2.putText(frame, utiles.fecha_y_hora(), UBICACION_FECHA_HORA, FUENTE_FECHA_Y_HORA,
                ESCALA_FUENTE, COLOR_FECHA_HORA, GROSOR_TEXTO, TIPO_LINEA_TEXTO)

# Generador de frames para transmitir la cámara en tiempo real
def generador_frames():
    while True:
        ok, imagen = obtener_frame_camara()
        if not ok:
            break
        else:
            # Retornar la imagen en modo de respuesta HTTP
            yield b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + imagen + b"\r\n"

# Función para obtener un frame de la cámara
def obtener_frame_camara():
    ok, frame = camara.read()
    if not ok:
        return False, None
    agregar_fecha_hora_frame(frame)
    # Escribir en el video en caso de que se esté grabando
    if grabando and archivo_video is not None:
        archivo_video.write(frame)
    # Codificar la imagen como JPG
    _, bufer = cv2.imencode(".jpg", frame)
    imagen = bufer.tobytes()
    return True, imagen

# Ruta para el streaming de la cámara
@app.route("/streaming_camara")
def streaming_camara():
    return Response(generador_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

# Ruta para descargar una foto tomada desde la cámara
@app.route("/tomar_foto_descargar")
def descargar_foto():
    ok, frame = obtener_frame_camara()
    if not ok:
        abort(500)
        return
    respuesta = Response(frame)
    respuesta.headers["Content-Type"] = "image/jpeg"
    respuesta.headers["Content-Transfer-Encoding"] = "Binary"
    respuesta.headers["Content-Disposition"] = "attachment; filename=\"foto.jpg\""
    return respuesta

# Ruta para guardar una foto tomada desde la cámara
@app.route("/tomar_foto_guardar")
def guardar_foto():
    nombre_foto = utiles.obtener_uuid() + ".jpg"
    ok, frame = camara.read()
    if ok:
        agregar_fecha_hora_frame(frame)
        cv2.imwrite(nombre_foto, frame)
    return jsonify({
        "ok": ok,
        "nombre_foto": nombre_foto,
    })

# Ruta principal, sirve el archivo index.html
@app.route('/')
def index():
    return render_template("/camaras.html")

# Ruta para comenzar la grabación de video

@app.route('/views/login.html')
def login():
    return render_template("/login.html")

@app.route('/views/register.html')
def register():
    return render_template("/register.html")

@app.route("/comenzar_grabacion")
def comenzar_grabacion():
    global grabando
    global archivo_video
    if grabando and archivo_video:
        return jsonify(False)
    nombre = utiles.fecha_y_hora_para_nombre_archivo() + ".avi"
    archivo_video = cv2.VideoWriter(
        nombre, fourcc, FRAMES_VIDEO, RESOLUCION_VIDEO)
    grabando = True
    return jsonify(True)

# Ruta para detener la grabación de video
@app.route("/detener_grabacion")
def detener_grabacion():
    global grabando
    global archivo_video
    if not grabando or not archivo_video:
        return jsonify(False)
    grabando = False
    archivo_video.release()
    archivo_video = None
    return jsonify(True)

# Ruta para obtener el estado de la grabación (si se está grabando o no)
@app.route("/estado_grabacion")
def estado_grabacion():
    return jsonify(grabando)

# Ejecutar la aplicación Flask en modo de depuración en el host 0.0.0.0
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")


app = Flask(__name__, static_folder="static")