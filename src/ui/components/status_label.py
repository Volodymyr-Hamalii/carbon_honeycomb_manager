"""Status label component for displaying application status messages."""

import customtkinter as ctk
from enum import Enum
from typing import Optional


class StatusType(Enum):
    """Status message types with associated colors."""
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"
    PROCESSING = "processing"


class StatusLabel(ctk.CTkFrame):
    """A sticky footer status label component for displaying status messages."""
    
    def __init__(self, parent: ctk.CTk | ctk.CTkFrame, **kwargs) -> None:
        super().__init__(parent, **kwargs)
        
        # Status colors
        self.status_colors = {
            StatusType.INFO: "#1f538d",      # Blue
            StatusType.SUCCESS: "#2d5a27",   # Green  
            StatusType.WARNING: "#8b5a00",   # Orange
            StatusType.ERROR: "#8b0000",     # Red
            StatusType.PROCESSING: "#4a4a4a" # Gray
        }
        
        # Default styling - start with minimum height
        self.configure(
            corner_radius=0,
            fg_color=self.status_colors[StatusType.INFO]
        )
        
        # Create main content frame
        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Create status label with wrapping
        self.status_label = ctk.CTkLabel(
            self.content_frame,
            text="Ready",
            font=ctk.CTkFont(size=12),
            text_color="white",
            wraplength=500,  # Wrap text at 500 pixels
            justify="left"
        )
        self.status_label.pack(pady=3, padx=5, side="left", fill="both", expand=True)
        
        # Create clear button
        self.clear_button = ctk.CTkButton(
            self.content_frame,
            text="Clear",
            width=60,
            height=24,
            font=ctk.CTkFont(size=10),
            command=self.clear_status
        )
        self.clear_button.pack(pady=3, padx=5, side="right")
        
    def set_status(self, message: str, status_type: StatusType = StatusType.INFO) -> None:
        """Set the status message and type."""
        self.status_label.configure(text=message)
        self.configure(fg_color=self.status_colors[status_type])
        
        # Dynamically adjust height based on message length
        self._adjust_height_for_message(message)
        
    def _adjust_height_for_message(self, message: str) -> None:
        """Adjust the height of the status label based on message length."""
        # Estimate number of lines needed based on message length and wrap length
        chars_per_line = 80  # Approximate characters per line at wrap length 500px
        estimated_lines: int = max(1, (len(message) + chars_per_line - 1) // chars_per_line)
        
        # Calculate height: base height + extra for additional lines
        base_height = 40
        line_height = 18
        new_height: int = base_height + (estimated_lines - 1) * line_height
        
        # Set minimum and maximum heights
        min_height = 40
        max_height = 120
        final_height: int = max(min_height, min(max_height, new_height))
        
        self.configure(height=final_height)
        
    def set_info(self, message: str) -> None:
        """Set an info status message."""
        self.set_status(message, StatusType.INFO)
        
    def set_success(self, message: str) -> None:
        """Set a success status message."""
        self.set_status(message, StatusType.SUCCESS)
        
    def set_warning(self, message: str) -> None:
        """Set a warning status message."""
        self.set_status(message, StatusType.WARNING)
        
    def set_error(self, message: str) -> None:
        """Set an error status message."""
        self.set_status(message, StatusType.ERROR)
        
    def set_processing(self, message: str) -> None:
        """Set a processing status message."""
        self.set_status(message, StatusType.PROCESSING)
        
    def clear_status(self) -> None:
        """Clear the status message."""
        self.set_status("Ready", StatusType.INFO)
        
    def get_current_message(self) -> str:
        """Get the current status message."""
        return self.status_label.cget("text")