from os import listdir
from os.path import isdir
from PIL import Image
from numpy import savez_compressed, expand_dims, load
from keras.preprocessing.image import img_to_array, array_to_img
from mtcnn import MTCNN
import numpy as np
from keras.models import load_model


def extract_face(filename, required_size=(160, 160)):
    image = Image.open(filename)
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
        return face_array
    else:
        return []

def load_faces(directory):
    faces = list()
    for filename in listdir(directory):
        path = directory + filename
        print(path)
        face = extract_face(path)
        if face != []:
            faces.append(face)
    return faces

def load_dataset(directory):
    X, y = list(), list()
    for subdir in listdir(directory):
        path = directory + subdir + '/'
        print(path)
        if not isdir(path):
            continue
        faces = load_faces(path)
        labels = [subdir for _ in range(len(faces))]
        print( '>loaded %d examples for class: %s' % (len(faces), subdir))
        X.extend(faces)
        y.extend(labels)
    return np.array(X), np.array(y)

def get_embedding(model, face_pixels):
    face_pixels = face_pixels.astype('float32')
    mean, std = face_pixels.mean(), face_pixels.std()
    face_pixels = (face_pixels - mean) / std
    samples = expand_dims(face_pixels, axis=0)
    yhat = model.predict(samples)
    return yhat[0]

def append_data(path):
    data = load('model/data_team_cv_new.npz', allow_pickle= True)
    origin_trainX, origin_trainy, origin_testX, origin_testy = data[ 'arr_0' ], data[ 'arr_1'], data[ 'arr_2'], data[ 'arr_3' ]

    trainX, trainy = load_dataset(path+'train/')
    testX, testy = load_dataset(path+'test/')
    model = load_model('model/facenet_keras.h5')
    newTrainX = []
    for face_pixels in trainX:
        embedding = get_embedding(model, face_pixels)
        newTrainX.append(embedding)
    concat_trainX = np.concatenate((origin_trainX, newTrainX))
    concat_trainy = np.concatenate((origin_trainy, trainy))
    newTestX = []
    for face_pixels in testX:
        embedding = get_embedding(model, face_pixels)
        newTestX.append(embedding)
    concat_testX = np.concatenate((origin_testX, newTestX))
    concat_testy = np.concatenate((origin_testy, testy))
    savez_compressed('model/data_team_cv_new.npz', concat_trainX, concat_trainy, concat_testX, concat_testy)

# trainX, trainy = load_dataset('register/train/')
# testX, testy = load_dataset('register/test/')
# print( 'Loaded: ' , trainX.shape, trainy.shape, testX.shape, testy.shape)
# print(trainX.dtype)
# append_data('register/')