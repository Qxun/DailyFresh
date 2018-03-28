from fdfs_client.client import Fdfs_client

client = Fdfs_client()
result = client.upload_appender_by_file('01.jpg')
print(result)