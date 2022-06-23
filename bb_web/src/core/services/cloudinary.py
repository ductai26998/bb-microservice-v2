import cloudinary
import cloudinary.api
import cloudinary.uploader


class CloudinaryService:
    @classmethod
    def upload_image(cls, image, folder: str):
        url = cloudinary.uploader.upload(image, folder=folder).get("url")
        return url

    @classmethod
    def upload_images(cls, images, folder: str):
        urls = []
        for image in images:
            url = cls.upload_image(image, folder)
            urls.append(url)
        return urls

    @classmethod
    def delete_image(cls, public_id, folder: str):
        return cloudinary.uploader.destroy(public_id, folder=folder)
