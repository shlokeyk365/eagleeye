'''
File validation for document processing 

provides :
- file extension validation against allowed types
- file size validation with configurable limits
- content-based file type detection 
- custom validation exceptions 

Designed to integrate with FastAPI upload endpoints and document ingestion services

Split into custom exception classes, core validation functions, and integration functions
'''

# imports 

import os 
import mimetypes
from pathlib import Path
from typing import List, Dict, Any, Optional

#extra imports if needed
# need to import python-magic, if implementing advanced file-type detection

#Project imports
from app.config import settings

#exception classes (custom)
class FileValidationError(Exception):
    """Base for file validation errors"""
    def __init__(self, message : str, filename: str = None, error_code : str = None):
        super().__init__(message)
        self.message = message
        self.filename = filename
        self.error_code = error_code
        self.status_code = 400 #validation errors default

    def __str__(self) -> str:
        if self.filename:
            return f"File validation error for '{self.filename}' : {self.message}"
        return f"File validation error: {self.message}"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for API responses"""
        return {
            "error" : self.error_code or "FILE_VALIDATION_ERROR",
            "message" : self.message,
            "filename" : self.filename,
            "status_code" : self.status_code
        }

class InvalidFileExtensionError(FileValidationError):
    """Base exception for when extension not allowed"""
    def __init__(self, filename: str, actual_extension: str, allowed_extensions: List[str]):
        message = f"File extension '.{actual_extension}' is not allowed. Allowed extensions: {', '.join(['.' + ext for ext in allowed_extensions])}"
        super().__init__(message, filename, "INVALID_FILE_EXTENSION")
        self.actual_extension = actual_extension
        self.allowed_extensions = allowed_extensions
    
    def to_dict(self) -> Dict[str, Any]:
        result = super().to_dict()
        result.update({
            "actual_extension": self.actual_extension,
            "allowed_extensions": self.allowed_extensions
        })
        return result


class FileTooLargeError(FileValidationError):
    """Raised when file exceeds maximum size"""
    
    def __init__(self, filename: str, file_size: int, max_size: int):
        file_size_mb = file_size / (1024 * 1024)
        max_size_mb = max_size / (1024 * 1024)
        message = f"File size {file_size_mb:.2f}MB exceeds maximum allowed size {max_size_mb:.2f}MB"
        super().__init__(message, filename, "FILE_TOO_LARGE")
        self.file_size = file_size
        self.max_size = max_size
        self.status_code = 413  # Payload Too Large
    
    def to_dict(self) -> Dict[str, Any]:
        result = super().to_dict()
        result.update({
            "file_size_bytes": self.file_size,
            "max_size_bytes": self.max_size,
            "file_size_mb": self.file_size / (1024 * 1024),
            "max_size_mb": self.max_size / (1024 * 1024)
        })
        return result

class UnsupportedFileTypeError(FileValidationError):
    """Raised when file type cannot be processed"""
    
    def __init__(self, filename: str, detected_type: str, supported_types: List[str] = None):
        message = f"Unsupported file type: {detected_type}"
        if supported_types:
            message += f". Supported types: {', '.join(supported_types)}"
        super().__init__(message, filename, "UNSUPPORTED_FILE_TYPE")
        self.detected_type = detected_type
        self.supported_types = supported_types or []
        self.status_code = 415  # Unsupported Media Type
    
    def to_dict(self) -> Dict[str, Any]:
        result = super().to_dict()
        result.update({
            "detected_type": self.detected_type,
            "supported_types": self.supported_types
        })
        return result

#core validation functions
def validate_file_extension(filename: str, allowed_extensions: List[str]) -> bool:
    """Validate file extension against allowed list"""
    if not filename:
        return False
    
    # Extract extension safely using pathlib
    extension = Path(filename).suffix.lower()
    if not extension:
        return False
    
    # Normalize allowed extensions
    allowed_set = {ext.lower() if ext.startswith('.') else f'.{ext.lower()}' 
                   for ext in allowed_extensions}
    
    return extension in allowed_set

def validate_file_size(file_size: int, max_size: int) -> bool:
    """Validate file size against maximum limit"""
    if file_size < 0 or max_size < 0:
        raise ValueError("File sizes cannot be negative")
    return file_size <= max_size

def validate_file_type(file_content: bytes, filename: str) -> str:
    """Detect actual file type from content and return MIME type"""
    if not file_content:
        raise ValueError("File content cannot be empty")
    
    # Try content-based detection first
    mime_type, _ = mimetypes.guess_type(filename)
    
    # Fallback to common binary types if detection fails
    if not mime_type:
        if file_content.startswith(b'%PDF'):
            mime_type = 'application/pdf'
        elif file_content.startswith(b'PK\x03\x04'):
            mime_type = 'application/zip'  # Could be docx, xlsx, etc.
        else:
            mime_type = 'application/octet-stream'
    
    return mime_type or 'application/octet-stream'


# core integration functions
def validate_file_comprehensive(file_content: bytes, filename: str, file_size: int) -> Dict[str, Any]:
    """Run all validations and return detailed results"""
    config = get_file_validation_config()
    errors = []
    results = {
        "valid": True,
        "errors": errors,
        "details": {}
    }
    
    # 1. Filename safety check
    filename_safe = is_safe_filename(filename)
    results["details"]["filename_safe"] = filename_safe
    if not filename_safe:
        errors.append("Filename contains unsafe characters or path traversal")
    
    # 2. Extension validation
    try:
        extension_valid = validate_file_extension(filename, config["allowed_extensions"])
        results["details"]["extension_valid"] = extension_valid
        if not extension_valid:
            errors.append(f"File extension not allowed. Allowed: {config['allowed_extensions']}")
    except Exception as e:
        results["details"]["extension_valid"] = False
        errors.append(f"Extension validation failed: {str(e)}")
    
    # 3. Size validation
    try:
        size_valid = validate_file_size(file_size, config["max_upload_size"])
        results["details"]["size_valid"] = size_valid
        results["details"]["file_size_mb"] = get_file_size_mb(file_size)
        results["details"]["max_size_mb"] = config["max_upload_size_mb"]
        if not size_valid:
            errors.append(f"File size {get_file_size_mb(file_size):.2f}MB exceeds maximum {config['max_upload_size_mb']:.2f}MB")
    except Exception as e:
        results["details"]["size_valid"] = False
        errors.append(f"Size validation failed: {str(e)}")
    
    # 4. File type detection
    try:
        detected_type = validate_file_type(file_content, filename)
        results["details"]["detected_type"] = detected_type
        results["details"]["type_valid"] = True  # Basic validation - just detection
    except Exception as e:
        results["details"]["type_valid"] = False
        results["details"]["detected_type"] = None
        errors.append(f"File type detection failed: {str(e)}")
    
    # Overall validity
    results["valid"] = len(errors) == 0
    
    return results

def get_file_validation_config() -> Dict[str, Any]:
    """Get current validation configuration from settings"""
    return {
        "max_upload_size": settings.max_upload_size,
        "max_upload_size_mb": get_file_size_mb(settings.max_upload_size),
        "allowed_extensions": settings.get_allowed_extensions_list(),
        "upload_dir": settings.upload_dir
    }

# utility functions
def get_file_size_mb(file_size_bytes: int) -> float:
    """Convert file size from bytes to megabytes"""
    if file_size_bytes < 0:
        raise ValueError("File size cannot be negative")
    return file_size_bytes / (1024 * 1024)

def is_safe_filename(filename: str) -> bool:
    """Check for path traversal and unsafe filename patterns"""
    if not filename:
        return False
    
    # Remove path components and check for traversal
    basename = os.path.basename(filename)
    if basename != filename:
        return False  # Path traversal attempt
    
    # Check for dangerous patterns
    dangerous_patterns = [
        '..', '../', '..\\',  # Path traversal
        '\x00',  # Null byte
        '<', '>', ':', '"', '|', '?', '*',  # Invalid characters
    ]
    
    filename_lower = filename.lower()
    for pattern in dangerous_patterns:
        if pattern in filename_lower:
            return False
    
    # Check for reserved Windows names
    reserved_names = {
        'con', 'prn', 'aux', 'nul',
        'com1', 'com2', 'com3', 'com4', 'com5', 'com6', 'com7', 'com8', 'com9',
        'lpt1', 'lpt2', 'lpt3', 'lpt4', 'lpt5', 'lpt6', 'lpt7', 'lpt8', 'lpt9'
    }
    
    name_without_ext = Path(filename).stem.lower()
    if name_without_ext in reserved_names:
        return False
    
    return True