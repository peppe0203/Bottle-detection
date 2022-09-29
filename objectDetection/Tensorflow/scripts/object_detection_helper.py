import os
from PIL import Image
import tensorflow as tf
from object_detection.utils import config_util
from object_detection.utils import label_map_util
from object_detection.utils import visualization_utils as viz_utils
from object_detection.builders import model_builder
import cv2
import numpy as np

DETECTION_MODEL = None
DETECTION_MODEL_VERSION = None
DETECTION_MODEL_PATH = None


def get_latest_model_version():
    return 4.0


def load_model(_version, _path="../workspace/exported-models/detection_v"):
    global DETECTION_MODEL, DETECTION_MODEL_VERSION, DETECTION_MODEL_PATH

    if DETECTION_MODEL_VERSION is not None and DETECTION_MODEL_VERSION == _version:
        return DETECTION_MODEL_PATH

    configs = config_util.get_configs_from_pipeline_file(f"{_path}{_version}/pipeline.config")
    detection_model = model_builder.build(model_config=configs['model'], is_training=False)

    ckpt = tf.compat.v2.train.Checkpoint(model=detection_model)
    ckpt.restore(os.path.join(f"{_path}{_version}/checkpoint", 'ckpt-0')).expect_partial()

    DETECTION_MODEL = detection_model
    DETECTION_MODEL_VERSION = _version
    DETECTION_MODEL_PATH = f"{_path}{_version}"

    return DETECTION_MODEL_PATH


@tf.function
def detect_fn(_image):
    _image, shapes = DETECTION_MODEL.preprocess(_image)
    prediction_dict = DETECTION_MODEL.predict(_image, shapes)
    detections = DETECTION_MODEL.postprocess(prediction_dict, shapes)

    return detections


def get_locations_of_detections(_image, _threshold=0.25, _model_version=get_latest_model_version(),
                                _model_path="../workspace/exported-models/detection_v", _label_colors_lower=[0, 100, 100],
                                _label_colors_upper=[255, 255, 255], _liquid_colors_lower=[10, 0, 200], _liquid_colors_upper=[160, 30, 255]):
    detections = []

    detections.extend(get_locations_of_bottles(_image, _threshold, _model_version, _model_path))

    detections = group_detections(detections)

    for detection in detections:
        label = get_location_of_label(_image, detection['bottle'], _label_colors_lower, _label_colors_upper)
        if label:
            detection['label'] = label

        liquid = get_location_of_liquid(_image, detection['bottle'], _liquid_colors_lower, _liquid_colors_upper)
        if liquid:
            detection['liquid'] = liquid

    return detections


def get_locations_of_bottles(_image, _threshold, _model_version, _model_path):
    path = load_model(_model_version, _model_path)

    category_index = label_map_util.create_category_index_from_labelmap(f"{path}/../../annotations/label_map.pbtxt")

    image_np = np.array(_image)
    input_tensor = tf.convert_to_tensor(np.expand_dims(image_np, 0), dtype=tf.float32)

    detections = detect_fn(input_tensor)

    num_detections = int(detections.pop('num_detections'))

    detections = {key: value[0, :num_detections].numpy()
                  for key, value in detections.items()}
    detections['num_detections'] = num_detections
    detections['detection_classes'] = detections['detection_classes'].astype(np.int64)

    label_id_offset = 1
    boxes = detections['detection_boxes']
    scores = detections['detection_scores']
    classes = detections['detection_classes'] + label_id_offset

    image_width, image_height = Image.fromarray(np.uint8(image_np)).convert('RGB').size
    detection_boxes = []
    for i in range(len(boxes)):
        if scores[i] >= _threshold:
            y_min, x_min, y_max, x_max = boxes[i]
            detection_boxes.append({
                'name': category_index[classes[i]]['name'].title(),
                'class': category_index[classes[i]]['name'],
                'score': scores[i],
                'coordinates': {
                    '%': {
                        'x_min': x_min,
                        'x_max': x_max,
                        'y_min': y_min,
                        'y_max': y_max
                    },
                    'px': {
                        'x_min': x_min * image_width,
                        'x_max': x_max * image_width,
                        'y_min': y_min * image_height,
                        'y_max': y_max * image_height
                    }
                }
            })

    return detection_boxes


def get_location_of_label(_image, _bottle_location, _lower, _upper):
    coordinates = _bottle_location['coordinates']['px']

    image_np = np.array(_image)
    image_np = 255 - image_np

    mask = np.zeros_like(image_np.copy())

    bottle_cut_out = cv2.rectangle(mask, (int(coordinates['x_max']), int(coordinates['y_min'])),
                                   (int(coordinates['x_min']), int(coordinates['y_max'])), (255, 255, 255), -1)

    bottle_cut_out_img = cv2.bitwise_and(image_np, bottle_cut_out)
    blurred_bottle_cut_out_img = cv2.GaussianBlur(bottle_cut_out_img, (31, 31), 0)
    hsv_blurred_bottle_cut_out_img = cv2.cvtColor(blurred_bottle_cut_out_img, cv2.COLOR_BGR2HSV)

    mask_img = cv2.inRange(hsv_blurred_bottle_cut_out_img, np.array(_lower), np.array(_upper))

    label_cut_out_img = cv2.bitwise_and(image_np, hsv_blurred_bottle_cut_out_img, mask=mask_img)

    ret, thresh = cv2.threshold(mask_img, 40, 255, 0)
    contours, hierarchy = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

    if len(contours) > 0:
        cv2.drawContours(label_cut_out_img, contours, -1, 255, 3)

        biggest_contour = max(contours, key=cv2.contourArea)
        x, y, width, height = cv2.boundingRect(biggest_contour)
        image_width, image_height = Image.fromarray(np.uint8(image_np)).convert('RGB').size

        width_of_bottle = _bottle_location['coordinates']['px']['x_max'] - _bottle_location['coordinates']['px']['x_min']
        if width >= width_of_bottle * 0.5:
            return {
                'name': 'Label',
                'class': 'label',
                'score': .99,
                'coordinates': {
                    '%': {
                        'x_min': x / image_width,
                        'x_max': (x + width) / image_width,
                        'y_min': y / image_height,
                        'y_max': (y + height) / image_height
                    },
                    'px': {
                        'x_min': x,
                        'x_max': x + width,
                        'y_min': y,
                        'y_max': y + height
                    }
                }
            }

    return None


def get_location_of_liquid(_image, _bottle_location, _lower, _upper):
    coordinates = _bottle_location['coordinates']['px']

    image_np = np.array(_image)

    image_np = 255 - image_np

    mask = np.zeros_like(image_np.copy())

    bottle_cut_out = cv2.rectangle(mask, (int(coordinates['x_max']), int(coordinates['y_min'])),
                                   (int(coordinates['x_min']), int(coordinates['y_max'])), (255, 255, 255), -1)

    bottle_cut_out_img = cv2.bitwise_and(image_np, bottle_cut_out)
    blurred_bottle_cut_out_img = cv2.GaussianBlur(bottle_cut_out_img, (31, 31), 0)

    hsv_bottle_cut_out_img = cv2.cvtColor(blurred_bottle_cut_out_img, cv2.COLOR_BGR2HSV)

    mask_img = cv2.inRange(hsv_bottle_cut_out_img, np.array(_lower), np.array(_upper))

    liquid_cut_out_img = cv2.bitwise_and(image_np, hsv_bottle_cut_out_img, mask=mask_img)

    ret, thresh = cv2.threshold(mask_img, 40, 255, 0)
    contours, hierarchy = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

    if len(contours) > 0 and contours is not None:
        cv2.drawContours(liquid_cut_out_img, contours, -1, 255, 3)
        liquid_contours = []

        contours_new = contours.copy()
        for i in range(2):
            biggest_contour = max(contours_new, key=cv2.contourArea)
            x, y, width, height = cv2.boundingRect(biggest_contour)

            width_of_bottle = _bottle_location['coordinates']['px']['x_max'] - _bottle_location['coordinates']['px']['x_min']

            if width >= width_of_bottle * 0.3:
                liquid_contours.append({
                    'x_min': x,
                    'x_max': x + width,
                    'y_min': y,
                    'y_max': y + height
                })

            contours_new = [i for i in contours_new if not np.array_equal(i, biggest_contour)]

            if len(contours_new) == 0:
                break

        result = {}
        for contour in liquid_contours:
            if result.get('x_min', contour['x_min'] + 1) > contour['x_min']:
                result['x_min'] = contour['x_min']

            if result.get('x_max', contour['x_max'] - 1) < contour['x_max']:
                result['x_max'] = contour['x_max']

            if result.get('y_min', contour['y_min'] + 1) > contour['y_min']:
                result['y_min'] = contour['y_min']

            if result.get('y_max', contour['y_max'] - 1) < contour['y_max']:
                result['y_max'] = contour['y_max']

        image_width, image_height = Image.fromarray(np.uint8(image_np)).convert('RGB').size
        if len(result) > 0:
            return {
                'name': 'Liquid',
                'class': 'liquid',
                'score': .99,
                'coordinates': {
                    '%': {
                        'x_min': result['x_min'] / image_width,
                        'x_max': result['x_max'] / image_width,
                        'y_min': result['y_min'] / image_height,
                        'y_max': result['y_max'] / image_height
                    },
                    'px': {
                        'x_min': result['x_min'],
                        'x_max': result['x_max'],
                        'y_min': result['y_min'],
                        'y_max': result['y_max']
                    }
                }
            }
    return None


def group_detections(_detections):
    grouped_detections = []

    bottles = (detection for detection in _detections if detection['class'] == 'bottle')
    amount_of_bottles = 0
    for bottle in bottles:
        group = {
            'bottle': bottle
        }

        group['bottle']['name'] = f"Bottle #{amount_of_bottles + 1}"

        grouped_detections.append(group)

        amount_of_bottles += 1

    not_bottles = (detection for detection in _detections if detection['class'] != 'bottle')
    for detection in not_bottles:
        for group_detection in grouped_detections:
            detection_location = detection['coordinates']['%']
            bottle_location = group_detection['bottle']['coordinates']['%']

            if detection_location['x_min'] >= bottle_location['x_min'] \
                    and detection_location['x_max'] <= bottle_location['x_max']:
                if detection_location['y_min'] >= bottle_location['y_min'] \
                        and detection_location['y_max'] <= bottle_location['y_max']:
                    group_detection[detection['class']] = detection

    return grouped_detections


def draw_detections(_image, _detections=None):
    if _detections is None:
        _detections = get_locations_of_detections(_image)
    elif not _detections:
        return _image

    image_with_detections = np.array(_image)

    detection_colors = {
        'liquid': "PaleGoldenRod",
        'bottle': "LightSalmon",
        'label': "Azure"
    }

    for detection_group in _detections:
        for detection in detection_group:
            if detection_group[detection]:
                coordinates = detection_group[detection]['coordinates']['%']

                viz_utils.draw_bounding_box_on_image_array(image_with_detections, coordinates['y_min'],
                                                           coordinates['x_min'],
                                                           coordinates['y_max'], coordinates['x_max'],
                                                           display_str_list=[detection_group[detection]['name']],
                                                           color=detection_colors[detection_group[detection]['class']])

    return image_with_detections


def evaluate_detection_groups(_detection_groups, _label_deviation=.05, _label_height=20, _label_top_position=70, _label_bottom_position=40, _liquid_deviation=.05, _liquid_fill=70, _is_debugging=False):
    results = []

    for detection_group in _detection_groups:
        bottle = detection_group['bottle']

        result = {}
        not_bottles = (detection for detection in detection_group if detection is not 'bottle')
        for detection in not_bottles:
            if detection == 'label':
                correct = False

                height_bottle = bottle['coordinates']['px']['y_max'] - bottle['coordinates']['px']['y_min']
                height_label = detection_group[detection]['coordinates']['px']['y_max'] - detection_group[detection]['coordinates']['px']['y_min']

                height_label_compared_to_bottle = round((height_label / height_bottle) * 100, 1)
                label_from_top = round(((detection_group[detection]['coordinates']['px']['y_min'] - bottle['coordinates']['px']['y_min']) / height_bottle) * 100, 1)
                label_from_bottom = round(((bottle['coordinates']['px']['y_max'] - detection_group[detection]['coordinates']['px']['y_max']) / height_bottle) * 100, 1)

                if (_label_height - (_label_height * _label_deviation)) <= height_label_compared_to_bottle <= (_label_height + (_label_height * _label_deviation)):
                    if (_label_top_position - (_label_top_position * _label_deviation)) <= label_from_top <= (_label_top_position + (_label_top_position * _label_deviation)):
                        if (_label_bottom_position - (_label_bottom_position * _label_deviation)) <= label_from_bottom <= (_label_bottom_position + (_label_bottom_position * _label_deviation)):
                            correct = True

                if correct:
                    result[detection] = "Correct"
                else:
                    result[detection] = "Incorrect"

                    if _is_debugging:
                        result[detection] += f"  (H: {height_label_compared_to_bottle}, T: {label_from_top}, B: {label_from_bottom})"

            elif detection == 'liquid':
                height_bottle = bottle['coordinates']['px']['y_max'] - bottle['coordinates']['px']['y_min']
                height_liquid = detection_group[detection]['coordinates']['px']['y_max'] - detection_group[detection]['coordinates']['px']['y_min']

                volume = round((height_liquid / height_bottle) * 100, 1)

                if (_liquid_fill - (_liquid_fill * _liquid_deviation)) <= volume <= (_liquid_fill + (_liquid_fill * _liquid_deviation)):
                    result[detection] = "Correct"
                elif volume > (_liquid_fill + (_liquid_fill * _liquid_deviation)):
                    result[detection] = "Too full"

                    if _is_debugging:
                        result[detection] += f" ({volume}%)"
                else:
                    result[detection] = "Too little"

                    if _is_debugging:
                        result[detection] += f" ({volume}%)"
            else:
                raise Exception(f"Cannot evaluate {detection['class']}.")

        if "label" not in result:
            result["label"] = "Not detected"
        if "liquid" not in result:
            result["liquid"] = "Not detected"

        results.append({
            'bottle': bottle['name'],
            'results': result
        })

    return results


if __name__ == "__main__":
    print("You are not able to run this file directly, use it as a helper for getting detections.")
