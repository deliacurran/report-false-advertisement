import boto3
from django.conf import settings

s3 = boto3.client('s3')


def upload(file, key):
    try:
        s3.upload_fileobj(file, settings.AWS_STORAGE_BUCKET_NAME, key)
        return True
    except Exception as e:
        print(e)
        return False

def delete_file(key):
    try:
        s3.delete_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=key)
        return True
    except Exception as e:
        print(e)
        return False

def generate_presigned_url(key):
    file_end = key.split('.')[-1]

    content_type = 'application/pdf' if file_end == 'pdf' else 'image/jpeg' if file_end == 'jpg' or file_end == 'jpeg' else 'text/plain' if file_end == 'txt' else 'application/octet-stream'
    url = s3.generate_presigned_url('get_object',
                                    Params={
                                        'Bucket':
                                        settings.AWS_STORAGE_BUCKET_NAME,
                                        'Key': key,
                                        'ResponseContentDisposition': 'inline',
                                        'ResponseContentType': content_type
                                    },
                                    ExpiresIn=3600)
    return url
