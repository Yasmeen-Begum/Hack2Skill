# Design Document

## Overview

The Freelance Invoice Generator is a Python-based web application that combines modern AI technologies with a user-friendly interface to streamline invoice creation for freelancers. The system architecture integrates Gradio for the UI layer, LangChain for LLM orchestration, CrewAI for multi-agent AI workflows, and ChromaDB as the vector database for persistent storage and semantic search.

The application follows a modular architecture with clear separation between the UI layer (Gradio), business logic layer (invoice generation and calculations), AI layer (RAG and content generation), and data layer (ChromaDB). This design ensures maintainability, testability, and extensibility.

## Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Gradio UI Layer                       │
│  (Forms, Preview, File Upload, Export Controls)             │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│                   Application Layer                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Invoice    │  │  Calculation │  │   Validation │      │
│  │   Manager    │  │   Engine     │  │   Service    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│                      AI Layer                                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  LangChain   │  │   CrewAI     │  │     RAG      │      │
│  │  Chains      │  │   Agents     │  │   Pipeline   │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│                     Data Layer                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   ChromaDB   │  │  File System │  │   Embeddings │      │
│  │  Collections │  │  (Logos)     │  │   Model      │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
```

### Technology Stack

- **UI Framework**: Gradio 4.x for rapid web interface development
- **LLM Framework**: LangChain for building LLM-powered applications
- **Multi-Agent Framework**: CrewAI for coordinating AI agents
- **Vector Database**: ChromaDB for persistent storage and semantic search
- **Embeddings**: OpenAI embeddings or sentence-transformers for vector generation
- **PDF Generation**: ReportLab or WeasyPrint for invoice export
- **Language**: Python 3.10+

## Components and Interfaces

### 1. Gradio UI Component

**Responsibilities:**
- Render input forms for invoice data
- Display invoice preview
- Handle file uploads (logo)
- Provide export functionality
- Show validation errors

**Key Interfaces:**
```python
def create_invoice_ui() -> gr.Blocks:
    """Creates the main Gradio interface"""
    
def handle_invoice_generation(business_info, client_info, line_items, ...) -> dict:
    """Processes invoice creation request"""
    
def handle_ai_description(keywords: str, context: str) -> str:
    """Generates AI-assisted service descriptions"""
```

### 2. Invoice Manager

**Responsibilities:**
- Coordinate invoice creation workflow
- Manage invoice lifecycle (create, save, retrieve, update)
- Interface with ChromaDB for persistence
- Generate unique invoice numbers

**Key Interfaces:**
```python
class InvoiceManager:
    def create_invoice(self, invoice_data: InvoiceData) -> Invoice
    def save_invoice(self, invoice: Invoice) -> str
    def get_invoice(self, invoice_id: str) -> Invoice
    def list_invoices(self) -> List[Invoice]
    def search_invoices(self, query: str) -> List[Invoice]
    def generate_invoice_number(self) -> str
```

### 3. Calculation Engine

**Responsibilities:**
- Calculate line item amounts
- Compute subtotals, taxes, discounts
- Calculate total due
- Validate numerical inputs

**Key Interfaces:**
```python
class CalculationEngine:
    def calculate_line_item(self, quantity: float, rate: float) -> float
    def calculate_subtotal(self, line_items: List[LineItem]) -> float
    def calculate_tax(self, subtotal: float, tax_rate: float) -> float
    def calculate_total(self, subtotal: float, tax: float, discount: float) -> float
```

### 4. RAG Pipeline

**Responsibilities:**
- Retrieve relevant past invoice data from ChromaDB
- Generate contextually appropriate service descriptions
- Provide semantic search over invoice history

**Key Interfaces:**
```python
class RAGPipeline:
    def __init__(self, chroma_client: ChromaClient, llm: BaseLLM)
    def retrieve_similar_descriptions(self, query: str, k: int = 5) -> List[str]
    def generate_description(self, keywords: str, context: List[str]) -> str
    def search_invoices_semantic(self, query: str) -> List[Invoice]
```

### 5. CrewAI Agent System

**Responsibilities:**
- Coordinate multiple AI agents for invoice tasks
- Description generation agent
- Invoice review agent
- Data extraction agent

**Key Interfaces:**
```python
class InvoiceCrewManager:
    def __init__(self, llm: BaseLLM)
    def create_description_agent(self) -> Agent
    def create_review_agent(self) -> Agent
    def generate_professional_description(self, brief: str) -> str
```

### 6. ChromaDB Repository

**Responsibilities:**
- Store and retrieve invoice documents
- Store business and client information
- Manage vector embeddings
- Provide semantic search capabilities

**Key Interfaces:**
```python
class ChromaDBRepository:
    def __init__(self, persist_directory: str)
    def save_invoice(self, invoice: Invoice) -> str
    def get_invoice(self, invoice_id: str) -> Invoice
    def save_business_info(self, business_info: BusinessInfo) -> None
    def get_business_info(self) -> BusinessInfo
    def save_client(self, client: Client) -> str
    def search_clients(self, query: str) -> List[Client]
    def get_all_invoices(self) -> List[Invoice]
```

### 7. Validation Service

**Responsibilities:**
- Validate invoice data inputs
- Check date logic
- Validate numerical ranges
- Ensure required fields are present

**Key Interfaces:**
```python
class ValidationService:
    def validate_invoice_data(self, data: InvoiceData) -> ValidationResult
    def validate_dates(self, invoice_date: date, due_date: date) -> bool
    def validate_tax_rate(self, rate: float) -> bool
    def validate_line_item(self, item: LineItem) -> ValidationResult
```

### 8. Invoice Renderer

**Responsibilities:**
- Generate formatted invoice preview (HTML)
- Export invoice to PDF
- Handle logo embedding
- Apply consistent styling

**Key Interfaces:**
```python
class InvoiceRenderer:
    def render_preview(self, invoice: Invoice) -> str  # Returns HTML
    def export_pdf(self, invoice: Invoice, output_path: str) -> str
    def embed_logo(self, logo_path: str) -> str  # Returns base64 or embedded image
```

## Data Models

### Invoice
```python
@dataclass
class Invoice:
    invoice_id: str
    invoice_number: str
    invoice_date: date
    due_date: date
    business_info: BusinessInfo
    client_info: ClientInfo
    line_items: List[LineItem]
    subtotal: float
    tax_rate: float
    tax_amount: float
    discount: float
    total_due: float
    payment_terms: str
    payment_methods: List[PaymentMethod]
    notes: str
    created_at: datetime
    updated_at: datetime
```

### BusinessInfo
```python
@dataclass
class BusinessInfo:
    business_name: str
    owner_name: str
    address: str
    city: str
    state: str
    zip_code: str
    phone: str
    email: str
    website: str
    logo_path: Optional[str] = None
```

### ClientInfo
```python
@dataclass
class Client:
    client_id: str
    name: str
    company: str
    address: str
    city: str
    state: str
    zip_code: str
    phone: str
    email: str
```

### LineItem
```python
@dataclass
class LineItem:
    description: str
    quantity: float
    rate: float
    amount: float
```

### PaymentMethod
```python
@dataclass
class PaymentMethod:
    method_type: str  # "Bank Transfer", "PayPal", "Wise", etc.
    details: str  # Account number, email, link, etc.
```


## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Logo display in rendered invoice
*For any* invoice with a logo path specified, rendering the invoice should produce output that contains a reference to or embedding of the logo image.
**Validates: Requirements 1.1**

### Property 2: Business information completeness
*For any* business information with all required fields populated, rendering an invoice should produce output containing the business name, address, contact details, and website.
**Validates: Requirements 1.2**

### Property 3: Business information persistence round-trip
*For any* valid business information, saving it to ChromaDB and then retrieving it should return data equivalent to the original.
**Validates: Requirements 1.3, 1.4**

### Property 4: Client information completeness
*For any* client information with all required fields populated, rendering an invoice should produce output containing the client name, company, address, phone, and email in the Bill To section.
**Validates: Requirements 2.1**

### Property 5: Client retrieval accuracy
*For any* client saved to ChromaDB, retrieving it by ID should return client data equivalent to the original.
**Validates: Requirements 2.2**

### Property 6: Client persistence with invoice
*For any* invoice containing client information, saving the invoice and then retrieving it should return client data equivalent to the original.
**Validates: Requirements 2.3**

### Property 7: Client search returns matching records
*For any* set of clients stored in ChromaDB, searching with a client name should return results that include clients whose names contain the search term.
**Validates: Requirements 2.4**

### Property 8: Line item amount calculation
*For any* line item with quantity and rate, the calculated amount should equal quantity multiplied by rate.
**Validates: Requirements 3.1, 3.2**

### Property 9: Line item deletion reduces count
*For any* invoice with multiple line items, deleting one line item should result in the line item count decreasing by one.
**Validates: Requirements 3.3**

### Property 10: Invoice totals calculation invariant
*For any* invoice with line items, tax rate, and discount, the following must hold:
- subtotal = sum of all line item amounts
- tax_amount = subtotal * (tax_rate / 100)
- total_due = subtotal + tax_amount - discount
**Validates: Requirements 3.4, 6.1, 6.2, 6.3, 6.4**

### Property 11: Whitespace-only descriptions are invalid
*For any* string composed entirely of whitespace characters, attempting to create a line item with that description should be rejected by validation.
**Validates: Requirements 3.5**

### Property 12: AI-generated descriptions are non-empty
*For any* valid keyword input to the AI description generator, the generated description should be non-empty and contain at least one word from the input keywords.
**Validates: Requirements 4.1**

### Property 13: RAG retrieval returns results for similar content
*For any* invoice description stored in ChromaDB, querying with similar keywords should return at least one result when similar content exists in the database.
**Validates: Requirements 4.2**

### Property 14: AI expansion increases description length
*For any* brief keyword input to the CrewAI description expander, the generated professional description should be longer than the input and contain the original keywords.
**Validates: Requirements 4.4**

### Property 15: Invoice number uniqueness
*For any* sequence of invoice creations, all generated invoice numbers should be unique.
**Validates: Requirements 5.1**

### Property 16: Date format validation
*For any* string that does not represent a valid date, attempting to set it as an invoice date should be rejected by validation.
**Validates: Requirements 5.2**

### Property 17: Due date constraint
*For any* invoice, the due date should be greater than or equal to the invoice date.
**Validates: Requirements 5.3**

### Property 18: Due date calculation from payment terms
*For any* invoice with payment terms specified in days, the due date should equal the invoice date plus the number of days in the payment terms.
**Validates: Requirements 5.5**

### Property 19: Tax rate range validation
*For any* tax rate value outside the range [0, 100], validation should reject the value.
**Validates: Requirements 6.5**

### Property 20: Payment terms display
*For any* invoice with payment terms specified, rendering the invoice should produce output containing the payment terms text.
**Validates: Requirements 7.1**

### Property 21: Payment methods display completeness
*For any* invoice with payment methods configured, rendering the invoice should produce output containing all payment method types and their associated details.
**Validates: Requirements 7.2, 7.4**

### Property 22: Payment methods persistence round-trip
*For any* set of payment methods saved with business information, retrieving the business information should return payment methods equivalent to the original.
**Validates: Requirements 7.3**

### Property 23: Notes display in invoice
*For any* invoice with notes specified, rendering the invoice should produce output containing the notes text in the footer section.
**Validates: Requirements 8.1**

### Property 24: Invoice preview generates valid output
*For any* complete invoice data, generating a preview should produce non-empty HTML output.
**Validates: Requirements 9.1**

### Property 25: Invoice export generates valid PDF
*For any* complete invoice data, exporting to PDF should produce a valid PDF file that can be opened.
**Validates: Requirements 9.2**

### Property 26: Invoice persistence round-trip
*For any* valid invoice, saving it to ChromaDB and then retrieving it by ID should return an invoice with all fields equivalent to the original.
**Validates: Requirements 10.1, 10.3, 8.3**

### Property 27: Invoice history retrieval completeness
*For any* set of invoices saved to ChromaDB, requesting invoice history should return all saved invoices.
**Validates: Requirements 10.2**

### Property 28: Vector embeddings creation
*For any* invoice saved to ChromaDB, the invoice should have associated vector embeddings stored in the database.
**Validates: Requirements 10.4**

### Property 29: Semantic search returns relevant invoices
*For any* natural language query related to invoice content, semantic search should return invoices whose content is semantically similar to the query.
**Validates: Requirements 10.5**

### Property 30: Validation errors for invalid inputs
*For any* invalid invoice data (missing required fields, invalid formats, constraint violations), validation should return specific error messages identifying the problems.
**Validates: Requirements 11.3**

## Error Handling

### Input Validation Errors
- **Invalid dates**: Return clear error messages indicating the date format issue or constraint violation
- **Invalid numerical values**: Return error messages for out-of-range values (negative amounts, tax rates > 100%)
- **Missing required fields**: Return error messages listing all missing required fields
- **Invalid file uploads**: Return error messages for unsupported file types or corrupted images

### AI Service Errors
- **LLM API failures**: Catch exceptions, log errors, and return user-friendly messages like "AI service temporarily unavailable"
- **Empty AI responses**: Validate AI outputs and retry or return default suggestions
- **Timeout errors**: Implement timeouts for AI calls and provide fallback behavior

### Database Errors
- **ChromaDB connection failures**: Catch connection errors and provide clear error messages
- **Query failures**: Handle malformed queries gracefully with error messages
- **Persistence failures**: Implement retry logic and inform users if save operations fail

### File System Errors
- **Logo upload failures**: Validate file size and format before processing
- **PDF export failures**: Catch rendering errors and provide diagnostic information
- **Missing files**: Handle missing logo files gracefully by rendering without logo

### Validation Strategy
- Validate inputs at the UI layer before processing
- Implement domain validation in business logic layer
- Return structured validation results with field-specific error messages
- Never allow invalid data to reach the database layer

## Testing Strategy

### Unit Testing Approach

The application will use **pytest** as the primary testing framework. Unit tests will focus on:

**Calculation Engine Tests:**
- Specific examples of line item calculations (e.g., 5 hours × $100/hr = $500)
- Tax calculation examples with various rates
- Discount application examples
- Edge cases: zero quantities, zero rates, 100% discount

**Validation Service Tests:**
- Examples of valid and invalid dates
- Boundary values for tax rates (0%, 50%, 100%, 101%)
- Empty and whitespace-only string validation
- Required field validation with missing fields

**Data Model Tests:**
- Object creation with valid data
- Serialization and deserialization examples
- Edge cases: empty lists, None values

**Integration Tests:**
- ChromaDB connection and basic operations
- File upload and storage
- PDF generation with sample data

Unit tests provide concrete examples that demonstrate correct behavior and catch specific bugs in implementation.

### Property-Based Testing Approach

The application will use **Hypothesis** as the property-based testing library. Property-based tests will verify universal properties across randomly generated inputs:

**Configuration:**
- Each property test will run a minimum of 100 iterations
- Tests will use Hypothesis strategies to generate valid test data
- Each test will be tagged with a comment referencing the design document property

**Test Tagging Format:**
```python
# Feature: freelance-invoice-generator, Property 8: Line item amount calculation
@given(quantity=st.floats(min_value=0.01, max_value=1000),
       rate=st.floats(min_value=0.01, max_value=10000))
def test_line_item_calculation(quantity, rate):
    ...
```

**Property Test Coverage:**
- **Calculation properties**: Verify mathematical invariants hold for all valid inputs
- **Round-trip properties**: Verify save/retrieve cycles preserve data integrity
- **Invariant properties**: Verify system constraints hold after all operations
- **Validation properties**: Verify invalid inputs are always rejected

**Key Property Tests:**
- Invoice totals calculation invariant (Property 10)
- Business information persistence round-trip (Property 3)
- Client persistence round-trip (Property 6)
- Invoice persistence round-trip (Property 26)
- Line item amount calculation (Property 8)
- Invoice number uniqueness (Property 15)
- Due date constraint (Property 17)
- Tax rate validation (Property 19)

Property-based tests provide comprehensive coverage by testing general correctness across many inputs, catching edge cases that might be missed by example-based unit tests.

### Complementary Testing Value

Unit tests and property tests work together:
- **Unit tests** catch specific bugs in concrete scenarios and serve as documentation
- **Property tests** verify general correctness and find unexpected edge cases
- Together they provide confidence that the system works correctly across all valid inputs

## Implementation Notes

### Gradio UI Layout

The Gradio interface will be organized into tabs:
1. **Invoice Creation Tab**: Forms for all invoice data entry
2. **Preview Tab**: Live preview of formatted invoice
3. **History Tab**: List of saved invoices with search
4. **Settings Tab**: Business information and payment methods configuration

### ChromaDB Collections

The system will use multiple ChromaDB collections:
- `invoices`: Stores complete invoice documents with embeddings
- `clients`: Stores client information with embeddings for search
- `business_info`: Stores business configuration (single document)
- `descriptions`: Stores service descriptions for RAG retrieval

### LangChain Integration

LangChain will be used for:
- Building RAG chains that retrieve similar descriptions and generate new ones
- Managing prompts for description generation
- Handling LLM API calls with retry logic

### CrewAI Agents

Two primary agents:
1. **Description Writer Agent**: Expands brief notes into professional descriptions
2. **Invoice Reviewer Agent**: Reviews generated invoices for completeness and professionalism

### PDF Generation

Use **ReportLab** for PDF generation:
- Create custom template matching the invoice layout
- Embed logo as base64 or direct image
- Apply consistent styling and fonts
- Support multi-page invoices for many line items

### Environment Configuration

Required environment variables:
- `OPENAI_API_KEY`: For LLM access (or alternative LLM provider)
- `CHROMA_PERSIST_DIR`: Directory for ChromaDB persistence
- `INVOICE_LOGO_DIR`: Directory for storing uploaded logos
- `INVOICE_EXPORT_DIR`: Directory for exported PDF files
