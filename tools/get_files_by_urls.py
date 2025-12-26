try:
    from gevent import monkey as _gevent_monkey
    _gevent_monkey.patch_all(ssl=False)
except Exception:
    pass
import os
import base64
from typing import Any, Dict
from collections.abc import Generator

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

import tos
from tos.auth import CredentialProviderAuth, StaticCredentialsProvider

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

class GetFilesByUrlsTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        try:
            self._validate_credentials(tool_parameters)
            
            results = self._download_files(tool_parameters)
            
            json_results = []
            for result in results:
                json_result = {
                    "filename": result.get('filename'),
                    "file_type": result.get('file_type'),
                    "file_size": result.get('file_size'),
                    "object_key": result.get('object_key'),
                    "content_type": result.get('content_type'),
                    "file_size_bytes": result.get('file_size_bytes'),
                    "url": result.get('url'),
                    "success": result.get('success', False)
                }
                if not result.get('success'):
                    json_result['error'] = result.get('error', 'Unknown error')
                json_results.append(json_result)
            
            yield self.create_json_message({
                "files": json_results
            })
            
            for result in results:
                if result.get('file_content'):
                    yield self.create_blob_message(
                        blob=result['file_content'],
                        meta={
                            "filename": result['filename'],
                            "mime_type": result['content_type']
                        }
                    )
            
            success_message = f"Batch download completed!\n"
            success_message += f"Total files: {len(results)}\n"
            success_message += f"Successful: {sum(1 for r in results if r.get('success'))}\n"
            success_message += f"Failed: {sum(1 for r in results if not r.get('success'))}\n"
            
            for i, result in enumerate(results, 1):
                status = "✓" if result.get('success') else "✗"
                success_message += f"\n{status} File {i}: {result['filename']}\n"
                if result.get('success'):
                    success_message += f"   Size: {result['file_size']:.2f} MB\n"
                    success_message += f"   Type: {result.get('file_type', 'unknown')}\n"
                else:
                    success_message += f"   Error: {result.get('error', 'Unknown error')}\n"
            
            yield self.create_text_message(success_message)
        except Exception as e:
            yield self.create_text_message(f"Operation failed: {str(e)}")
            raise e
    
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        pass
    
    def _download_files(self, parameters: dict[str, Any]) -> list[dict]:
        try:
            urls_str = parameters.get('urls')
            
            if not urls_str:
                raise ValueError("Missing required parameter: 'urls' must be provided")
            
            urls = [url.strip() for url in urls_str.split(';') if url.strip()]
            
            if not urls:
                raise ValueError("No valid URLs provided")
            
            credentials = self.runtime.credentials if self.runtime else {}
            access_key_id = credentials.get('access_key_id')
            access_key_secret = credentials.get('access_key_secret')
            bucket = credentials.get('bucket')
            endpoint = credentials.get('endpoint')
            region = credentials.get('region', '')
            enable_verify_ssl = credentials.get('enable_verify_ssl', False)
            
            if '.' in endpoint:
                region = endpoint.split('.')[0].replace('tos-', '')
            else:
                region = credentials.get('region', '')
            
            if not access_key_id or not access_key_secret or not bucket or not endpoint:
                raise ValueError("Missing required credential: access_key_id, access_key_secret, bucket or endpoint")
            
            results = []
            
            for url in urls:
                try:
                    result = self._download_single_file(
                        url, access_key_id, access_key_secret, 
                        bucket, endpoint, region, enable_verify_ssl, parameters
                    )
                    result['success'] = True
                    results.append(result)
                except Exception as e:
                    results.append({
                        'filename': os.path.basename(unquote_plus(url.split('/')[-1] if '/' in url else url)),
                        'success': False,
                        'error': str(e),
                        'url': url
                    })
            
            return results
        except Exception as e:
            raise e
    
    def _download_single_file(self, url: str, access_key_id: str, access_key_secret: str, 
                              bucket: str, endpoint: str, region: str, 
                              enable_verify_ssl: bool, parameters: dict[str, Any]) -> dict:
        try:
            parsed_bucket, parsed_endpoint, object_key = self._parse_tos_url(url)
            
            if parsed_bucket:
                bucket = parsed_bucket
            if parsed_endpoint:
                endpoint = parsed_endpoint
            
            client = tos.TosClientV2(
                ak=access_key_id,
                sk=access_key_secret,
                endpoint=endpoint,
                region=region,
                enable_verify_ssl=enable_verify_ssl,
                request_timeout=30
            )
            
            file_content = None
            content_type = None
            file_size = 0
            
            try:
                response = client.get_object(bucket=bucket, key=object_key)
                file_content = response.read()
                file_size = len(file_content)
                content_type = response.headers.get('Content-Type', 'application/octet-stream')
            except Exception as e:
                try:
                    import requests as _requests
                    _resp = _requests.get(url, stream=True, verify=enable_verify_ssl, timeout=30)
                    if _resp.status_code == 200:
                        file_content = _resp.content
                        file_size = int(_resp.headers.get('Content-Length', len(file_content)))
                        content_type = _resp.headers.get('Content-Type', 'application/octet-stream')
                    else:
                        raise e
                except Exception:
                    raise e
            
            filename = parameters.get('filename')
            if not filename:
                filename = os.path.basename(unquote_plus(object_key))
                if not filename:
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
            
            return {
                "filename": filename,
                "file_type": file_type,
                "file_size": round(file_size_mb, 2),
                "object_key": unquote_plus(object_key),
                "content_type": content_type,
                "file_size_bytes": file_size,
                "file_content": file_content,
                "url": url
            }
        except Exception as e:
            raise e
    
    def _parse_tos_url(self, url: str) -> tuple[str, str, str]:
        import re
        
        pattern1 = r'^https?://([^.]+)\.([^/]+)/(.*)$'
        match1 = re.match(pattern1, url)
        
        if match1:
            return match1.group(1), match1.group(2), match1.group(3)
        
        pattern2 = r'^https?://([^.]+)\.([^/]+)$'
        match2 = re.match(pattern2, url)
        
        if match2:
            return match2.group(1), match2.group(2), ''
        
        raise ValueError(f"Invalid TOS URL format: {url}")
