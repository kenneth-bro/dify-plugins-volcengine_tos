# Volcengine TOS Cloud Storage

A powerful Dify plugin providing seamless integration with Volcengine Torch Object Storage (TOS). Enables direct file uploads to Volcengine TOS, efficient file retrieval using URLs, batch operations, and public file downloads with rich configuration options.

## Version Information

- **Current Version**: v0.0.2
- **Release Date**: 2025-12-26
- **Compatibility**: Dify Plugin Framework
- **Python Version**: 3.12

## Quick Start
1. Download the `volcengine_tos` plugin from the Dify Marketplace.
2. Configure your Volcengine TOS authorization information.
3. After completing the above configuration, you can start using the plugin immediately.

### Version History
- **v0.0.2** (2025-12-26): Added batch file download, public file download capabilities, fixed bugs
- **v0.0.1** (2025-09-22): Initial release with file upload and retrieval capabilities, support for multiple directory structures and filename modes

## Core Features

### File Upload to TOS
- **Direct File Upload**: Upload any file type directly to Volcengine TOS
- **Flexible Directory Structure**: Multiple storage directory organization options
  - Flat structure (no_subdirectory)
  - Hierarchical date structure (yyyy_mm_dd_hierarchy)
  - Combined date structure (yyyy_mm_dd_combined)
- **Filename Customization**: Control how filenames are stored in TOS
  - Use original filename
  - Append timestamp to original filename
- **Source File Tracking**: Automatically captures and returns the original filename
- **Smart Extension Detection**: Automatically determine file extensions based on content type

### File Retrieval by URL
- **Direct Content Access**: Retrieve file content directly using TOS URLs
- **Cross-Region Support**: Works with all Volcengine TOS regions worldwide

### Batch File Download
- **Multiple URLs Support**: Download multiple files at once using semicolon-separated URLs
- **Efficient Batch Processing**: Process multiple files in a single operation
- **Detailed Status Reporting**: Track success/failure status for each file

### Public File Download
- **No Authentication Required**: Download public files from any platform without API keys
- **Universal Compatibility**: Works with any publicly accessible URL
- **Flexible SSL Options**: Configure SSL verification as needed

## Technical Advantages

- **Secure Authentication**: Robust credential handling with support for HTTPS
- **Efficient Storage Management**: Intelligent file organization options
- **Comprehensive Error Handling**: Detailed error messages and status reporting
- **Multiple File Type Support**: Works with all common file formats
- **Rich Parameter Configuration**: Extensive options for customized workflows
- **Source File Tracking**: Preserves original filename information
- **Batch Operations**: Support for uploading and downloading multiple files
- **Public Access**: Download public files without authentication

## Requirements

- Python 3.12
- Volcengine TOS account with valid AccessKey credentials (for TOS operations)
- Dify Platform access
- Required Python packages (installed via requirements.txt)

## Installation & Configuration

1. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Configure the plugin in Dify with the following parameters:
   - **Endpoint**: Your Volcengine TOS endpoint (e.g., tos-cn-beijing.volces.com)
   - **Bucket Name**: Your TOS bucket name
   - **AccessKey ID**: Your Volcengine AccessKey ID
   - **AccessKey Secret**: Your Volcengine AccessKey Secret
   - **Use HTTPS**: Whether to use HTTPS for TOS requests (default: true)

## Usage

The plugin provides five powerful tools for interacting with Volcengine TOS:

### 1. Upload File to TOS (upload_file)

Dedicated tool for uploading files to Volcengine TOS.
- **Parameters**:
  - `file`: The local file to upload (required)
  - `directory`: First-level directory under the bucket (required)
  - `directory_mode`: Optional directory structure mode (default: `no_subdirectory`)
    - `no_subdirectory`: Store directly in specified directory
    - `yyyy_mm_dd_hierarchy`: Store in date-based hierarchical structure
    - `yyyy_mm_dd_combined`: Store in combined date directory
  - `filename`: Optional custom filename for TOS storage
  - `filename_mode`: Optional filename composition mode (default: `filename`)
    - `filename`: Use original filename
    - `filename_timestamp`: Use original filename plus timestamp

### 2. Multi Upload Files to TOS (multi_upload_files)

Dedicated tool for uploading multiple files to Volcengine TOS.
- **Parameters**:
  - `files`: The local files to upload (required, up to 10 files)
  - `directory`: First-level directory under the bucket (required)
  - `directory_mode`: Optional directory structure mode (default: `no_subdirectory`)
    - `no_subdirectory`: Store directly in specified directory
    - `yyyy_mm_dd_hierarchy`: Store in date-based hierarchical structure
    - `yyyy_mm_dd_combined`: Store in combined date directory
  - `filename_mode`: Optional filename composition mode (default: `filename`)
    - `filename`: Use original filename
    - `filename_timestamp`: Use original filename plus timestamp

### 3. Get File by URL (get_file_by_url)

Dedicated tool for retrieving files from Volcengine TOS using URLs.
- **Parameters**:
  - `file_url`: The URL of the file in Volcengine TOS

### 4. Get Files by URLs (get_files_by_urls)

Dedicated tool for batch downloading multiple files from Volcengine TOS.
- **Parameters**:
  - `urls`: Multiple file URLs separated by semicolon (;) (required)
    - Example: `url1;url2;url3`

### 5. Get Public File by URL (get_public_file_by_url)

Dedicated tool for downloading public files from any platform without authentication.
- **Parameters**:
  - `url`: The public URL of the file to download (required)
  - `enable_verify_ssl`: Enable SSL certificate verification (default: true)

## Examples

### Upload File
<img width="2066" height="1034" alt="upload-01" src="https://github.com/user-attachments/assets/36efab38-aaca-4a51-938c-26daa791f4a0" />

### Batch Upload Files
<img width="2040" height="736" alt="upload-02" src="https://github.com/user-attachments/assets/178410d5-bfc4-4b9a-83ac-1c7a12159323" />

### Get File by URL
<img width="2231" height="645" alt="download-01" src="https://github.com/user-attachments/assets/1bd2c648-a30b-45a3-9fed-d0ed362390b6" />
<img width="2131" height="564" alt="download-02" src="https://github.com/user-attachments/assets/9ebcdd32-efde-4908-b702-9eccfee66d44" />

## Notes

- Ensure your TOS bucket has the correct permissions configured
- The plugin requires valid Volcengine credentials with appropriate TOS access permissions (for TOS operations)
- Public file download does not require any credentials
- For very large files, consider using multipart upload functionality (not currently implemented)

## Developer Information

- **Author**: `https://github.com/sawyer-shi`
- **Source Code**: `https://github.com/sawyer-shi/dify-plugins-volcengine_tos`
- **Email**: sawyer36@foxmail.com
- **License**: MIT License
- **Support**: Through Dify platform and GitHub Issues

---

**Ready to seamlessly integrate with Volcengine TOS?**
