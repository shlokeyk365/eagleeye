---
name: Phase 2 Document Ingestion
overview: Build a comprehensive document ingestion module that accepts multiple file types (PDF, DOCX, DOC, TXT), extracts text content using appropriate libraries, handles scanned documents with OCR, validates files, and returns structured text data for downstream NLP processing.
todos:
  - id: file_validator
    content: Create app/utils/file_validator.py with file validation functions (extension, size, type detection)
    status: pending
  - id: text_cleaner
    content: Create app/utils/text_cleaner.py with text cleaning and normalization functions
    status: pending
  - id: document_service
    content: Create app/services/document_ingestion.py with DocumentIngestionService class and parser methods (PDF, DOCX, TXT, OCR)
    status: pending
    dependencies:
      - file_validator
      - text_cleaner
  - id: api_routes
    content: Create app/api/routes/case_processing.py with upload endpoint and error handling
    status: pending
    dependencies:
      - document_service
  - id: integrate_routes
    content: Update app/main.py to include the case_processing router
    status: pending
    dependencies:
      - api_routes
  - id: unit_tests
    content: Create tests/test_document_ingestion.py with unit tests for parsing and validation
    status: pending
    dependencies:
      - document_service
      - file_validator
---

# Phase 2: Document Ingestion Module

## Overview

Build a robust document ingestion system that can handle multiple file formats commonly found in legal cases (PDFs, Word documents, text files). The module will extract raw text, handle scanned documents via OCR, validate files, and prepare text for downstream NLP processing.

## Architecture

```
User uploads file → API endpoint → File validation → Document parser → Text extraction → Text cleaning → Return structured data
```

## Files to Create/Modify

### New Files:

1. **`app/services/document_ingestion.py`** - Core document processing service
2. **`app/api/routes/case_processing.py`** - API endpoints for file uploads
3. **`app/utils/file_validator.py`** - File validation utilities
4. **`app/utils/text_cleaner.py`** - Text cleaning and normalization
5. **`tests/test_document_ingestion.py`** - Unit tests

### Files to Modify:

1. **`app/main.py`** - Include the new API router

## Implementation Details

### 1. File Validator Utility (`app/utils/file_validator.py`)

**Purpose**: Validate uploaded files before processing

**Functions**:

- `validate_file_extension(filename: str, allowed_extensions: List[str]) -> bool`
  - Check if file extension is in allowed list
  - Case-insensitive matching

- `validate_file_size(file_size: int, max_size: int) -> bool`
  - Verify file doesn't exceed maximum upload size

- `validate_file_type(file_content: bytes, filename: str) -> str`
  - Detect actual file type (not just extension)
  - Return file type: "pdf", "docx", "doc", "txt"

**Error Handling**:

- Raise custom exceptions: `InvalidFileExtensionError`, `FileTooLargeError`, `UnsupportedFileTypeError`

### 2. Text Cleaner Utility (`app/utils/text_cleaner.py`)

**Purpose**: Clean and normalize extracted text

**Functions**:

- `clean_text(text: str) -> str`
  - Remove excessive whitespace
  - Normalize line breaks
  - Remove control characters
  - Preserve paragraph structure

- `remove_headers_footers(text: str, max_line_length: int = 100) -> str`
  - Identify and remove repetitive headers/footers
  - Optional: can be enhanced later with ML-based detection

### 3. Document Ingestion Service (`app/services/document_ingestion.py`)

**Purpose**: Main service orchestrating document parsing

**Class**: `DocumentIngestionService`

**Methods**:

- `__init__(self)`
  - Initialize document parsers
  - Set up OCR if needed

- `parse_pdf(file_path: str, use_ocr: bool = False) -> Dict[str, Any]`
  - Primary: Use PyMuPDF (fitz) for text extraction
  - Fallback: Use pdfplumber for better table/form handling
  - If text is sparse/minimal: detect scanned document and use OCR
  - Return: `{"text": str, "metadata": {"pages": int, "method": str}}`

- `parse_docx(file_path: str) -> Dict[str, Any]`
  - Use python-docx to extract text
  - Preserve paragraph structure
  - Extract basic metadata (if available)
  - Return: `{"text": str, "metadata": {"paragraphs": int}}`

- `parse_text(file_path: str) -> Dict[str, Any]`
  - Simple text file reading
  - Handle encoding detection (UTF-8, Latin-1, etc.)
  - Return: `{"text": str, "metadata": {}}`

- `extract_with_ocr(file_path: str) -> str`
  - Use pytesseract for OCR
  - Convert PDF pages to images (PyMuPDF)
  - Process each page through OCR
  - Combine results

- `parse_document(file_path: str, file_type: str) -> Dict[str, Any]`
  - Main entry point
  - Route to appropriate parser based on file_type
  - Apply text cleaning
  - Return structured result: 
    ```python
    {
        "text": str,
        "metadata": {
            "file_type": str,
            "file_size": int,
            "pages": int (if applicable),
            "extraction_method": str,
            "word_count": int,
            "character_count": int
        },
        "errors": List[str]  # Any warnings or errors
    }
    ```


**Error Handling**:

- Handle corrupted files gracefully
- Log errors but don't crash
- Return error information in response

### 4. API Routes (`app/api/routes/case_processing.py`)

**Purpose**: FastAPI endpoints for document upload and processing

**Endpoints**:

- `POST /api/v1/documents/upload`
  - Accept multipart file upload
  - Validate file (size, extension, type)
  - Save to temporary location (uploads/)
  - Call DocumentIngestionService
  - Return parsed text + metadata
  - Clean up file after processing (or schedule cleanup)

**Request**: `FormData` with `file: UploadFile`

**Response**:

  ```json
  {
    "success": true,
    "document_id": "uuid",
    "data": {
      "text": "...",
      "metadata": {...}
    },
    "processing_time_ms": float
  }
  ```

- `POST /api/v1/documents/batch-upload` (optional, for Phase 2)
  - Accept multiple files
  - Process each file
  - Return array of results

**Error Responses**:

- 400: Invalid file type/size
- 422: Validation error
- 500: Processing error

**Dependencies**:

- FastAPI `UploadFile`, `File`, `Form`
- File validation utilities
- DocumentIngestionService

### 5. Integration with Main App (`app/main.py`)

**Changes**:

- Import and include the case_processing router
- Add route prefix: `/api/v1`

### 6. Testing (`tests/test_document_ingestion.py`)

**Test Cases**:

- Test PDF text extraction (digital PDF)
- Test DOCX parsing
- Test TXT file parsing
- Test file validation (valid/invalid extensions, sizes)
- Test error handling (corrupted files, unsupported types)
- Test OCR path (if test files available)
- Test text cleaning functions

## Data Flow

```
1. Client uploads file via POST /api/v1/documents/upload
2. FastAPI receives UploadFile
3. FileValidator checks extension, size, type
4. File saved temporarily to uploads/
5. DocumentIngestionService.parse_document() called
   a. Routes to appropriate parser (PDF/DOCX/TXT)
   b. Extracts text using library
   c. Detects if OCR needed (for PDFs)
   d. Applies text cleaning
   e. Calculates metadata
6. TextCleaner normalizes text
7. Response returned with text + metadata
8. File cleanup (immediate or scheduled)
```

## Key Design Decisions

1. **PDF Parsing Strategy**:

   - Primary: PyMuPDF (fast, good text extraction)
   - Fallback: pdfplumber (better for tables/forms)
   - OCR: pytesseract (for scanned documents)
   - Detection: If extracted text < threshold words per page → trigger OCR

2. **File Storage**:

   - Store temporarily in `uploads/` directory
   - Use UUID for unique filenames
   - Clean up after processing (or implement retention policy)

3. **Error Handling**:

   - Don't fail silently - return error details
   - Log all errors for debugging
   - Graceful degradation (e.g., partial text extraction)

4. **Performance Considerations**:

   - Async file I/O where possible
   - Large files: stream processing if needed
   - OCR is slow - consider async processing for large batches

## Success Criteria

- ✅ Can extract text from digital PDFs
- ✅ Can extract text from DOCX files
- ✅ Can extract text from TXT files
- ✅ Validates file types and sizes correctly
- ✅ Handles errors gracefully
- ✅ Returns structured, clean text data
- ✅ API endpoint accepts files and returns parsed text
- ✅ Basic tests pass

## Dependencies Already Installed

All required libraries are in requirements.txt:

- `pymupdf` (fitz) - PDF parsing
- `pdfplumber` - PDF parsing (alternative)
- `python-docx` - Word documents
- `pytesseract` - OCR
- `Pillow` - Image processing for OCR

## Next Steps After Phase 2

- Phase 3: NLP/AI Processing (extract dates, entities, timelines)
- Frontend integration (file upload UI)
- Batch processing improvements
- Advanced OCR optimization