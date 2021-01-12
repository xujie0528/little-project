from django.core.files.storage import Storage
from django.conf import settings

from fdfs_client.client import Fdfs_client


class FastDFSStorage(Storage):
    """自定义 FastDFS 文件存储类"""
    def _save(self, name, content):
        """文件的保存方法"""
        # name: 上传文件的名称
        # content: 包含上传文件内容的File对象，content.read()获取上传文件内容

        # 创建 Fdfs_client 对象
        client = Fdfs_client(settings.FDFS_CLIENT_CONF)

        # 上传文件到 FastDFS 系统
        res = client.upload_by_buffer(content.read())
        print(res)

        if res.get('Status') != 'Upload successed.':
            raise Exception('上传文件到FDFS系统失败')

        # 获取返回的文件ID
        file_id = res.get('Remote file_id')

        return file_id

    def exists(self, name):
        """判断上传文件的名称和文件系统中原有的文件名是否冲突"""
        # name: 上传文件的名称
        return False

    def url(self, name):
        """返回可访问到图片的完整的 URL 地址"""
        return settings.FDFS_URL + name
