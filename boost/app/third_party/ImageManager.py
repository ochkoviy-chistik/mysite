import os
from django.conf import settings


class ImageManager:
    def __init__(self, path_to_image):
        self.path_to_image = path_to_image

    def delete(self):
        if settings.DEFAULT_AVATAR not in self.path_to_image and \
                settings.DEFAULT_PREVIEW not in self.path_to_image:
            os.remove(self.path_to_image)
