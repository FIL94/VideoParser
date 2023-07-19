import cv2
import os
import sys
import numpy as np
from tqdm import tqdm


def read_init_path():
    print("Введите полный путь к видеофайлам:")
    path = input()
    if path == "ВЫХОД":
        sys.exit()
    if path == '' or not os.path.exists(path):
        print("Указанн пустой или неверный путь!")
        return None
    else:
        return path


def read_dest_path():
    print("Введите путь для сохранения кадров:")
    path = input()
    if path == "ВЫХОД":
        sys.exit()
    if path == '':
        return path
    else:
        if os.path.exists(path):
            print("Указанная папка уже существует.")
            return path
        else:
            try:
                os.mkdir(path)
                print("Папка создана.")
                return path
            except:
                print("Указан недопустимый путь!")
                return None

def read_fps():
    print("Введите кратность записи кадров (по умолчанию = 1):")
    fps = input()
    if fps == "ВЫХОД":
        sys.exit()
    if fps == '':
        return 1
    else:
        try:
            return int(fps)
        except ValueError:
            print("Неверный формат кратности! Требуется ввести целое число.")
            return None


def read_resolution():
    print("Введите требуемое разрешение (по умолчанию равно наибольшему размеру кадра):")
    resolution = input()
    if resolution == "ВЫХОД":
        sys.exit()
    if resolution == '':
        return 0
    else:
        try:
            return int(resolution)
        except ValueError:
            print("Неверный формат разрешения! Требуется ввести одно целое число.")
            return None


def main():
    init_path = read_init_path()
    while init_path is None:
        init_path = read_init_path()
    print("Выбран путь к файлам:  " + init_path)
    print('')

    dest_path = read_dest_path()
    while dest_path is None:
        dest_path = read_dest_path()
    if dest_path == '':
        dest_path = init_path
    print("Выбран путь для сохранения:  " + dest_path)
    print('')

    fps = read_fps()
    while fps is None:
        fps = read_fps()
    if fps == 1:
        print("Выбран режим сохранения всех кадров.")
        print('')
    elif fps < 1:
        fps = 1
        print("Выбран режим сохранения всех кадров.")
        print('')
    else:
        print("Выбран режим сохранения каждых " + str(fps) + " кадров.")
        print('')

    resolution = read_resolution()
    while resolution is None:
        resolution = read_resolution()
    if resolution == 0:
        print("Выбрано сохранение кадров с разрешением по умолчанию.")
        print('')
    else:
        print("Выбрано разрешение: " + str(resolution) + "x" + str(resolution))
        print('')

    files = os.listdir(init_path)
    videos_list = []
    for file in files:
        if file.endswith(('.mp4', '.avi')):
            videos_list.append(file)
    if len(videos_list) == 0:
        print("В выбранной папке нет видеофалов! Введите правильный путь.")
        main()
    else:
        print("Найдено " + str(len(videos_list)) + " файлов.")
        print("Начало обработки.")
        for video in videos_list:
            cap = cv2.VideoCapture(os.path.join(init_path, video))
            video = os.path.splitext(video)[0]
            if not os.path.exists(os.path.join(dest_path, video)):
                os.mkdir(os.path.join(dest_path, video))

            for count in tqdm(range(int(cap.get(cv2.CAP_PROP_FRAME_COUNT)))):
                _, frame = cap.read()
                if fps == 1:
                    if frame.shape[0] > frame.shape[1]:
                        delay = (frame.shape[0] - frame.shape[1]) / 2
                        leftLine = frame[:, 0, :]
                        leftLine = leftLine[:, np.newaxis, :]
                        leftField = np.repeat(leftLine, delay, 1)
                        rightLine = frame[:, -1, :]
                        rightLine = rightLine[:, np.newaxis, :]
                        rightField = np.repeat(rightLine, delay, 1)
                        image = np.concatenate([leftField, frame, rightField], 1)
                    elif frame.shape[0] < frame.shape[1]:
                        delay = (frame.shape[1] - frame.shape[2]) / 2
                        upperLine = frame[0, :, :]
                        upperLine = upperLine[np.newaxis, :, :]
                        upperField = np.repeat(upperLine, delay, 0)
                        lowerLine = frame[-1, :, :]
                        lowerLine = lowerLine[np.newaxis, :, :]
                        lowerField = np.repeat(lowerLine, delay, 0)
                        image = np.concatenate([upperField, frame, lowerField], 0)
                    else:
                        image = frame

                    if resolution != 0:
                        image = cv2.resize(image, (resolution, resolution))

                    cv2.imwrite(os.path.join(dest_path, video, r"{:0>5}.jpg".format(count)), image)
                else:
                    if count % fps == 0:
                        if frame.shape[0] > frame.shape[1]:
                            delay = (frame.shape[0] - frame.shape[1]) / 2
                            leftLine = frame[:, 0, :]
                            leftLine = leftLine[:, np.newaxis, :]
                            leftField = np.repeat(leftLine, delay, 1)
                            rightLine = frame[:, -1, :]
                            rightLine = rightLine[:, np.newaxis, :]
                            rightField = np.repeat(rightLine, delay, 1)
                            image = np.concatenate([leftField, frame, rightField], 1)
                        elif frame.shape[0] < frame.shape[1]:
                            delay = (frame.shape[1] - frame.shape[2]) / 2
                            upperLine = frame[0, :, :]
                            upperLine = upperLine[np.newaxis, :, :]
                            upperField = np.repeat(upperLine, delay, 0)
                            lowerLine = frame[-1, :, :]
                            lowerLine = lowerLine[np.newaxis, :, :]
                            lowerField = np.repeat(lowerLine, delay, 0)
                            image = np.concatenate([upperField, frame, lowerField], 0)
                        else:
                            image = frame

                        if resolution != 0:
                            image = cv2.resize(image, (resolution, resolution))

                        cv2.imwrite(os.path.join(dest_path, video, r"{:0>5}.jpg".format(count)), image)

            print('Файл ' + video + ' обработан.')

    print('\nОбработка завершена!!!\n')



if __name__ == '__main__':
    while True:
        main()
