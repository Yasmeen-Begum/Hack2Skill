"""Quick test for PDF generation"""
from datetime import date, datetime
from src.models import Invoice, BusinessInfo, ClientInfo, LineItem, PaymentMethod
from src.services.invoice_renderer import InvoiceRenderer
from src.config import Config
import os

# Create test invoice
business = BusinessInfo(
    business_name="Test Freelance Business",
    owner_name="John Doe",
    address="123 Business St",
    city="San Francisco",
    state="CA",
    zip_code="94102",
    phone="555-1234",
    email="john@test.com",
    website="https://test.com"
)

client = ClientInfo(
    client_id="CLIENT-TEST123",
    name="Jane Smith",
    company="Acme Corp",
    address="456 Client Ave",
    city="New York",
    state="NY",
    zip_code="10001",
    phone="555-5678",
    email="jane@acme.com"
)

line_items = [
    LineItem("Website Design", 10.0, 100.0, 1000.0),
    LineItem("Logo Creation", 5.0, 50.0, 250.0)
]

payment_methods = [
    PaymentMethod("Bank Transfer", "Account: 1234567890")
]

invoice = Invoice(
    invoice_id="INV-TEST123",
    invoice_number="INV-001",
    invoice_date=date(2025, 11, 29),
    due_date=date(2025, 12, 13),
    business_info=business,
    client_info=client,
    line_items=line_items,
    subtotal=1250.0,
    tax_rate=10.0,
    tax_amount=125.0,
    discount=0.0,
    total_due=1375.0,
    payment_terms="Net 14 days",
    payment_methods=payment_methods,
    notes="Thank you for your business!",
    created_at=datetime.now(),
    updated_at=datetime.now()
)

# Generate PDF
renderer = InvoiceRenderer()
pdf_path = os.path.join(Config.INVOICE_EXPORT_DIR, "test_invoice.pdf")

print("Generating test invoice PDF...")
result = renderer.export_pdf(invoice, pdf_path)
print(f"✓ PDF generated successfully: {result}")
print(f"✓ File size: {os.path.getsize(result)} bytes")
print("\nYou can find the PDF at:", result)
