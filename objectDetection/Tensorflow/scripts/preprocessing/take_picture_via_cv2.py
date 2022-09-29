from cv2 import cv2

cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)
# video capture source camera (Here webcam of laptop)

i = 91
while True:
    ret, frame = cap.read()
    # display the captured image
    cv2.imshow('img1', frame)

    # save on pressing 's'
    if cv2.waitKey(1) & 0xFF == ord('s'):
        cv2.imwrite('../../workspace/images/new/Bottle_' + str(i) + '.png', frame)
        cv2.destroyAllWindows()
        i += 1

    elif cv2.waitKey(1) & 0xFF == ord('q'):
        cap.release()