# Freelance Invoice Generator

A web-based application for creating professional invoices with AI-powered features.

## Features

- 📄 Professional invoice generation with customizable branding
- 🤖 AI-assisted service description generation (RAG + CrewAI)
- 💾 Persistent storage with ChromaDB
- 🔍 Semantic search over invoice history
- 📊 Automatic calculations (subtotals, taxes, discounts)
- 📤 PDF export functionality
- 🎨 User-friendly Gradio interface

## Installation

1. Clone the repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file based on `.env.example`:
```bash
cp .env.example .env
```

4. Add your OpenAI API key to the `.env` file

5. Run the setup script:
```bash
python setup.py
```

## Usage

### Quick Start

1. Make sure you have a `.env` file (copy from `.env.example` if needed)
2. Run the application:
```bash
python run_app.py
```

3. The app will automatically open in your browser at http://localhost:7860

### Features Available Now

✅ **Create Professional Invoices**
- Fill in business and client information
- Add up to 3 line items (easily expandable)
- Automatic calculation of subtotals, taxes, and totals
- Add payment methods and notes

✅ **Generate PDF**
- Click "Generate Invoice PDF" button
- Download professional PDF invoice
- Preview HTML version in the interface

✅ **Automatic Calculations**
- Line item amounts (quantity × rate)
- Subtotal (sum of all line items)
- Tax calculation based on percentage
- Discount application
- Final total calculation

## Project Structure

```
├── src/
│   ├── models/          # Data models
│   ├── services/        # Business logic
│   ├── repositories/    # Data access layer
│   ├── ai/             # AI services (RAG, CrewAI)
│   ├── ui/             # Gradio interface
│   └── config.py       # Configuration management
├── tests/              # Test suite
├── data/               # Data storage (created automatically)
│   ├── chroma/        # ChromaDB persistence
│   ├── logos/         # Uploaded logos
│   └── exports/       # Exported PDFs
└── requirements.txt    # Python dependencies
```

## Testing

Run tests:
```bash
pytest
```

Run tests with coverage:
```bash
pytest --cov=src
```

## License

MIT
