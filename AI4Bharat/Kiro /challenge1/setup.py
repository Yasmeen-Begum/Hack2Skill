"""Setup script for the Freelance Invoice Generator"""
from src.config import Config


def setup():
    """Initialize the application"""
    print("Setting up Freelance Invoice Generator...")
    
    # Validate configuration
    errors = Config.validate()
    if errors:
        print("\nConfiguration errors:")
        for error in errors:
            print(f"  - {error}")
        print("\nPlease create a .env file based on .env.example")
        return False
    
    # Create directories
    Config.create_directories()
    print(f"✓ Created directory: {Config.CHROMA_PERSIST_DIR}")
    print(f"✓ Created directory: {Config.INVOICE_LOGO_DIR}")
    print(f"✓ Created directory: {Config.INVOICE_EXPORT_DIR}")
    
    # Initialize ChromaDB
    from src.repositories.chroma_repository import ChromaDBRepository
    repo = ChromaDBRepository()
    print("✓ Initialized ChromaDB collections")
    
    print("\nSetup complete! You can now run the application.")
    return True


if __name__ == "__main__":
    setup()
