from src.mvp.main import MainModel, MainPresenter, MainView
from src.services import Logger

logger = Logger("Main")


def main() -> None:
    """Main application entry point."""
    try:
        # Create MVP components
        model = MainModel()
        view = MainView()
        presenter = MainPresenter(model, view)
        
        # Initialize application
        presenter.initialize_application()
        
        # Set up closing event
        def on_closing() -> None:
            presenter.on_application_closing()
            view.quit()
        view.protocol("WM_DELETE_WINDOW", on_closing)
        
        # Start the application
        view.mainloop()
        
    except Exception as e:
        logger.error(f"Application failed to start: {e}")
        raise


if __name__ == "__main__":
    main()
