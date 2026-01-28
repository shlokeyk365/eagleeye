---
name: Text Cleaner Implementation Plan
overview: Create a comprehensive text cleaning and normalization utility module that removes excessive whitespace, normalizes line breaks, removes control characters, and optionally removes headers/footers from extracted document text. This module will be used by the document ingestion service to clean raw text before NLP processing.
todos:
  - id: implement_clean_text
    content: Implement clean_text() function with line break normalization, whitespace cleanup, control character removal, and paragraph preservation
    status: pending
  - id: implement_remove_headers
    content: Implement remove_headers_footers() function using Counter to identify and remove repetitive lines
    status: pending
  - id: add_docstrings
    content: Add comprehensive docstrings to all functions explaining parameters, return values, and behavior
    status: pending
    dependencies:
      - implement_clean_text
      - implement_remove_headers
  - id: handle_edge_cases
    content: Add edge case handling for empty strings, None values, very short texts, and error conditions
    status: pending
    dependencies:
      - implement_clean_text
      - implement_remove_headers
  - id: test_implementation
    content: Test both functions with various text samples including edge cases, mixed line breaks, and documents with headers/footers
    status: pending
    dependencies:
      - implement_clean_text
      - implement_remove_headers
      - handle_edge_cases
---

# Text Cleaner Implementation Plan

## Overview

Build `app/utils/text_cleaner.py` - a utility module for cleaning and normalizing text extracted from documents. This module will prepare raw text for downstream NLP processing by removing noise, normalizing formatting, and optionally removing repetitive headers/footers.

## File Location

`app/utils/text_cleaner.py`

## Current Status

The file exists but only contains placeholder comments. Needs full implementation.

## Requirements

### Core Functions to Implement

#### 1. `clean_text(text: str) -> str`

**Purpose**: Basic text cleaning and normalization

**What it should do**:

- Remove excessive whitespace (multiple spaces → single space)
- Normalize line breaks (handle \r\n, \r, \n variations)
- Remove control characters (except newlines and tabs)
- Preserve paragraph structure (keep double newlines for paragraph breaks)
- Strip leading/trailing whitespace
- Handle empty/None input gracefully

**Input**: Raw text string (may contain formatting issues)

**Output**: Cleaned text string

**Example**:

```python
input_text = "Hello    world\r\n\n\nThis   is   a   test."
output = clean_text(input_text)
# Output: "Hello world\n\nThis is a test."
```

#### 2. `remove_headers_footers(text: str, max_line_length: int = 100) -> str`

**Purpose**: Remove repetitive headers and footers from documents

**What it should do**:

- Identify lines that appear frequently (likely headers/footers)
- Remove lines that are too short and appear multiple times
- Preserve document content
- Handle edge cases (very short documents, no headers/footers)

**Input**: Text string, optional max line length parameter

**Output**: Text with headers/footers removed

**Strategy**:

- Count frequency of each line
- Remove lines that appear more than N times (e.g., 3+ times) and are short
- Keep lines that are part of actual content
- This is a basic implementation - can be enhanced with ML later

**Example**:

```python
text = """Page 1
This is actual content.
More content here.
Page 1
Footer text
Page 1"""
cleaned = remove_headers_footers(text)
# Should remove "Page 1" and "Footer text" if they appear frequently
```

## Implementation Details

### Function 1: `clean_text(text: str) -> str`

**Step-by-step implementation**:

1. **Handle edge cases**:
   ```python
   if not text or not isinstance(text, str):
       return ""
   ```

2. **Normalize line breaks**:

   - Convert `\r\n` (Windows) → `\n`
   - Convert `\r` (old Mac) → `\n`
   - Result: All line breaks become `\n`

3. **Remove control characters**:

   - Keep: `\n` (newline), `\t` (tab)
   - Remove: Other control characters (0x00-0x1F, 0x7F-0x9F)
   - Use regex: `re.sub(r'[\x00-\x08\x0b-\x0c\x0e-\x1f\x7f-\x9f]', '', text)`

4. **Normalize whitespace**:

   - Multiple spaces/tabs → single space
   - Use regex: `re.sub(r'[ \t]+', ' ', text)`
   - Preserve newlines

5. **Normalize multiple newlines**:

   - More than 2 consecutive newlines → exactly 2 (paragraph break)
   - Use regex: `re.sub(r'\n{3,}', '\n\n', text)`

6. **Strip leading/trailing whitespace**:

   - `text.strip()`

**Python libraries needed**:

- `re` (built-in) - Regular expressions
- No external dependencies required

### Function 2: `remove_headers_footers(text: str, max_line_length: int = 100) -> str`

**Step-by-step implementation**:

1. **Handle edge cases**:
   ```python
   if not text or len(text.split('\n')) < 5:
       return text  # Too short to have headers/footers
   ```

2. **Split into lines**:
   ```python
   lines = text.split('\n')
   ```

3. **Count line frequency**:
   ```python
   from collections import Counter
   line_counts = Counter(lines)
   ```

4. **Identify repetitive lines**:

   - Lines that appear 3+ times
   - Lines that are short (length <= max_line_length)
   - These are likely headers/footers

5. **Filter out repetitive short lines**:
   ```python
   filtered_lines = []
   for line in lines:
       if line_counts[line] >= 3 and len(line.strip()) <= max_line_length:
           # Skip this line (likely header/footer)
           continue
       filtered_lines.append(line)
   ```

6. **Rejoin text**:
   ```python
   return '\n'.join(filtered_lines)
   ```


**Edge cases to handle**:

- Very short documents (return as-is)
- No repetitive lines (return as-is)
- All lines are repetitive (return empty or original - decide on behavior)
- Lines with only whitespace (should be considered "short")

**Python libraries needed**:

- `collections.Counter` (built-in) - For counting line frequencies
- No external dependencies required

## Testing Requirements

Create test cases for:

1. **clean_text() tests**:

   - Normal text with extra spaces
   - Text with mixed line breaks (\r\n, \r, \n)
   - Text with control characters
   - Text with multiple consecutive newlines
   - Empty string
   - None input
   - Text with tabs

2. **remove_headers_footers() tests**:

   - Text with repetitive headers
   - Text with repetitive footers
   - Text with both headers and footers
   - Text without headers/footers (should return unchanged)
   - Very short text (should return unchanged)
   - Edge case: all lines are repetitive

## Documentation Resources

### Python Regular Expressions

- **Official Python re module docs**: https://docs.python.org/3/library/re.html
- **Regex tutorial**: https://docs.python.org/3/howto/regex.html
- **Regex101 (interactive tester)**: https://regex101.com/ - Test your regex patterns here

### Python Collections (Counter)

- **Official Counter docs**: https://docs.python.org/3/library/collections.html#collections.Counter
- **Counter tutorial**: https://realpython.com/python-counter/

### Text Processing Best Practices

- **Python string methods**: https://docs.python.org/3/library/stdtypes.html#string-methods
- **Text cleaning patterns**: https://stackoverflow.com/questions/1276764/stripping-everything-but-alphanumeric-chars-from-a-string-in-python

### Unicode and Control Characters

- **Unicode control characters**: https://en.wikipedia.org/wiki/Unicode_control_characters
- **Python unicode handling**: https://docs.python.org/3/howto/unicode.html

## Code Structure Template

```python
"""Text cleaning and normalization utilities"""
import re
from collections import Counter
from typing import Optional


def clean_text(text: str) -> str:
    """
    Clean and normalize extracted text.
    
    Args:
        text: Raw text string to clean
        
    Returns:
        Cleaned text string
    """
    # TODO: Implement cleaning logic
    pass


def remove_headers_footers(text: str, max_line_length: int = 100) -> Optional[str]:
    """
    Remove repetitive headers and footers from text.
    
    Args:
        text: Text string to process
        max_line_length: Maximum length for lines considered as headers/footers
        
    Returns:
        Text with headers/footers removed, or None if processing fails
    """
    # TODO: Implement header/footer removal logic
    pass
```

## Success Criteria

✅ `clean_text()` successfully:

- Normalizes all line break types
- Removes excessive whitespace
- Removes control characters
- Preserves paragraph structure
- Handles edge cases gracefully

✅ `remove_headers_footers()` successfully:

- Identifies repetitive lines
- Removes common headers/footers
- Preserves document content
- Handles edge cases (short docs, no headers, etc.)

✅ Code is:

- Well-documented with docstrings
- Type-hinted
- Handles errors gracefully
- Follows Python best practices

## Integration Points

This module will be imported and used by:

- `app/services/document_ingestion.py` - After text extraction, before returning results

**Usage example** (for reference):

```python
from app.utils.text_cleaner import clean_text, remove_headers_footers

# In document_ingestion.py:
raw_text = extract_text_from_pdf(file_path)
cleaned_text = clean_text(raw_text)
final_text = remove_headers_footers(cleaned_text)
```

## Questions to Consider

1. Should `remove_headers_footers()` return `None` on error or the original text?
2. What's the threshold for "repetitive" - 3 times? 2 times? Make it configurable?
3. Should we preserve single newlines or normalize everything to paragraph breaks?

## Next Steps After Implementation

1. Test with sample documents
2. Integrate with document_ingestion.py
3. Refine based on real-world document patterns
4. Consider ML-based header/footer detection for Phase 3