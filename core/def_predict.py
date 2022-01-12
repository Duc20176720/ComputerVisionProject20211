from keras.models import load_model
import numpy as np
from numpy import load, expand_dims
from keras.preprocessing.image import array_to_img, img_to_array
from mtcnn import MTCNN
from sklearn.preprocessing import LabelEncoder
from sklearn.preprocessing import Normalizer
from sklearn.svm import SVC

def get_embedding(model, face_pixels):
    face_pixels = face_pixels.astype('float32')
    mean, std = face_pixels.mean(), face_pixels.std()
    face_pixels = (face_pixels - mean) / std
    samples = np.expand_dims(face_pixels, axis=0)
    yhat = model.predict(samples)
    return yhat[0]
def extract_face(image, required_size=(160, 160)):

    image = array_to_img(image)
    image = image.convert('RGB')        
    pixels = img_to_array(image)
    detector = MTCNN()
    results = detector.detect_faces(pixels)
    if results != []:
        x1, y1, width, height = results[0]['box']
        x1, y1 = abs(x1), abs(y1)
        x2, y2 = x1 + width, y1 + height
        face = pixels[y1:y2, x1:x2]
        image = array_to_img(face)
        image = image.resize(required_size)
        face_array = img_to_array(image)
        return results, face_array
    else:
        return []
def predict(img):
    # model = load_model('facenet_keras.h5')
    model_root = load_model('model/facenet_keras.h5')
    data = load('model/data_team_cv_new.npz')
    trainX, trainy, testX, testy = data['arr_0'], data['arr_1'], data['arr_2'], data['arr_3']
    # normalize input vectors
    in_encoder = Normalizer(norm='l2')
    trainX = in_encoder.transform(trainX)
    testX = in_encoder.transform(testX)
    # label encode targets
    out_encoder = LabelEncoder()
    out_encoder.fit(trainy)
    trainy = out_encoder.transform(trainy)
    testy = out_encoder.transform(testy)
    # fit model
    model = SVC(kernel='linear', probability=True)
    model.fit(trainX, trainy)

    # img = Image.open('test_3.jpg')
    # print(type(img))
    bound, face = extract_face(img)
    embedding_face = get_embedding(model_root, face)


    print('========================RESULT========================')

    #prediction for the face
    samples = expand_dims(embedding_face, axis=0)
    yhat_class = model.predict(samples)
    yhat_prob = model.predict_proba(samples)
    print(yhat_prob)
    #get name
    class_index = yhat_class[0]
    print(yhat_prob[0, class_index])
    class_probability = yhat_prob[0,class_index] * 100
    predict_names = out_encoder.inverse_transform(yhat_class)
    print( 'Predicted: %s (%f)' % (predict_names[0], class_probability))
    if class_probability >= 90:
        return predict_names[0]
    else:
        return "Unknown"


# cap = cv2.VideoCapture(0)
# while(True):
#     ret, frame = cap.read()
#     cv2.imshow('frame', frame)

#     bound, face = extract_face(frame)
#     embedding_face = get_embedding(model_root, face)
#     samples = expand_dims(embedding_face, axis=0)
#     yhat_class = model.predict(samples)
#     predict_names = out_encoder.inverse_transform(yhat_class)
#     print(predict_names[0])

#     if cv2.waitKey(1) & 0xFF == ord('q'):
#         break
# cap.release()
# cv2.destroyAllWindows()
