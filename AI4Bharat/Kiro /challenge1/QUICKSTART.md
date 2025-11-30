# Quick Start Guide

## Get Your Invoice Generator Running in 3 Steps!

### Step 1: Install Dependencies (if not done already)
```bash
pip install -r requirements.txt
```

### Step 2: Run the Application
```bash
python run_app.py
```

### Step 3: Create Your First Invoice!

The app will open in your browser automatically. You'll see a form with:

1. **Business Information** - Your freelance business details
2. **Client Information** - Who you're billing
3. **Invoice Details** - Invoice number and date
4. **Line Items** - Services you provided (up to 3 items)
5. **Totals** - Tax rate and discount
6. **Payment & Notes** - How clients can pay you

Fill in the form and click **"Generate Invoice PDF"** to:
- ✅ Get a professional PDF invoice
- ✅ See an HTML preview
- ✅ Download the PDF to send to your client

## Example Invoice

The form comes pre-filled with example data so you can generate a sample invoice immediately!

## Where Are My PDFs?

All generated PDFs are saved in: `./data/exports/`

## Tips

- **Invoice Numbers**: Use a consistent format like "INV-001", "INV-002", etc.
- **Payment Terms**: Common values are 14, 30, or 60 days
- **Tax Rate**: Enter as a percentage (e.g., 10 for 10%)
- **Line Items**: Leave Description 3 empty if you only need 2 items

## What's Next?

This is a working MVP! Future features will include:
- 🤖 AI-powered description generation
- 💾 Save and retrieve invoices from database
- 🔍 Search past invoices
- 📊 Invoice history and analytics
- 🎨 Logo upload support

## Need Help?

Check the main README.md for more detailed information.
