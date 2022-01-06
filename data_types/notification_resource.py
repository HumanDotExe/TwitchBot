import base64
import mimetypes
import pathlib

from data_types.types_collection import NotificationType


class NotificationResource:

    audio_formats = [".mp3", ".wav", ".ogg"]
    image_formats = [".gif", ".jpg", ".jpeg", ".png", ".webp", ".apng"]

    def __init__(self, notification_type: NotificationType):
        self.notification_type = notification_type
        self._message = None
        self._image = None
        self._image_mime = None
        self._sound = None
        self._sound_mime = None

    def has_message(self):
        return self._message is not None

    def has_image(self):
        return self._image is not None

    def has_sound(self):
        return self._sound is not None

    def get_message(self):
        return self._message

    def get_image(self):
        return self._image, self._image_mime

    def get_sound(self):
        return self._sound, self._sound_mime

    def set_message(self, message):
        self._message = message

    def set_image(self, image_name, resource_path: pathlib.Path):
        image_path = resource_path / image_name
        if image_path.is_file() and image_path.suffix.lower() in NotificationResource.image_formats:
            if image_path.suffix.lower() == ".webp":
                image_mimetype = "image/webp"
            else:
                image_mimetype = mimetypes.guess_type(image_path)[0]
            if image_mimetype:
                self._image = base64.b64encode(open(image_path, 'rb').read()).decode('utf-8')
                self._image_mime = image_mimetype

    def set_sound(self, sound_name, resource_path: pathlib.Path):
        sound_path = resource_path / sound_name
        if sound_path.is_file() and sound_path.suffix.lower() in NotificationResource.audio_formats:
            sound_mimetype = mimetypes.guess_type(sound_path)[0]
            if sound_mimetype:
                self._sound = base64.b64encode(open(sound_path, 'rb').read()).decode('utf-8')
                self._sound_mime = sound_mimetype