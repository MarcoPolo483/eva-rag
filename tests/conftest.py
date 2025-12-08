"""Pytest configuration and fixtures."""
import pytest
from io import BytesIO
from uuid import uuid4


@pytest.fixture
def sample_pdf_content() -> bytes:
    """Sample PDF binary content for testing."""
    # Minimal valid PDF structure
    return b"""%PDF-1.4
1 0 obj
<< /Type /Catalog /Pages 2 0 R >>
endobj
2 0 obj
<< /Type /Pages /Kids [3 0 R] /Count 1 >>
endobj
3 0 obj
<< /Type /Page /Parent 2 0 R /Contents 4 0 R /MediaBox [0 0 612 792] >>
endobj
4 0 obj
<< /Length 44 >>
stream
BT
/F1 12 Tf
100 700 Td
(Test Content) Tj
ET
endstream
endobj
xref
0 5
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
0000000214 00000 n 
trailer
<< /Size 5 /Root 1 0 R >>
startxref
306
%%EOF
"""


@pytest.fixture
def sample_text_content() -> str:
    """Sample text content for testing."""
    return """This is a sample document.

It contains multiple paragraphs for testing the document loaders
and language detection.

Eligibility criteria: 1) Employed for 600+ hours, 2) Valid work permit."""


@pytest.fixture
def tenant_id() -> str:
    """Generate test tenant ID."""
    return str(uuid4())


@pytest.fixture
def space_id() -> str:
    """Generate test space ID."""
    return str(uuid4())


@pytest.fixture
def user_id() -> str:
    """Generate test user ID."""
    return str(uuid4())


@pytest.fixture
def document_id() -> str:
    """Generate test document ID."""
    return str(uuid4())
