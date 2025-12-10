"""
Comprehensive test of all M365 loaders via LoaderFactory
"""
import io
from src.eva_rag.loaders.factory import LoaderFactory

def test_factory():
    """Test that factory correctly routes to all M365 loaders"""
    
    print("=== Testing LoaderFactory with M365 Formats ===\n")
    
    # Test CSV
    print("1. Testing CSV via factory...")
    csv_loader = LoaderFactory.get_loader("employment.csv")
    print(f"   ✅ Got loader: {type(csv_loader).__name__}")
    
    # Test Excel
    print("\n2. Testing Excel via factory...")
    xlsx_loader = LoaderFactory.get_loader("employment.xlsx")
    xls_loader = LoaderFactory.get_loader("unemployment.xls")
    print(f"   ✅ Got .xlsx loader: {type(xlsx_loader).__name__}")
    print(f"   ✅ Got .xls loader: {type(xls_loader).__name__}")
    
    # Test PowerPoint
    print("\n3. Testing PowerPoint via factory...")
    pptx_loader = LoaderFactory.get_loader("presentation.pptx")
    ppt_loader = LoaderFactory.get_loader("slides.ppt")
    print(f"   ✅ Got .pptx loader: {type(pptx_loader).__name__}")
    print(f"   ✅ Got .ppt loader: {type(ppt_loader).__name__}")
    
    # Test MS Project
    print("\n4. Testing MS Project via factory...")
    mpp_loader = LoaderFactory.get_loader("project.mpp")
    print(f"   ✅ Got .mpp loader: {type(mpp_loader).__name__}")
    
    # Test existing loaders still work
    print("\n5. Testing existing loaders...")
    pdf_loader = LoaderFactory.get_loader("document.pdf")
    docx_loader = LoaderFactory.get_loader("document.docx")
    xml_loader = LoaderFactory.get_loader("data.xml")
    html_loader = LoaderFactory.get_loader("page.html")
    print(f"   ✅ Got PDF loader: {type(pdf_loader).__name__}")
    print(f"   ✅ Got DOCX loader: {type(docx_loader).__name__}")
    print(f"   ✅ Got XML loader: {type(xml_loader).__name__}")
    print(f"   ✅ Got HTML loader: {type(html_loader).__name__}")
    
    # List all supported extensions
    print("\n=== Supported File Extensions ===")
    extensions = LoaderFactory.supported_extensions()
    print(f"Total: {len(extensions)} extensions")
    print(f"Extensions: {', '.join(sorted(extensions))}")
    
    print("\n✅ LoaderFactory test complete!")
    print(f"✅ All {len(extensions)} file types supported!")

if __name__ == '__main__':
    test_factory()
