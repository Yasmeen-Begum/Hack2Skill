# Implementation Plan

- [x] 1. Set up project structure and dependencies



  - Create directory structure for models, services, repositories, UI, and tests
  - Set up Python virtual environment
  - Install required packages: gradio, langchain, crewai, chromadb, hypothesis, pytest, reportlab
  - Create configuration file for environment variables
  - Initialize ChromaDB with required collections
  - _Requirements: All_




- [ ] 2. Implement core data models
  - [ ] 2.1 Create data model classes
    - Define Invoice, BusinessInfo, ClientInfo, LineItem, and PaymentMethod dataclasses
    - Implement serialization methods (to_dict, from_dict) for ChromaDB storage
    - _Requirements: 1.2, 2.1, 3.1, 7.2_

  - [ ] 2.2 Write property test for business info round-trip
    - **Property 3: Business information persistence round-trip**
    - **Validates: Requirements 1.3, 1.4**

  - [ ] 2.3 Write property test for client persistence
    - **Property 6: Client persistence with invoice**
    - **Validates: Requirements 2.3**

  - [ ] 2.4 Write property test for invoice round-trip
    - **Property 26: Invoice persistence round-trip**
    - **Validates: Requirements 10.1, 10.3, 8.3**

- [ ] 3. Implement calculation engine
  - [ ] 3.1 Create CalculationEngine class
    - Implement calculate_line_item method (quantity × rate)
    - Implement calculate_subtotal method (sum of line items)
    - Implement calculate_tax method (subtotal × tax_rate / 100)
    - Implement calculate_total method (subtotal + tax - discount)
    - _Requirements: 3.1, 3.2, 3.4, 6.1, 6.2_

  - [ ] 3.2 Write property test for line item calculation
    - **Property 8: Line item amount calculation**
    - **Validates: Requirements 3.1, 3.2**

  - [ ] 3.3 Write property test for invoice totals invariant
    - **Property 10: Invoice totals calculation invariant**
    - **Validates: Requirements 3.4, 6.1, 6.2, 6.3, 6.4**

  - [ ] 3.4 Write unit tests for calculation edge cases
    - Test zero quantities and rates
    - Test 100% discount
    - Test 0% and 100% tax rates
    - _Requirements: 6.1, 6.2_

- [ ] 4. Implement validation service
  - [ ] 4.1 Create ValidationService class
    - Implement validate_invoice_data method
    - Implement validate_dates method (due_date >= invoice_date)
    - Implement validate_tax_rate method (0 <= rate <= 100)
    - Implement validate_line_item method (non-empty description)
    - Return structured ValidationResult with field-specific errors
    - _Requirements: 3.5, 5.2, 5.3, 6.5, 11.3_

  - [ ] 4.2 Write property test for whitespace description validation
    - **Property 11: Whitespace-only descriptions are invalid**
    - **Validates: Requirements 3.5**

  - [ ] 4.3 Write property test for due date constraint
    - **Property 17: Due date constraint**
    - **Validates: Requirements 5.3**

  - [ ] 4.4 Write property test for tax rate validation
    - **Property 19: Tax rate range validation**
    - **Validates: Requirements 6.5**

  - [ ] 4.5 Write property test for validation error messages
    - **Property 30: Validation errors for invalid inputs**
    - **Validates: Requirements 11.3**

  - [ ] 4.6 Write unit tests for date validation
    - Test invalid date formats
    - Test boundary cases for due dates
    - _Requirements: 5.2, 5.3_

- [ ] 5. Implement ChromaDB repository
  - [ ] 5.1 Create ChromaDBRepository class
    - Initialize ChromaDB client with persistence directory
    - Create collections for invoices, clients, business_info, descriptions
    - Implement save_invoice and get_invoice methods
    - Implement save_business_info and get_business_info methods
    - Implement save_client, get_client, and search_clients methods
    - Implement get_all_invoices method
    - Generate embeddings for stored documents
    - _Requirements: 1.3, 1.4, 2.2, 2.3, 2.4, 7.3, 10.1, 10.2, 10.4_

  - [ ] 5.2 Write property test for client search
    - **Property 7: Client search returns matching records**
    - **Validates: Requirements 2.4**

  - [ ] 5.3 Write property test for invoice history completeness
    - **Property 27: Invoice history retrieval completeness**
    - **Validates: Requirements 10.2**

  - [ ] 5.4 Write property test for vector embeddings creation
    - **Property 28: Vector embeddings creation**
    - **Validates: Requirements 10.4**

  - [ ] 5.5 Write unit tests for ChromaDB operations
    - Test connection initialization
    - Test collection creation
    - Test basic CRUD operations
    - _Requirements: 10.1, 10.2_

- [ ] 6. Implement invoice manager
  - [ ] 6.1 Create InvoiceManager class
    - Implement create_invoice method (coordinates validation and calculation)
    - Implement save_invoice method (delegates to repository)
    - Implement get_invoice method (retrieves from repository)
    - Implement list_invoices method (retrieves all from repository)
    - Implement generate_invoice_number method (sequential format)
    - Implement calculate_due_date method (invoice_date + payment_term_days)
    - _Requirements: 5.1, 5.5, 10.1, 10.2_

  - [ ] 6.2 Write property test for invoice number uniqueness
    - **Property 15: Invoice number uniqueness**
    - **Validates: Requirements 5.1**

  - [ ] 6.3 Write property test for due date calculation
    - **Property 18: Due date calculation from payment terms**
    - **Validates: Requirements 5.5**

  - [ ] 6.4 Write property test for line item deletion
    - **Property 9: Line item deletion reduces count**
    - **Validates: Requirements 3.3**

- [ ] 7. Implement RAG pipeline
  - [ ] 7.1 Create RAGPipeline class
    - Initialize with ChromaDB client and LLM
    - Implement retrieve_similar_descriptions method (queries descriptions collection)
    - Implement generate_description method (uses LangChain with retrieved context)
    - Implement search_invoices_semantic method (semantic search over invoices)
    - Create LangChain prompt templates for description generation
    - _Requirements: 4.1, 4.2, 10.5_

  - [ ] 7.2 Write property test for RAG retrieval
    - **Property 13: RAG retrieval returns results for similar content**
    - **Validates: Requirements 4.2**

  - [ ] 7.3 Write property test for semantic search
    - **Property 29: Semantic search returns relevant invoices**
    - **Validates: Requirements 10.5**

  - [ ] 7.4 Write property test for AI-generated descriptions
    - **Property 12: AI-generated descriptions are non-empty**
    - **Validates: Requirements 4.1**

  - [ ] 7.5 Write unit tests for RAG pipeline
    - Test with mock LLM responses
    - Test retrieval with empty database
    - Test error handling for LLM failures
    - _Requirements: 4.1, 4.2_

- [ ] 8. Implement CrewAI agent system
  - [ ] 8.1 Create InvoiceCrewManager class
    - Initialize with LLM configuration
    - Create description writer agent with role and goal
    - Create invoice reviewer agent
    - Implement generate_professional_description method (coordinates agents)
    - Define agent tasks for description expansion
    - _Requirements: 4.4_

  - [ ] 8.2 Write property test for AI expansion
    - **Property 14: AI expansion increases description length**
    - **Validates: Requirements 4.4**

  - [ ] 8.3 Write unit tests for CrewAI agents
    - Test agent initialization
    - Test description expansion with sample inputs
    - Test error handling
    - _Requirements: 4.4_

- [ ] 9. Implement invoice renderer
  - [ ] 9.1 Create InvoiceRenderer class
    - Implement render_preview method (generates HTML)
    - Create HTML template with CSS styling
    - Implement embed_logo method (base64 encoding or file path)
    - Handle missing logo gracefully
    - Implement export_pdf method (uses ReportLab)
    - Create PDF template matching HTML layout
    - _Requirements: 1.1, 1.2, 1.5, 2.1, 7.1, 7.2, 8.1, 9.1, 9.2_

  - [ ] 9.2 Write property test for logo display
    - **Property 1: Logo display in rendered invoice**
    - **Validates: Requirements 1.1**

  - [ ] 9.3 Write property test for business info completeness
    - **Property 2: Business information completeness**
    - **Validates: Requirements 1.2**

  - [ ] 9.4 Write property test for client info completeness
    - **Property 4: Client information completeness**
    - **Validates: Requirements 2.1**

  - [ ] 9.5 Write property test for payment terms display
    - **Property 20: Payment terms display**
    - **Validates: Requirements 7.1**

  - [ ] 9.6 Write property test for payment methods display
    - **Property 21: Payment methods display completeness**
    - **Validates: Requirements 7.2, 7.4**

  - [ ] 9.7 Write property test for notes display
    - **Property 23: Notes display in invoice**
    - **Validates: Requirements 8.1**

  - [ ] 9.8 Write property test for preview generation
    - **Property 24: Invoice preview generates valid output**
    - **Validates: Requirements 9.1**

  - [ ] 9.9 Write property test for PDF export
    - **Property 25: Invoice export generates valid PDF**
    - **Validates: Requirements 9.2**

  - [ ] 9.10 Write unit tests for rendering
    - Test HTML generation with sample data
    - Test PDF generation with sample data
    - Test logo embedding
    - Test rendering without logo
    - _Requirements: 1.1, 1.5, 9.1, 9.2_

- [ ] 10. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 11. Implement Gradio UI
  - [ ] 11.1 Create main Gradio interface
    - Create Invoice Creation tab with input forms
    - Add fields for business info (name, address, contact, logo upload)
    - Add fields for client info (name, company, address, contact)
    - Add dynamic line items section (add/remove rows)
    - Add fields for tax rate, discount, payment terms
    - Add payment methods configuration
    - Add notes field
    - _Requirements: 1.1, 1.2, 2.1, 3.1, 6.1, 6.2, 7.1, 7.2, 8.1, 11.1_

  - [ ] 11.2 Create Preview tab
    - Display live invoice preview using InvoiceRenderer
    - Update preview when form data changes
    - _Requirements: 9.1, 11.4_

  - [ ] 11.3 Create History tab
    - Display list of saved invoices
    - Implement search functionality (text and semantic)
    - Add load invoice button for each saved invoice
    - _Requirements: 10.2, 10.5_

  - [ ] 11.4 Create Settings tab
    - Form for business information configuration
    - Payment methods management
    - Save and load business settings
    - _Requirements: 1.3, 1.4, 7.3_

  - [ ] 11.5 Implement AI assistance buttons
    - Add "Generate Description" button for line items
    - Connect to RAG pipeline and CrewAI agents
    - Display AI suggestions for user approval
    - _Requirements: 4.1, 4.3, 4.4_

  - [ ] 11.6 Implement form validation and error display
    - Validate inputs on submission
    - Display validation errors next to relevant fields
    - Prevent submission with invalid data
    - _Requirements: 11.3_

  - [ ] 11.7 Implement invoice actions
    - Add "Save Invoice" button (saves to ChromaDB)
    - Add "Export PDF" button (generates and downloads PDF)
    - Add "Load Invoice" functionality from history
    - Add "New Invoice" button (clears form)
    - _Requirements: 9.2, 10.1, 10.3_

  - [ ] 11.8 Implement client autocomplete
    - Add client search/autocomplete in client info section
    - Auto-fill client details when selected from history
    - _Requirements: 2.2, 2.4_

  - [ ] 11.9 Write integration tests for UI workflows
    - Test complete invoice creation workflow
    - Test save and load workflow
    - Test AI description generation workflow
    - Test PDF export workflow
    - _Requirements: All_

- [ ] 12. Implement error handling and logging
  - [ ] 12.1 Add error handling throughout application
    - Wrap AI service calls with try-catch and timeouts
    - Handle ChromaDB connection failures gracefully
    - Handle file system errors for logo and PDF operations
    - Validate AI outputs before using them
    - _Requirements: All_

  - [ ] 12.2 Add logging
    - Configure Python logging
    - Log errors and important operations
    - Log AI service calls and responses
    - _Requirements: All_

  - [ ] 12.3 Write unit tests for error handling
    - Test AI service failure scenarios
    - Test database connection failures
    - Test file system errors
    - _Requirements: All_

- [ ] 13. Create configuration and environment setup
  - [ ] 13.1 Create configuration module
    - Load environment variables (API keys, directories)
    - Provide default values for optional settings
    - Validate required configuration on startup
    - _Requirements: All_

  - [ ] 13.2 Create setup script
    - Initialize ChromaDB collections
    - Create required directories
    - Validate environment configuration
    - _Requirements: All_

  - [ ] 13.3 Write unit tests for configuration
    - Test environment variable loading
    - Test default value handling
    - Test validation of required settings
    - _Requirements: All_

- [ ] 14. Create example data and documentation
  - [ ] 14.1 Create sample data
    - Generate example business information
    - Generate example client data
    - Generate example invoices
    - _Requirements: All_

  - [ ] 14.2 Write README documentation
    - Installation instructions
    - Configuration guide
    - Usage examples
    - API documentation for key components
    - _Requirements: All_

- [ ] 15. Final checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.
