from django.core.files.storage import Storage
from fdfs_client.client import Fdfs_client
from django.conf import settings

class FdfsStorage(Storage):
    def save(self, name, content, max_length=None):
        buffer = content.read()
        client = Fdfs_client(settings.FDFS_CLIENT)
        try:
            result = client.upload_appender_by_buffer(buffer)
        except:
            raise

        if result.get('Status')=='Upload successed.':
            return result.get('Remote file_id')
        else :
            raise Exception('上传失败')

    def url(self, name):
        return settings.FDFS_SERVER + name