import requests
from django.conf import settings



class SocialsConfig:
    def post_to_facebook(post):
        url = f"https://graph.facebook.com/v19.0/{settings.FACEBOOK_PAGE_ID}/feed"

        data = {
            "message": (
                f"{post.title}\n\n"
                f"{post.excerpt}\n\n"
                f"{post.get_absolute_url()}"
            ),
            "access_token": settings.FACEBOOK_ACCESS_TOKEN,
        }

        response = requests.post(url, data=data)
        response.raise_for_status()


    def post_to_instagram(post):
        # Step 1: create media container
        create_url = f"https://graph.facebook.com/v19.0/{settings.INSTAGRAM_BUSINESS_ID}/media"
        create_data = {
            "image_url": post.image.url,
            "caption": f"{post.title}\n\n{post.get_absolute_url()}",
            "access_token": settings.FACEBOOK_ACCESS_TOKEN,
        }

        media = requests.post(create_url, data=create_data).json()

        if "id" not in media:
            raise Exception(media)

        # Step 2: publish media
        publish_url = f"https://graph.facebook.com/v19.0/{settings.INSTAGRAM_BUSINESS_ID}/media_publish"
        publish_data = {
            "creation_id": media["id"],
            "access_token": settings.FACEBOOK_ACCESS_TOKEN,
        }

        response = requests.post(publish_url, data=publish_data)
        response.raise_for_status()
