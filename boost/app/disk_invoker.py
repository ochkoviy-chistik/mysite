import uuid
import yadisk


class DiskInvoker:
    def __init__(self, token):
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
