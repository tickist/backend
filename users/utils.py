# -*- coding: utf-8 -*-
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from PIL import Image, ImageFilter


def create_thumbnail(path, user_id, type_profile=1,
                     sizes=None, frames=True):
    if not sizes:
        sizes = settings.DEFAULT_AVATAR_SIZES
    for size in sizes:
        try:
            basewidth = size[0]
            baseheight = size[1]
            sufix = "%sx%s" % (str(basewidth), str(baseheight))
            img = Image.open(settings.MEDIA_ROOT + "/" + path)
            if img.size[0] > img.size[1]:
                wpercent = (basewidth / float(img.size[0]))
                hsize = int((float(img.size[1]) * float(wpercent)))
                img = img.resize((basewidth, hsize), Image.ANTIALIAS)
            else:
                wpercent = (baseheight / float(img.size[1]))
                wsize = int((float(img.size[0]) * float(wpercent)))
                img = img.resize((wsize, baseheight), Image.ANTIALIAS)
            name = thumbnail_size(url_last(path), sufix)  # aby do nazwy dodać sufix
            if img.mode != "RGB":
                img = img.convert("RGB")
            if frames:
                img_new_frame = Image.new("RGBA", (size[0], size[1]), (255, 255, 255))
                img_new_frame.paste(img, ((size[0] - img.size[0]) // 2, (size[1] - img.size[1]) // 2))
                img = img_new_frame

            if int(type_profile) == 1:
                img.save(settings.MEDIA_ROOT + "/users/%d/%s" % (int(user_id), name))
                #resize(img, (60, 60), 0, MEDIA_ROOT + "pliki/groups/%d/%s" % (id, name_search) )
        #except IOError:
        except KeyError:
            pass


def thumbnail_size(file_path, size):
    """ filtr dodaje do nazwy pliku '_mini'"""

    file_path = file_path.split(".")
    ext = file_path.pop()
    new_file_path = '.'.join(file_path)
    new_file_path = '%s_%s.%s' % (new_file_path, size, ext)
    return new_file_path


def url_last(value):
    """ Zwraca ostatni element """
    return value.split('/')[-1]


def jwt_response_payload_handler(token, user=None, request=None):
    """
    Returns the response data for both the login and refresh views.
    Override to return a custom response such as including the
    serialized representation of the User.

    Example:

    def jwt_response_payload_handler(token, user=None):
        return {
            'token': token,
            'user': UserSerializer(user).data
        }

    """
    return {
        'token': token,
        'user_id': user.id
    }