"""Launch the Gradio invoice generator app"""
from src.ui.app import create_ui

if __name__ == "__main__":
    print("Starting Freelance Invoice Generator...")
    print("The app will open in your browser automatically.")
    print("Press Ctrl+C to stop the server.")
    
    app = create_ui()
    app.launch(
        server_name="127.0.0.1",
        server_port=7860,
        share=False
    )
