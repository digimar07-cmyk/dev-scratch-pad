"""LASERFLIX - Entry Point

Netflix-style project manager for laser cutting designs.
Refactored following Martin Fowler and Kent Beck principles.
"""
import tkinter as tk
from laserflix_tkinter import setup_logging
from laserflix_tkinter.app import LaserflixApp


def main():
    """Application entry point."""
    # Setup logging
    logger = setup_logging()
    logger.info("="*60)
    logger.info("LASERFLIX Starting...")
    logger.info("="*60)
    
    # Create root window
    root = tk.Tk()
    
    # Create application
    app = LaserflixApp(root)
    
    # Start event loop
    try:
        root.mainloop()
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
    except Exception as e:
        logger.exception("Application crashed: %s", e)
    finally:
        logger.info("LASERFLIX Shutting down...")


if __name__ == "__main__":
    main()
