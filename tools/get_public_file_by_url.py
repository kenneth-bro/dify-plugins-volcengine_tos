try:
    from gevent import monkey as _gevent_monkey
    _gevent_monkey.patch_all(ssl=False)
except Exception:
    pass
import os
from typing import Any
from collections.abc import Generator

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

import urllib3
from urllib.parse import unquote_plus
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

try:
    import requests
    import urllib3.contrib.pyopenssl as pyopenssl
    pyopenssl.extract_from_urllib3()
except Exception:
    pass

try:
    import ssl as _stdlib_ssl
    import urllib3.util.ssl_ as _urllib3_ssl

    _ORIG_CREATE_CTX = _urllib3_ssl.create_urllib3_context

    def _safe_create_urllib3_context(*args, **kwargs):
        try:
            return _ORIG_CREATE_CTX(*args, **kwargs)
        except RecursionError:
            ssl_version = kwargs.get("ssl_version")
            ciphers = kwargs.get("ciphers")
            cert_reqs = kwargs.get("cert_reqs")
            options = kwargs.get("options")
            cadata = kwargs.get("cadata")
            protocol = ssl_version if isinstance(ssl_version, int) else (
                _stdlib_ssl.PROTOCOL_TLS_CLIENT if hasattr(_stdlib_ssl, "PROTOCOL_TLS_CLIENT") else _stdlib_ssl.PROTOCOL_TLS
            )
            ctx = _stdlib_ssl.SSLContext(protocol)
            if cert_reqs is not None:
                try:
                    ctx.verify_mode = cert_reqs
                except Exception:
                    pass
            if options is not None:
                try:
                    ctx.options |= options
                except Exception:
                    pass
            if ciphers is not None:
                try:
                    ctx.set_ciphers(ciphers)
                except Exception:
                    pass
            if cadata is not None:
                try:
                    ctx.load_verify_locations(cadata=cadata)
                except Exception:
                    pass
            return ctx

    _urllib3_ssl.create_urllib3_context = _safe_create_urllib3_context
except Exception:
    pass

try:
    import urllib3.connection as _urllib3_conn
    _urllib3_conn.create_urllib3_context = _safe_create_urllib3_context
except Exception:
    pass

class GetPublicFileByUrlTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        try:
            result, file_content = self._download_public_file(tool_parameters)
            
            yield self.create_json_message({
                "files": [{
                    "file_name": result['filename'],
                    "file_size": result['file_size_bytes'],
                    "mime_type": result['content_type']
                }]
            })
            
            yield self.create_blob_message(
                blob=file_content,
                meta={
                    "filename": result['filename'],
                    "mime_type": result['content_type']
                }
            )
            
            success_message = "Public file downloaded successfully!\n"
            success_message += f"Filename: {result['filename']}\n"
            success_message += f"File type: {result.get('file_type', 'unknown')}\n"
            success_message += f"File size: {result['file_size']:.2f} MB\n"
            success_message += f"URL: {result['url']}\n"
            success_message += f"Content type: {result.get('content_type')}"
            
            yield self.create_text_message(success_message)
        except Exception as e:
            yield self.create_text_message(f"Operation failed: {str(e)}")
            raise e
    
    def _download_public_file(self, parameters: dict[str, Any]) -> tuple[dict, bytes]:
        try:
            url = parameters.get('url')
            
            if not url:
                raise ValueError("Missing required parameter: 'url' must be provided")
            
            enable_verify_ssl = parameters.get('enable_verify_ssl', True)
            
            import requests as _requests
            
            response = _requests.get(url, stream=True, verify=enable_verify_ssl, timeout=30)
            
            if response.status_code != 200:
                raise ValueError(f"Failed to download file. HTTP status code: {response.status_code}")
            
            file_content = response.content
            file_size = len(file_content)
            content_type = response.headers.get('Content-Type', 'application/octet-stream')
            
            filename = parameters.get('filename')
            if not filename:
                try:
                    from urllib.parse import urlparse
                    parsed_url = urlparse(url)
                    path = parsed_url.path
                    filename = os.path.basename(unquote_plus(path))
                    if not filename:
                        filename = "download"
                except Exception:
                    filename = "download"
            
            file_type = 'unknown'
            _, extension = os.path.splitext(filename)
            if extension:
                file_type = extension[1:].lower()
            else:
                content_type_map = {
                    'image/': 'image',
                    'audio/': 'audio',
                    'video/': 'video',
                    'application/pdf': 'pdf',
                    'text/': 'text',
                    'application/json': 'json',
                    'application/xml': 'xml'
                }
                for ct, ft in content_type_map.items():
                    if content_type.startswith(ct):
                        file_type = ft
                        break
            
            file_size_mb = file_size / (1024 * 1024) if file_size > 0 else 0
            
            result = {
                "filename": filename,
                "file_type": file_type,
                "file_size": round(file_size_mb, 2),
                "url": url,
                "content_type": content_type,
                "file_size_bytes": file_size
            }
            
            return result, file_content
        except Exception as e:
            raise e
