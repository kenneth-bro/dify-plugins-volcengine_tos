def get_content_type_by_extension(extension: str) -> str:
    """
    根据文件扩展名获取内容类型(MIME类型)
    
    Args:
        extension (str): 文件扩展名，例如 '.jpg', '.png' 等
    
    Returns:
        str: 对应的MIME类型，如果未找到则返回 'application/octet-stream'
    """
    # 常见文件扩展名到MIME类型的映射
    content_type_map = {
        # 图片类型
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.png': 'image/png',
        '.gif': 'image/gif',
        '.bmp': 'image/bmp',
        '.webp': 'image/webp',
        '.svg': 'image/svg+xml',
        '.ico': 'image/x-icon',
        
        # 文档类型
        '.txt': 'text/plain',
        '.pdf': 'application/pdf',
        '.doc': 'application/msword',
        '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        '.xls': 'application/vnd.ms-excel',
        '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        '.ppt': 'application/vnd.ms-powerpoint',
        '.pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
        
        # 音频类型
        '.mp3': 'audio/mpeg',
        '.wav': 'audio/wav',
        '.ogg': 'audio/ogg',
        '.flac': 'audio/flac',
        
        # 视频类型
        '.mp4': 'video/mp4',
        '.avi': 'video/x-msvideo',
        '.mov': 'video/quicktime',
        '.wmv': 'video/x-ms-wmv',
        '.flv': 'video/x-flv',
        '.mkv': 'video/x-matroska',
        
        # 压缩文件
        '.zip': 'application/zip',
        '.rar': 'application/vnd.rar',
        '.7z': 'application/x-7z-compressed',
        '.tar': 'application/x-tar',
        '.gz': 'application/gzip',
        
        # 代码文件
        '.py': 'text/x-python',
        '.js': 'application/javascript',
        '.css': 'text/css',
        '.html': 'text/html',
        '.htm': 'text/html',
        '.xml': 'application/xml',
        '.json': 'application/json',
        
        # 其他常见类型
        '.csv': 'text/csv',
        '.rtf': 'application/rtf',
    }
    
    # 转换为小写并查找对应的MIME类型
    extension = extension.lower()
    return content_type_map.get(extension, 'application/octet-stream')


def get_content_type_from_tos_response(response) -> str:
    """
    从火山引擎 TOS SDK 的响应对象中获取 content_type
    
    兼容多种 SDK 版本，依次尝试以下方式：
    1. response.content_type 属性（标准方式）
    2. response.headers.get('Content-Type')（兼容旧版本）
    3. response.metadata.get('content-type')（备选方案）
    4. 默认返回 'application/octet-stream'
    
    Args:
        response: TOS SDK 的 GetObjectOutput 响应对象
    
    Returns:
        str: 内容类型(MIME类型)，如果无法获取则返回 'application/octet-stream'
    
    Example:
        >>> response = client.get_object(bucket='my-bucket', key='file.txt')
        >>> content_type = get_content_type_from_tos_response(response)
        >>> print(content_type)  # 'text/plain'
    """
    # 默认值
    default_content_type = 'application/octet-stream'
    
    # 方式1: 尝试直接访问 content_type 属性（火山引擎 TOS SDK 标准方式）
    if hasattr(response, 'content_type') and response.content_type:
        return response.content_type
    
    # 方式2: 尝试从 headers 中获取
    if hasattr(response, 'headers') and response.headers:
        content_type = response.headers.get('Content-Type')
        if content_type:
            return content_type
    
    # 方式3: 尝试从 metadata 中获取
    if hasattr(response, 'metadata') and response.metadata:
        content_type = response.metadata.get('content-type')
        if content_type:
            return content_type
    
    # 如果所有方式都失败，返回默认值
    return default_content_type