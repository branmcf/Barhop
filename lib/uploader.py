
import os
import math
import uuid
from PIL import Image


class ImageUploader(object):
    UPLOAD_PATH = "/var/www/barhop/static/images"

    def __init__(self, uploaded_file, uploaded_name):
        self.uploaded_file = uploaded_file
        self.uploaded_name = uuid.uuid4().hex

    def extension(self):
        """

        :return:
        """
        return os.path.splitext(self.uploaded_file.name)[1]

    def upload(self):
        """

        :return:
        """
        image_path = self.save()
        resizer = ImageResizer(image_path)

        for image_size in self.sizes():
            resized_dir = "%dx%d" % image_size
            resized_path = os.path.join(self.UPLOAD_PATH, self.get_type(), resized_dir, self.get_image_name())
            ensure_path(resized_path)
            resized_image = resizer.resize(*image_size)
            resized_image.save(resized_path)
        return True

    def get_image_name(self):
        """

        :return:
        """
        return self.uploaded_name + self.extension()

    def sizes(self):
        """

        :return:
        """
        raise NotImplementedError

    def save(self):
        image_name = self.get_image_name()
        image_path = os.path.join(self.UPLOAD_PATH, self.get_type(), image_name)
        ensure_path(image_path)
        with open(image_path, "wb") as image:
            for chunk in self.uploaded_file.chunks():
                image.write(chunk)
        return image_path

    def get_type(self):
        """

        :return:
        """
        raise NotImplementedError


class ImageResizer(object):
    def __init__(self, image_path):
        """

        :param image_path:
        :return:
        """
        self.image = Image.open(image_path)
        size = self.image.size
        self.org_aspect_ratio = self.aspect_ratio(size[0], size[1])

    def crop(self, width, height):
        """

        :param width:
        :param height:
        :return:
        """
        img_width, img_height = self.image.size
        resize_ratio = self.aspect_ratio(width, height)

        if width > img_width:
            height = int(max(img_width / resize_ratio, 1))
            width = int(img_width)

        if height > img_height:
            width = int(max(resize_ratio * img_height, 1))
            height = int(img_height)
        resize_ratio = self.aspect_ratio(width, height)

        # get output width and height to do the first crop
        if self.org_aspect_ratio == resize_ratio:
            crop_box = None
        else:
            if self.org_aspect_ratio > resize_ratio:
                crop_width = int(math.ceil(img_height * resize_ratio))
                crop_height = img_height
                x = int(math.ceil(img_width / 2 - crop_width / 2))
                y = 0
            elif self.org_aspect_ratio < resize_ratio:
                crop_width = img_width
                crop_height = int(math.ceil(img_width / resize_ratio))
                x = 0
                y = int(math.ceil(img_height / 2 - crop_height / 2))
            crop_box = (x, y, x + crop_width, y + crop_height)
        return self.image.crop(crop_box)

    def resize(self, width, height):
        """

        :param width:
        :param height:
        :return:
        """
        crop_image = self.crop(width, height)
        return crop_image.resize([width, height], resample=Image.ANTIALIAS)

    @classmethod
    def aspect_ratio(cls, width, height):
        """

        :param width:
        :param height:
        :return:
        """
        return float(width) / height


def ensure_path(path):
    head, _ = os.path.split(path)
    if head and not os.path.exists(head):
        try:
            os.makedirs(head)
        except IOError:
            raise
    return True
