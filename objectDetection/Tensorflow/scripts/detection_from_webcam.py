import object_detection_helper
import cv2

capture = cv2.VideoCapture(0)
while capture.isOpened():
    ret, img = capture.read()

    img_result = object_detection_helper.draw_detections(img)

    cv2.imshow("Detection from webcam", img_result)

    if cv2.waitKey(33) == ord('q'):
        capture.release()

cv2.destroyAllWindows()
