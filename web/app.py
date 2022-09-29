from objectDetection.Tensorflow.scripts import object_detection_helper
from flask import Flask, render_template, Response, jsonify, request
import yaml
import io
import cv2
import numpy as np


app = Flask(__name__)

CAPTURE = cv2.VideoCapture(1, cv2.CAP_DSHOW)
CONFIG = {}
CONFIG_COLORS = {}
EVALUATION = []


def load_config():
    global CONFIG, CONFIG_COLORS

    with open("config.yaml", "r") as stream:
        CONFIG = yaml.safe_load(stream)

    if not CONFIG_COLORS and CONFIG_COLORS is not CONFIG.get("detections").get("colors"):
        CONFIG_COLORS = CONFIG.get("detections").get("colors").copy()


def video():
    ret, img = CAPTURE.read()
    while CAPTURE.isOpened():
        # Capture frame-by-frame
        ret, img = CAPTURE.read()
        if ret:
            threshold = CONFIG['detections']['tf']['threshold']
            version = CONFIG['detections']['tf']['version']
            path = "../objectDetection/Tensorflow/workspace/exported-models/detection_v"
            label_colors = CONFIG['detections']['colors']['label']
            liquid_colors = CONFIG['detections']['colors']['liquid']
            detections = object_detection_helper.get_locations_of_detections(img, threshold, version, path,
                                                                             [label_colors.get('hue').get('min'),
                                                                              label_colors.get('sat').get('min'),
                                                                              label_colors.get('val').get('min')],
                                                                             [label_colors.get('hue').get('max'),
                                                                              label_colors.get('sat').get('max'),
                                                                              label_colors.get('val').get('max')],
                                                                             [liquid_colors.get('hue').get('min'),
                                                                              liquid_colors.get('sat').get('min'),
                                                                              liquid_colors.get('val').get('min')],
                                                                             [liquid_colors.get('hue').get('max'),
                                                                              liquid_colors.get('sat').get('max'),
                                                                              liquid_colors.get('val').get('max')],
                                                                             )

            img_result = object_detection_helper.draw_detections(img, detections)

            evaluate_label = CONFIG['detections']['evaluation']['label']
            evaluate_liquid = CONFIG['detections']['evaluation']['liquid']
            debugging_mode = CONFIG['detections']['debugging_mode']
            evaluate(object_detection_helper.evaluate_detection_groups(detections, evaluate_label['deviation'], evaluate_label['height'], evaluate_label['top_position'], evaluate_label['bottom_position'], evaluate_liquid['deviation'], evaluate_liquid['fill'], debugging_mode))

            img = cv2.resize(img_result, (0, 0), fx=0.5, fy=0.5)
            frame = cv2.imencode('.jpg', img)[1].tobytes()
            yield b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n'
        else:
            break


def video_label():
    while CAPTURE.isOpened():
        ret, img = CAPTURE.read()
        if ret:
            reversed_img = 255 - img.copy()
            blurred_img = cv2.GaussianBlur(reversed_img, (31, 31), 0)
            hsv = cv2.cvtColor(blurred_img, cv2.COLOR_BGR2HSV)

            hue = CONFIG_COLORS.get('label').get('hue')
            sat = CONFIG_COLORS.get('label').get('sat')
            val = CONFIG_COLORS.get('label').get('val')

            mask = cv2.inRange(hsv, np.array([hue.get('min'), sat.get('min'), val.get('min')]),
                               np.array([hue.get('max'), sat.get('max'), val.get('max')]))

            result = cv2.bitwise_and(img, img, mask=mask)
            result_frame = cv2.resize(result, (0, 0), fx=0.5, fy=0.5)
            frame = cv2.imencode('.jpg', result_frame)[1].tobytes()
            yield b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n'
        else:
            break


def video_liquid():
    global CONFIG, CONFIG_COLORS

    while CAPTURE.isOpened():
        ret, img = CAPTURE.read()
        if ret:
            reversed_img = 255 - img.copy()
            blurred_img = cv2.GaussianBlur(reversed_img, (31, 31), 0)
            hsv = cv2.cvtColor(blurred_img, cv2.COLOR_BGR2HSV)

            hue = CONFIG_COLORS.get('liquid').get('hue')
            sat = CONFIG_COLORS.get('liquid').get('sat')
            val = CONFIG_COLORS.get('liquid').get('val')

            mask = cv2.inRange(hsv, np.array([hue.get('min'), sat.get('min'), val.get('min')]),
                               np.array([hue.get('max'), sat.get('max'), val.get('max')]))

            result = cv2.bitwise_and(img, img, mask=mask)
            result_frame = cv2.resize(result, (0, 0), fx=0.5, fy=0.5)
            frame = cv2.imencode('.jpg', result_frame)[1].tobytes()
            yield b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n'
        else:
            break


def evaluate(_evaluation_results):
    global EVALUATION

    if EVALUATION is None:
        EVALUATION = _evaluation_results
    else:
        if _evaluation_results != EVALUATION:
            EVALUATION = _evaluation_results


@app.route('/')
def index():
    return render_template("index.html", config=CONFIG, colors=CONFIG_COLORS)


#
# Liquid
#
@app.route('/config/liquid', methods=['POST'])
def liquid_color_detection_configuration():
    global CONFIG, CONFIG_COLORS

    if request.method == "POST":
        data = request.get_json()

        configuration = data.get("configuration")
        is_permanent = data.get("isPermanent", False)

        liquid_colors = {
            'hue': {
                'min': int(configuration.get("hue")[0]),
                'max': int(configuration.get("hue")[1]),
            },
            'sat': {
                'min': int(configuration.get("sat")[0]),
                'max': int(configuration.get("sat")[1]),
            },
            'val': {
                'min': int(configuration.get("val")[0]),
                'max': int(configuration.get("val")[1]),
            }
        }

        if is_permanent:
            CONFIG['detections']['colors']['liquid'] = liquid_colors

            with io.open("config.yaml", "w", encoding="utf-8") as file:
                yaml.dump(CONFIG, file, default_flow_style=False, allow_unicode=True)

            load_config()
        else:
            CONFIG_COLORS['liquid'] = liquid_colors

        return "Moet anders werkt het niet!"


@app.route('/liquid/feed')
def liquid_feed():
    return Response(video_liquid(), mimetype='multipart/x-mixed-replace; boundary=frame')


#
# Label
#
@app.route('/config/label', methods=['POST'])
def label_color_detection_configuration():
    global CONFIG, CONFIG_COLORS

    if request.method == "POST":
        data = request.get_json()

        configuration = data.get("configuration")
        is_permanent = data.get("isPermanent", False)

        label_colors = {
            'hue': {
                'min': int(configuration.get("hue")[0]),
                'max': int(configuration.get("hue")[1]),
            },
            'sat': {
                'min': int(configuration.get("sat")[0]),
                'max': int(configuration.get("sat")[1]),
            },
            'val': {
                'min': int(configuration.get("val")[0]),
                'max': int(configuration.get("val")[1]),
            }
        }

        if is_permanent:
            # Change label colors in config.
            CONFIG['detections']['colors']['label'] = label_colors
            # Save changes to config.
            with io.open("config.yaml", "w", encoding="utf-8") as file:
                yaml.dump(CONFIG, file, default_flow_style=False, allow_unicode=True)

            # Reload config after making changes.
            load_config()
        else:
            # Change label colors for testing
            CONFIG_COLORS['label'] = label_colors

    return "Dit moet anders werkt het op de een of andere manier niet."


@app.route('/config/tensorflow', methods=['POST'])
def tensorflow_detection_configuration():
    global CONFIG

    if request.method == "POST":
        data = request.get_json()

        CONFIG['detections']['tf']['threshold'] = float(data.get("threshold"))

        with io.open("config.yaml", "w", encoding="utf-8") as file:
            yaml.dump(CONFIG, file, default_flow_style=False, allow_unicode=True)

        # Reload config after making changes.
        load_config()

    return "Return anders werkt het niet."


@app.route('/config/evaluation', methods=['POST'])
def evaluation_configuration():
    global CONFIG

    if request.method == "POST":
        data = request.get_json()

        label = data.get("label")
        liquid = data.get("liquid")

        evaluation_config = {
            'label': {
                'deviation': float(label.get("deviation")),
                'height': int(label.get("height")),
                'top_position': int(label.get("top_position")),
                'bottom_position': int(label.get("bottom_position"))
            },
            'liquid': {
                'deviation': float(liquid.get("deviation")),
                'fill': int(liquid.get("fill")),
            }
        }

        CONFIG['detections']['evaluation'] = evaluation_config

        with io.open("config.yaml", "w", encoding="utf-8") as file:
            yaml.dump(CONFIG, file, default_flow_style=False, allow_unicode=True)

        load_config()

    return "Return anders werkt het niet"


#
# Debug mode
#
@app.route('/config/debug',  methods=['POST'])
def debug_mode():
    global CONFIG

    if request.method == "POST":
        data = request.get_json()
        debug_mode = data.get('debug_mode')
        CONFIG['detections']['debugging_mode'] = debug_mode

        with io.open("config.yaml", "w", encoding="utf-8") as file:
            yaml.dump(CONFIG, file, default_flow_style=False, allow_unicode=True)

        load_config()

    return "Return anders werkt het niet"


@app.route('/label/feed')
def label_feed():
    return Response(video_label(), mimetype='multipart/x-mixed-replace; boundary=frame')


#
# Detections feed
#
@app.route('/feed')
def feed():
    return Response(video(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/feed/results')
def feed_results():
    return jsonify(EVALUATION)


if __name__ == "__main__":
    load_config()

    app.run(host="", debug=True, use_reloader=False)
