import yadisk
import dotenv
import uuid


class DiskInvoker:
    def __init__(self, token):
        self.disk = yadisk.YaDisk(token=token)
        self.commands = {
            'upload': UploadFileCommand,
            'publish': PublishFileCommand,
            'get_info': GetInfoCommand,
            'delete': DeleteFileCommand,
        }

    def run(self, command, file=None, path=None):
        return self.commands[command](self).execute(file=file, path=path)


class Command(object):
    def __init__(self, disk_invoker: DiskInvoker):
        self.disk = disk_invoker.disk

    def execute(self, file=None, path=None):
        pass


class UploadFileCommand(Command):
    def __init__(self, disk_invoker: DiskInvoker):
        super().__init__(disk_invoker)

    def execute(self, file=None, path=None):
        self.disk.upload(file, path)


class PublishFileCommand(Command):
    def __init__(self, disk_invoker: DiskInvoker):
        super().__init__(disk_invoker)

    def execute(self, file=None, path=None):
        self.disk.publish(path)


class GetInfoCommand(Command):
    def __init__(self, disk_invoker: DiskInvoker):
        super().__init__(disk_invoker)

    def execute(self, file=None, path=None):
        info = self.disk.get_meta(path)
        return info


class DeleteFileCommand(Command):
    def __init__(self, disk_invoker: DiskInvoker):
        super().__init__(disk_invoker)

    def execute(self, file=None, path=None):
        self.disk.remove(path)


def unique_name_generator():
    return str(uuid.uuid4())


def main():
    path = f'{dotenv.get_key(r"../.env", "DISK_PATH")}' \
           f'{unique_name_generator()}'

    disk_invoker = DiskInvoker(dotenv.get_key(r'../.env', 'DISK_TOKEN'))

    disk_invoker.run('upload', file=r'../media/pic.png', path=path)
    disk_invoker.run('publish', path=path)
    link = disk_invoker.run('get_info', path=path)['public_url']
    disk_invoker.disk.remove(path)


if __name__ == '__main__':
    main()
