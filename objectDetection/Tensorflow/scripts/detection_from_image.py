import object_detection_helper
import cv2


img = cv2.imread("../workspace/images/test/Bottle_54.png")

detections = object_detection_helper.get_locations_of_detections(img, _model_version=3.0)

result_image = object_detection_helper.draw_detections(img, detections)

cv2.imshow('Detection from image', result_image)

cv2.waitKey(0)
cv2.destroyAllWindows()
