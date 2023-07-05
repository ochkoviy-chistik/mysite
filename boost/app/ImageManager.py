import os


class ImageManager:
    def __init__(self, path_to_image):
        self.path_to_image = path_to_image

    def delete(self):
        os.remove(self.path_to_image)
