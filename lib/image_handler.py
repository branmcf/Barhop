
from PIL import Image
from lib.uploader import ImageUploader


class ProfileImageUploader(ImageUploader):
    def __init__(self, uploaded_file, uploaded_name):
        super(ProfileImageUploader, self).__init__(uploaded_file,uploaded_name)

    def get_type(self):
        """

        :return:
        """
        return "profile"

    def sizes(self):
        """

        :return:
        """
        return ((200, 200),)


def is_image(image):
    """

    :param image:
    :return:
    """
    try:
        Image.open(image)
    except IOError:
        return False
    return True


def is_valid_image(w_required, h_required, w_actual, h_actual):
    if w_actual < w_required and h_actual < h_required:
        return False, "Image of size atleast %dx%d expected. Got %dx%d" % (w_required, h_required, w_actual, w_actual)
    return True, ''
