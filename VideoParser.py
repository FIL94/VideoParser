import cv2
import os
import sys
import numpy as np
from PIL import Image
from tqdm import tqdm
from random import shuffle


def read_task(flag: bool = True):
    if flag:
        print('\n МЕНЮ')
        print('Выберите задачу:')
        print('1. Раскадровка видео')
        print('2. Переформатирование изображений')
        print('3. Загрузка файлов из S3')
    print('Ваш выбор:')
    ans = input()
    if ans == "ВЫХОД":
        sys.exit()
    elif ans == '':
        print('Не указана задача. Введите номер задачи из списка.')
        return None
    elif ans in ['1', '2', '3']:
        return int(ans)
    else:
        print('Неверно указана задача. Введите номер задачи из списка.')
        return None


def read_init_path():
    print("Введите полный путь к файлам:")
    path = input()
    if path == "ВЫХОД":
        sys.exit()
    if path == '' or not os.path.exists(path):
        print("Указанн пустой или неверный путь!")
        return None
    else:
        return path


def read_dest_path():
    print("Введите путь для сохранения результатов:")
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
    print("Введите требуемое разрешение (по умолчанию равно наибольшему размеру изображения):")
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


def video_parsing_task():
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

    resolution = read_resolution()
    while resolution is None:
        resolution = read_resolution()
    if resolution == 0:
        print("Выбрано сохранение изображений с разрешением по умолчанию.")
        print('')
    else:
        print("Выбрано разрешение: " + str(resolution) + "x" + str(resolution))
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

    perform_video(init_path, dest_path, fps, resolution)


def images_reformating_task():
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

    resolution = read_resolution()
    while resolution is None:
        resolution = read_resolution()
    if resolution == 0:
        print("Выбрано сохранение изображений с разрешением по умолчанию.")
        print('')
    else:
        print("Выбрано разрешение: " + str(resolution) + "x" + str(resolution))
        print('')

    if dest_path == init_path:
        if resolution > 0:
            dest_path = dest_path + " ({0}x{1})".format(resolution, resolution)
        else:
            dest_path = dest_path + " (исх.разр.)"
        os.mkdir(dest_path)
    perform_image(init_path, dest_path, resolution)


def files_downloading():
    from minio import Minio
    try:
        client = Minio("s3-nn.ext.odtn.ru", "nnn", "SvK5eZaB6")
        print("Соединение с сервером установлено.")
        print('')
    except:
        print("Не удалось поключиться к хранилищу. Проверьте подключение к Интернету.")
        return

    buckets = list(client.list_buckets())
    selected_bucket = None
    selected_list = None
    while selected_bucket is None:
        print("Выберите папку:")
        for i, bucket in enumerate(buckets):
            print(f"{i+1}. {bucket.name}")
        ans = input()
        if ans == "ВЫХОД":
            sys.exit()
        if ans in list([str(x+1) for x in range(len(buckets))]):
            selected_bucket = buckets[int(ans)-1]
            print(f"Выбрана папка: {selected_bucket}")
            print("Идет поиск файлов...")
            objects = list(client.list_objects(selected_bucket.name))
            images_list = []
            videos_list = []
            for obj in objects:
                if obj.object_name.endswith(tuple(Image.registered_extensions().keys())):
                    images_list.append(obj.object_name)
                elif obj.object_name.endswith(('.mp4', '.avi')):
                    videos_list.append(obj.object_name)
            if len(images_list) == 0 and len(videos_list) == 0:
                print("В папке нет изображений или видео.")
                selected_bucket = None
            else:
                print(f"В выбранной папке найдено {len(images_list)} изображений и {len(videos_list)} видео.")
                print('')

                if len(images_list) == 0:
                    selected_list = videos_list
                    print("Будут скачаны видеофайлы.")
                elif len(videos_list) == 0:
                    selected_list = images_list
                    print("Будут скачаны изображения.")
                else:
                    while selected_list is None:
                        print("Что скачать:")
                        print("1. Изображения")
                        print("2. Видео")
                        ans = input()
                        if ans == "ВЫХОД":
                            sys.exit()
                        if ans == '1':
                            selected_list = images_list
                            print("Будут скачаны изображения.")
                        elif ans == '2':
                            selected_list = videos_list
                            print("Будут скачаны видеозаписи.")
                        else:
                            print("Указано недопустимое значение. Введите номер нужного варианта.")
                            selected_list = None
        else:
            print("Указано недопустимое значение. Введите номер нужного варианта.")
            selected_bucket = None
    print('')

    files_number = None
    while files_number is None:
        print("Укажите количество скачиваемых файлов:")
        ans = input()
        if ans == "ВЫХОД":
            sys.exit()
        if ans == '':
            files_number = len(selected_list)
        else:
            try:
                if int(ans) > len(selected_list):
                    print("Указанно количество превышающее количество файлов в папке.")
                    files_number = None
                else:
                    files_number = int(ans)
            except ValueError:
                print("Неверный формат количества! Требуется ввести целое число.")
                files_number = None
    print(f"Будет скачано: {files_number} файлов.")
    print('')

    print("Скачать в случайном порядке?(ДА для подтверждения)")
    ans = input()
    if ans == 'ДА':
        indexes = list(range(len(selected_list)))
        shuffle(indexes)
        selected_list = list([selected_list[x] for x in indexes])
        print("Файлы будут скачаны в случайном порядке.")
    else:
        print("Файлы будут скачаны по порядку.")
    print('')

    dest_path = read_dest_path()
    while dest_path is None:
        dest_path = read_dest_path()
        if dest_path == '':
            dest_path = None
    print("Выбран путь для сохранения:  " + dest_path)
    print('')

    for i in tqdm(range(files_number)):
        try:
            client.fget_object(selected_bucket.name, selected_list[i],
                           os.path.join(dest_path, selected_list[i]))
        except:
            print(f"Загрузка файла {selected_list[i]} не удалась!")
    print("Файлы успешно загружены!")


def main():
    tasks = {1: 'Раскадровка видео',
             2: 'Переформатирование изображений',
             3: 'Загрузка файлов из S3'}
    task = read_task()
    while task is None:
        task = read_task(False)
    print('Выбрана задача: ' + tasks[task])
    print('')

    if task == 1:
        video_parsing_task()
    elif task == 2:
        images_reformating_task()
    elif task == 3:
        files_downloading()


def perform_image(init_path, dest_path, resolution):
    files = os.listdir(init_path)
    images_list = []
    for file in files:
        if file.endswith(tuple(Image.registered_extensions().keys())):
            images_list.append(file)
    if len(images_list) == 0:
        print("В выбранной папке нет изображений! Введите правильный путь.")
        main()
    else:
        print("Найдено " + str(len(images_list)) + " файлов.")
        print("Начало обработки.")
        for image in tqdm(images_list):
            if image.endswith('.gif'):
                im = Image.open(os.path.join(init_path, image)).convert("RGB")
            else:
                im = Image.open(os.path.join(init_path, image))
            img = np.asarray(im)
            image = os.path.splitext(image)[0]

            if img.shape[0] > img.shape[1]:
                delay = (img.shape[0] - img.shape[1]) / 2
                leftLine = img[:, 0, :]
                leftLine = leftLine[:, np.newaxis, :]
                if img.shape[0] % 2 == 1 or img.shape[1] % 2 == 1:
                    leftField = np.repeat(leftLine, delay + 1, 1)
                else:
                    leftField = np.repeat(leftLine, delay, 1)
                rightLine = img[:, -1, :]
                rightLine = rightLine[:, np.newaxis, :]
                rightField = np.repeat(rightLine, delay, 1)
                img = np.concatenate([leftField, img, rightField], 1)
            elif img.shape[0] < img.shape[1]:
                delay = (img.shape[1] - img.shape[0]) / 2
                upperLine = img[0, :, :]
                upperLine = upperLine[np.newaxis, :, :]
                if img.shape[0] % 2 == 1 or img.shape[1] % 2 == 1:
                    upperField = np.repeat(upperLine, delay + 1, 0)
                else:
                    upperField = np.repeat(upperLine, delay, 0)
                lowerLine = img[-1, :, :]
                lowerLine = lowerLine[np.newaxis, :, :]
                lowerField = np.repeat(lowerLine, delay, 0)
                img = np.concatenate([upperField, img, lowerField], 0)

            if resolution != 0:
                img = cv2.resize(img, (resolution, resolution))

            im = Image.fromarray(img.astype('uint8'), 'RGB')
            im.save(os.path.join(dest_path, image + ".jpg"), quality=100)


def perform_video(init_path, dest_path, fps, resolution):
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
                        delay = (frame.shape[1] - frame.shape[0]) / 2
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

                    cv2.imwrite(os.path.join(dest_path, video, r"{:0>5}.jpg".format(count)), image,
                                [int(cv2.IMWRITE_JPEG_QUALITY), 100])
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
                            delay = (frame.shape[1] - frame.shape[0]) / 2
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

                        cv2.imwrite(os.path.join(dest_path, video, r"{:0>5}.jpg".format(count)), image,
                                    [int(cv2.IMWRITE_JPEG_QUALITY), 100])

            print('Файл ' + video + ' обработан.')

    print('\nОбработка завершена!!!\n')


if __name__ == '__main__':
    while True:
        main()
