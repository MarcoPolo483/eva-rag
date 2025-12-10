"""Tests for HTML document loader."""
from io import BytesIO

import pytest

from eva_rag.loaders.html_loader import HTMLLoader


@pytest.fixture
def html_loader():
    """Create HTML loader instance."""
    return HTMLLoader()


def test_html_loader_simple_page(html_loader):
    """Test loading simple HTML page."""
    html_content = """
    <html>
        <head><title>Test Document</title></head>
        <body>
            <h1>Main Heading</h1>
            <p>This is a paragraph.</p>
            <p>This is another paragraph.</p>
        </body>
    </html>
    """
    
    file = BytesIO(html_content.encode('utf-8'))
    result = html_loader.load(file, "test.html")
    
    assert "Main Heading" in result.text
    assert "This is a paragraph" in result.text
    assert "This is another paragraph" in result.text
    assert result.metadata.get("title") == "Test Document"


def test_html_loader_with_tables(html_loader):
    """Test loading HTML with salary tables (like Canadian IT collective agreement)."""
    html_content = """
    <html>
        <body>
            <h2>IT: Information Technology Group annual rates of pay</h2>
            <table>
                <tr>
                    <th>Level</th>
                    <th>Step 1</th>
                    <th>Step 2</th>
                    <th>Step 3</th>
                </tr>
                <tr>
                    <td>IT-01</td>
                    <td>60,696</td>
                    <td>62,940</td>
                    <td>65,180</td>
                </tr>
                <tr>
                    <td>IT-02</td>
                    <td>75,129</td>
                    <td>77,535</td>
                    <td>79,937</td>
                </tr>
                <tr>
                    <td>IT-03</td>
                    <td>88,683</td>
                    <td>91,737</td>
                    <td>94,792</td>
                </tr>
            </table>
        </body>
    </html>
    """
    
    file = BytesIO(html_content.encode('utf-8'))
    result = html_loader.load(file, "salary_table.html")
    
    # Check heading preserved
    assert "IT: Information Technology Group annual rates of pay" in result.text
    
    # Check table structure in markdown format
    assert "| Level | Step 1 | Step 2 | Step 3 |" in result.text
    assert "| --- | --- | --- | --- |" in result.text
    assert "| IT-01 | 60,696 | 62,940 | 65,180 |" in result.text
    assert "| IT-02 | 75,129 | 77,535 | 79,937 |" in result.text
    assert "| IT-03 | 88,683 | 91,737 | 94,792 |" in result.text


def test_html_loader_complex_tables_with_spans(html_loader):
    """Test loading HTML with complex tables including colspan."""
    html_content = """
    <html>
        <body>
            <h2>Complex Table</h2>
            <table>
                <tr>
                    <th colspan="2">Group A</th>
                    <th>Group B</th>
                </tr>
                <tr>
                    <td>Value 1</td>
                    <td>Value 2</td>
                    <td>Value 3</td>
                </tr>
            </table>
        </body>
    </html>
    """
    
    file = BytesIO(html_content.encode('utf-8'))
    result = html_loader.load(file, "complex_table.html")
    
    # Check table with colspan is handled
    assert "Group A" in result.text
    assert "Group B" in result.text
    assert "Value 1" in result.text


def test_html_loader_with_lists(html_loader):
    """Test loading HTML with lists."""
    html_content = """
    <html>
        <body>
            <h2>Benefits List</h2>
            <ul>
                <li>Health Insurance</li>
                <li>Dental Coverage</li>
                <li>Vacation Leave</li>
            </ul>
            <h3>Steps</h3>
            <ol>
                <li>Complete form</li>
                <li>Submit to HR</li>
                <li>Wait for approval</li>
            </ol>
        </body>
    </html>
    """
    
    file = BytesIO(html_content.encode('utf-8'))
    result = html_loader.load(file, "lists.html")
    
    # Check unordered list
    assert "• Health Insurance" in result.text
    assert "• Dental Coverage" in result.text
    
    # Check ordered list
    assert "1. Complete form" in result.text
    assert "2. Submit to HR" in result.text
    assert "3. Wait for approval" in result.text


def test_html_loader_removes_scripts_and_styles(html_loader):
    """Test that script and style tags are removed."""
    html_content = """
    <html>
        <head>
            <style>
                body { color: red; }
            </style>
            <script>
                console.log('test');
            </script>
        </head>
        <body>
            <p>Visible content</p>
        </body>
    </html>
    """
    
    file = BytesIO(html_content.encode('utf-8'))
    result = html_loader.load(file, "with_scripts.html")
    
    assert "Visible content" in result.text
    assert "color: red" not in result.text
    assert "console.log" not in result.text


def test_html_loader_with_metadata(html_loader):
    """Test extracting metadata from HTML."""
    html_content = """
    <html>
        <head>
            <title>Collective Agreement</title>
            <meta name="description" content="IT Group Collective Agreement 2021-2025">
        </head>
        <body>
            <p>Agreement content</p>
        </body>
    </html>
    """
    
    file = BytesIO(html_content.encode('utf-8'))
    result = html_loader.load(file, "metadata.html")
    
    assert result.metadata.get("title") == "Collective Agreement"
    assert "IT Group Collective Agreement" in result.metadata.get("description", "")


def test_html_loader_empty_raises_error(html_loader):
    """Test that empty HTML raises ValueError."""
    html_content = """
    <html>
        <head></head>
        <body></body>
    </html>
    """
    
    file = BytesIO(html_content.encode('utf-8'))
    
    with pytest.raises(ValueError, match="contains no extractable text"):
        html_loader.load(file, "empty.html")


def test_html_loader_real_world_structure(html_loader):
    """Test with structure similar to Canada.ca collective agreement pages."""
    html_content = """
    <html>
        <head>
            <title>Information Technology (IT) - Canada.ca</title>
        </head>
        <body>
            <main>
                <h1>Information Technology (IT)</h1>
                
                <section>
                    <h2>Part 5: pay and duration</h2>
                    
                    <article>
                        <h3>Article 47: pay administration</h3>
                        <p>Except as provided herein, the terms and conditions governing 
                        the application of pay to employees are not affected by this agreement.</p>
                    </article>
                </section>
                
                <section>
                    <h2>Appendix "A"</h2>
                    <h3>IT: Information Technology Group annual rates of pay (in dollars)</h3>
                    
                    <table>
                        <thead>
                            <tr>
                                <th>Effective Date</th>
                                <th>IT-01 Step 1</th>
                                <th>IT-01 Step 2</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td>December 22, 2020</td>
                                <td>60,696</td>
                                <td>62,940</td>
                            </tr>
                            <tr>
                                <td>December 22, 2021</td>
                                <td>61,606</td>
                                <td>63,884</td>
                            </tr>
                        </tbody>
                    </table>
                </section>
            </main>
        </body>
    </html>
    """
    
    file = BytesIO(html_content.encode('utf-8'))
    result = html_loader.load(file, "canada_agreement.html")
    
    # Check headings at different levels
    assert "# Information Technology (IT)" in result.text
    assert "## Part 5: pay and duration" in result.text
    assert "### Article 47: pay administration" in result.text
    
    # Check table structure
    assert "| Effective Date | IT-01 Step 1 | IT-01 Step 2 |" in result.text
    assert "| December 22, 2020 | 60,696 | 62,940 |" in result.text
    
    # Check paragraph content
    assert "terms and conditions governing" in result.text


def test_html_loader_handles_nested_tables(html_loader):
    """Test handling of nested table structures."""
    html_content = """
    <html>
        <body>
            <h2>Pay Rates by Year</h2>
            <table>
                <tr>
                    <th>Year</th>
                    <th>Rate</th>
                </tr>
                <tr>
                    <td>2020</td>
                    <td>$60,000</td>
                </tr>
                <tr>
                    <td>2021</td>
                    <td>$62,000</td>
                </tr>
            </table>
        </body>
    </html>
    """
    
    file = BytesIO(html_content.encode('utf-8'))
    result = html_loader.load(file, "pay_rates.html")
    
    assert "| Year | Rate |" in result.text
    assert "| 2020 | $60,000 |" in result.text
    assert "| 2021 | $62,000 |" in result.text


def test_html_loader_invalid_html_raises_error(html_loader):
    """Test that invalid HTML is handled gracefully."""
    html_content = b"\x80\x81\x82"  # Invalid bytes
    
    file = BytesIO(html_content)
    
    # Should raise error for empty/invalid content
    with pytest.raises(ValueError, match="contains no extractable text"):
        html_loader.load(file, "invalid.html")
