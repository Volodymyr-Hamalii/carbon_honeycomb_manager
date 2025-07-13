from typing import Any, Protocol
from src.interfaces import IGeneralPresenter, IGeneralView, IGeneralModel
from src.services import Logger


class GeneralPresenter(IGeneralPresenter):
    """General presenter with default logic."""
    
    def __init__(self, model: IGeneralModel, view: IGeneralView) -> None:
        self.model: IGeneralModel = model
        self.view: IGeneralView = view
        self.logger = Logger(self.__class__.__name__)
    
    def handle_error(self, operation: str, error: Exception) -> None:
        """Common error handling."""
        error_message = f"Failed to {operation}: {str(error)}"
        self.view.show_error_message(error_message)
        self.logger.error(error_message)
    
    def handle_success(self, operation: str, message: str | None = None) -> None:
        """Common success handling."""
        success_message = message or f"{operation.capitalize()} completed successfully"
        self.view.show_status_message(success_message)
        self.logger.info(success_message)
    
    def get_parameters(self) -> Any:
        """Get current parameters from model."""
        return self.model.get_mvp_params()
    
    def set_parameters(self, params: Any) -> None:
        """Set parameters in model."""
        self.model.set_mvp_params(params)
    
    def update_parameter(self, parameter_name: str, value: Any) -> None:
        """Update a single parameter."""
        params = self.get_parameters()
        setattr(params, parameter_name, value)
        self.set_parameters(params)
