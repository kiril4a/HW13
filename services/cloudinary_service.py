from cloudinary.uploader import upload

async def upload_file_to_cloudinary(file):
    try:
        result = await upload(file, folder="avatars/")
        print("here")
        return result
    except Exception as e:
        raise e
