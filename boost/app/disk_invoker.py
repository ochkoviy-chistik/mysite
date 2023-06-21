"""
Этот модуль содержит исполнителя, созданного на основе модуля yadisk (Яндекс.Диск) и комманды к исполнителю.
"""


import uuid
import yadisk
import dotenv


class DiskInvoker:
    """
    Класс исполнитель, выполняющий комманды, связанные с "Яндекс.Диск".
    """
    def __init__(self, token: str):

        self.disk = yadisk.YaDisk(token=token)

    def run(self, command, **kwargs):
        return command(self).execute(**kwargs)


class Command(object):
    def __init__(self, disk_invoker: DiskInvoker):
        self.disk = disk_invoker.disk

    def execute(self, **kwargs):
        pass


class UploadFileCommand(Command):
    def __init__(self, disk_invoker: DiskInvoker):
        super().__init__(disk_invoker)

    def execute(self, **kwargs):
        self.disk.upload(kwargs['file'], kwargs['path'])


class PublishFileCommand(Command):
    def __init__(self, disk_invoker: DiskInvoker):
        super().__init__(disk_invoker)

    def execute(self, **kwargs):
        self.disk.publish(kwargs['path'])


class GetInfoCommand(Command):
    def __init__(self, disk_invoker: DiskInvoker):
        super().__init__(disk_invoker)

    def execute(self, **kwargs):
        info = self.disk.get_meta(kwargs['path'])
        return info


class DeleteFileCommand(Command):
    def __init__(self, disk_invoker: DiskInvoker):
        super().__init__(disk_invoker)

    def execute(self, **kwargs):
        self.disk.remove(kwargs['path'])


class COMMANDS:
    UPLOAD = UploadFileCommand
    PUBLISH = PublishFileCommand
    INFO = GetInfoCommand
    DELETE = DeleteFileCommand


def unique_name_generator():
    return str(uuid.uuid4())


def main():
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
