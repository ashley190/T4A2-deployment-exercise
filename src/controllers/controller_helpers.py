from flask_login import current_user
from models.Profile import Profile
import boto3
import os
import requests
import json


class Helpers():
    """
    Commonly used helpers
    """
    @classmethod
    def retrieve_profile(cls):
        """Retrieve user id and profile of active user"""
        user_id = current_user.get_id()
        profile = Profile.query.filter_by(user_id=user_id).first()
        return user_id, profile

    @classmethod
    def retrieve_profile_picture(cls, profile_image):
        """Retrieve profile_image from S3 bucket"""
        s3 = boto3.client('s3')
        bucket = os.environ.get("AWS_S3_BUCKET")
        url = s3.generate_presigned_url('get_object', Params={
            "Bucket": bucket,
            "Key": f"profile_images/{profile_image.filename}"}, ExpiresIn=5)
        return url

    @classmethod
    def location_search(cls, postcode):
        """Searches location by postcode using external API"""
        api_url = f"http://v0.postcodeapi.com.au/suburbs/{postcode}.json"
        response = requests.get(api_url)
        return json.loads(response.text) or None
