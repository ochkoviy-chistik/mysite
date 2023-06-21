"""
Этот модуль содержит исполнителя, созданного на основе
модуля yadisk (Яндекс.Диск) и комманды к исполнителю.
"""


import uuid
import yadisk
import dotenv


class DiskInvoker:
    """
    Класс исполнитель, выполняющий комманды, связанные с "Яндекс.Диск".
    """
    def __init__(self, token: str):
        """
        Конструктор класса DiskInvoker.
        Создает экземпляр класса yadisk.YaDisk.
        Принимает специальный токен.
        Получить можно здесь: https://yandex.ru/dev/disk/rest/.
        """
        self.disk = yadisk.YaDisk(token=token)

    def run(self, command, **kwargs):
        """
        Метод принимает на вход комманду и
        необходимые дополнительные параметры
        """
        return command(self).execute(**kwargs)



class UploadFileCommand:
    """
    Класс комманды сохранения файла на облако.
    """
    def __init__(self, disk_invoker: DiskInvoker):
        """
        Конструктор команды.
        Принимает на вход объект исполнителя.
        """
        self.disk = disk_invoker.disk

    def execute(self, **kwargs):
        """
        Сохраняет файл на облако.
        """
        self.disk.upload(kwargs['file'], kwargs['path'])


class PublishFileCommand:
    """
    Класс комманды, которая делает файл на диске публичным.
    """
    def __init__(self, disk_invoker: DiskInvoker):
        """
        Конструктор команды.
        Принимает на вход объект исполнителя.
        """
        self.disk = disk_invoker.disk

    def execute(self, **kwargs):
        """
        Делает файл публичным.
        """
        self.disk.publish(kwargs['path'])


class GetInfoCommand:
    """
    Класс комманды, получающей информацию о файле.
    """
    def __init__(self, disk_invoker: DiskInvoker):
        """
        Конструктор команды.
        Принимает на вход объект исполнителя.
        """
        self.disk = disk_invoker.disk

    def execute(self, **kwargs):
        """
        Получает инфу о файле, лежащему по такому-то пути.
        """
        info = self.disk.get_meta(kwargs['path'])
        return info


class DeleteFileCommand:
    """
    Класс комманды, которая удаляет файл.
    """
    def __init__(self, disk_invoker: DiskInvoker):
        """
        Конструктор команды.
        Принимает на вход объект исполнителя.
        """
        self.disk = disk_invoker.disk

    def execute(self, **kwargs):
        """
        Удаляет файл, лежащий по такому-то пути.
        """
        self.disk.remove(kwargs['path'])


class COMMANDS:
    """
    Класс, содержащий список исполняемых комманд.
    """
    UPLOAD = UploadFileCommand
    PUBLISH = PublishFileCommand
    INFO = GetInfoCommand
    DELETE = DeleteFileCommand


def unique_name_generator():
    """
    Генерирует уникальное имя файла.
    """
    return str(uuid.uuid4())


def main():
    """
    For fun :)
    """
    path = f'{dotenv.get_key(r"../../.env", "DISK_PATH")}' \
           f'{unique_name_generator()}'

    disk_invoker = DiskInvoker(dotenv.get_key(r'../../.env', 'DISK_TOKEN'))

    disk_invoker.run(COMMANDS.UPLOAD, file=r'../media/pic.png', path=path)
    disk_invoker.run(COMMANDS.PUBLISH, path=path)
    link = disk_invoker.run(COMMANDS.INFO, path=path)
    print(link)
    disk_invoker.run(COMMANDS.DELETE, path=path)


if __name__ == '__main__':
    main()
