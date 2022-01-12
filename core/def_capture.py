import cv2
import os
import time
def capture_image(cap, name_user):
    # cap = cv2.VideoCapture(0)
    frame_count = 0
    image_count = 0
    dir = ''

    while(image_count < 40):

        ret, frame = cap.read()
        
        if frame_count == 0:

            name = name_user
            dir = os.path.join('register', 'train', name)
            os.mkdir(dir)
            time.sleep(2)
        elif frame_count == 160:
            dir = os.path.join('register', 'test', name)
            os.mkdir(dir)
            time.sleep(2)

        if frame_count % 5 == 0:
            cv2.imwrite(dir+'/'+str(image_count)+'.jpg', frame)
            image_count += 1

        frame_count += 1
    print('done')