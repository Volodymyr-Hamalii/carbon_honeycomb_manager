"""Mixin class to enable touchpad scrolling for CustomTkinter components."""

import tkinter as tk
import customtkinter as ctk
from typing import Union, Optional, Any


class ScrollableMixin:
    """Mixin to add touchpad/mouse wheel scrolling support to widgets."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._scrollable_widgets: list[Union[ctk.CTkCanvas, ctk.CTkScrollableFrame]] = []

    def enable_touchpad_scrolling(self) -> None:
        """Enable touchpad scrolling for all scrollable components in this window."""
        # Type ignore needed for mixin's after method
        self.after(100, self._setup_scrolling)  # type: ignore
        
    def refresh_scrolling(self) -> None:
        """Refresh scrolling setup - useful after UI changes."""
        self._setup_scrolling()

    def _setup_scrolling(self) -> None:
        """Set up scrolling for all scrollable widgets found in the window."""
        self._find_scrollable_widgets(self)

        for widget in self._scrollable_widgets:
            self._bind_mousewheel_to_widget(widget)
            self._bind_keyboard_to_widget(widget)
            
        # Set the first scrollable widget as the default focused widget for keyboard scrolling
        if self._scrollable_widgets and (not hasattr(self, '_focused_scrollable_widget') or self._focused_scrollable_widget is None):
            # Prioritize CTkScrollableFrame over CTkCanvas
            main_scrollable = None
            for widget in self._scrollable_widgets:
                if isinstance(widget, ctk.CTkScrollableFrame):
                    main_scrollable = widget
                    break
            if not main_scrollable and self._scrollable_widgets:
                main_scrollable = self._scrollable_widgets[0]
            
            if main_scrollable:
                self._focused_scrollable_widget = main_scrollable  # type: ignore

    def _find_scrollable_widgets(self, parent: tk.Widget) -> None:
        """Recursively find all scrollable widgets in the window."""
        for child in parent.winfo_children():
            # Check for CTkScrollableFrame
            if isinstance(child, ctk.CTkScrollableFrame):
                self._scrollable_widgets.append(child)
                # CTkScrollableFrame has an internal canvas
                canvas = self._get_scrollable_frame_canvas(child)
                if canvas:
                    self._scrollable_widgets.append(canvas)

            # Check for CTkCanvas (used in Tables) but exclude small canvases that are part of input widgets
            elif isinstance(child, ctk.CTkCanvas):
                # Only include canvas if it's likely a main content area, not an input widget canvas
                if self._is_main_canvas(child):
                    self._scrollable_widgets.append(child)

            # Recursively search children
            self._find_scrollable_widgets(child)

    def _is_main_canvas(self, canvas: ctk.CTkCanvas) -> bool:
        """Check if a canvas is a main scrollable area, not part of an input widget."""
        try:
            # Get canvas dimensions
            width = canvas.winfo_reqwidth()
            height = canvas.winfo_reqheight()
            
            # Small canvases (typically < 100px in either dimension) are usually part of input widgets
            # Main scrollable canvases are typically much larger
            if width < 100 or height < 100:
                return False
                
            # Check parent hierarchy - if parent is an input widget, exclude this canvas
            parent = canvas.master
            while parent:
                parent_class = parent.__class__.__name__
                if any(name in parent_class for name in [
                    'InputField', 'Entry', 'Button', 'CheckBox', 'ComboBox', 
                    'Dropdown', 'Slider', 'Switch', 'Label'
                ]):
                    return False
                parent = getattr(parent, 'master', None)
                
            return True
        except (AttributeError, tk.TclError):
            return False

    def _get_scrollable_frame_canvas(self, scrollable_frame: ctk.CTkScrollableFrame) -> Optional[ctk.CTkCanvas]:
        """Get the internal canvas from a CTkScrollableFrame."""
        try:
            # CTkScrollableFrame has a _parent_canvas attribute
            if hasattr(scrollable_frame, '_parent_canvas'):
                return scrollable_frame._parent_canvas  # type: ignore
            # Alternative: check for _canvas attribute
            elif hasattr(scrollable_frame, '_canvas'):
                return scrollable_frame._canvas  # type: ignore
        except AttributeError:
            pass
        return None

    def _bind_mousewheel_to_widget(self, widget: Union[ctk.CTkCanvas, ctk.CTkScrollableFrame]) -> None:
        """Bind mouse wheel events to a specific widget."""
        def _on_mousewheel(event: tk.Event) -> str:
            """Handle vertical mouse wheel scrolling."""
            try:
                if isinstance(widget, ctk.CTkScrollableFrame):
                    # For CTkScrollableFrame, get the internal canvas
                    canvas = self._get_scrollable_frame_canvas(widget)
                    if canvas:
                        canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
                elif isinstance(widget, ctk.CTkCanvas):
                    # For CTkCanvas, use its scroll method
                    widget.yview_scroll(int(-1 * (event.delta / 120)), "units")
            except (AttributeError, tk.TclError):
                # Ignore errors if scrolling is not available
                pass
            return "break"

        def _on_shift_mousewheel(event: tk.Event) -> str:
            """Handle horizontal mouse wheel scrolling."""
            try:
                if isinstance(widget, ctk.CTkScrollableFrame):
                    # CTkScrollableFrame typically doesn't have horizontal scrolling
                    pass
                elif isinstance(widget, ctk.CTkCanvas):
                    # For CTkCanvas, use horizontal scroll
                    widget.xview_scroll(int(-1 * (event.delta / 120)), "units")
            except (AttributeError, tk.TclError):
                # Ignore errors if scrolling is not available
                pass
            return "break"

        # Linux support
        def _on_button_4(event: tk.Event) -> str:
            """Handle Linux scroll up."""
            try:
                if isinstance(widget, ctk.CTkScrollableFrame):
                    canvas = self._get_scrollable_frame_canvas(widget)
                    if canvas:
                        canvas.yview_scroll(-1, "units")
                elif isinstance(widget, ctk.CTkCanvas):
                    widget.yview_scroll(-1, "units")
            except (AttributeError, tk.TclError):
                pass
            return "break"

        def _on_button_5(event: tk.Event) -> str:
            """Handle Linux scroll down."""
            try:
                if isinstance(widget, ctk.CTkScrollableFrame):
                    canvas = self._get_scrollable_frame_canvas(widget)
                    if canvas:
                        canvas.yview_scroll(1, "units")
                elif isinstance(widget, ctk.CTkCanvas):
                    widget.yview_scroll(1, "units")
            except (AttributeError, tk.TclError):
                pass
            return "break"

        def _on_shift_button_4(event: tk.Event) -> str:
            """Handle Linux horizontal scroll left."""
            try:
                if isinstance(widget, ctk.CTkCanvas):
                    widget.xview_scroll(-1, "units")
            except (AttributeError, tk.TclError):
                pass
            return "break"

        def _on_shift_button_5(event: tk.Event) -> str:
            """Handle Linux horizontal scroll right."""
            try:
                if isinstance(widget, ctk.CTkCanvas):
                    widget.xview_scroll(1, "units")
            except (AttributeError, tk.TclError):
                pass
            return "break"

        # Bind scroll events directly to the scrollable widget instead of using global bind_all
        # This prevents input fields from triggering scrolling
        widget.bind("<MouseWheel>", _on_mousewheel)
        widget.bind("<Shift-MouseWheel>", _on_shift_mousewheel)
        widget.bind("<Button-4>", _on_button_4)
        widget.bind("<Button-5>", _on_button_5)
        widget.bind("<Shift-Button-4>", _on_shift_button_4)
        widget.bind("<Shift-Button-5>", _on_shift_button_5)
        
        # Set this widget as focused for keyboard scrolling when mouse enters it
        # (but only main scrollable widgets should reach this point due to filtering)
        def _set_focus_on_enter(event: tk.Event) -> None:
            """Set this scrollable widget as focused when mouse enters."""
            self._focused_scrollable_widget = widget  # type: ignore
        
        widget.bind("<Enter>", _set_focus_on_enter)

    def _bind_keyboard_to_widget(self, widget: Union[ctk.CTkCanvas, ctk.CTkScrollableFrame]) -> None:
        """Bind keyboard arrow keys and page navigation for scrolling."""
        def _on_key_up(event: tk.Event) -> str:
            """Handle Up arrow key."""
            try:
                if isinstance(widget, ctk.CTkScrollableFrame):
                    canvas = self._get_scrollable_frame_canvas(widget)
                    if canvas:
                        canvas.yview_scroll(-1, "units")
                elif isinstance(widget, ctk.CTkCanvas):
                    widget.yview_scroll(-1, "units")
            except (AttributeError, tk.TclError):
                pass
            return "break"
        
        def _on_key_down(event: tk.Event) -> str:
            """Handle Down arrow key."""
            try:
                if isinstance(widget, ctk.CTkScrollableFrame):
                    canvas = self._get_scrollable_frame_canvas(widget)
                    if canvas:
                        canvas.yview_scroll(1, "units")
                elif isinstance(widget, ctk.CTkCanvas):
                    widget.yview_scroll(1, "units")
            except (AttributeError, tk.TclError):
                pass
            return "break"
        
        def _on_key_left(event: tk.Event) -> str:
            """Handle Left arrow key."""
            try:
                if isinstance(widget, ctk.CTkCanvas):
                    widget.xview_scroll(-1, "units")
            except (AttributeError, tk.TclError):
                pass
            return "break"
        
        def _on_key_right(event: tk.Event) -> str:
            """Handle Right arrow key."""
            try:
                if isinstance(widget, ctk.CTkCanvas):
                    widget.xview_scroll(1, "units")
            except (AttributeError, tk.TclError):
                pass
            return "break"
        
        def _on_page_up(event: tk.Event) -> str:
            """Handle Page Up key."""
            try:
                if isinstance(widget, ctk.CTkScrollableFrame):
                    canvas = self._get_scrollable_frame_canvas(widget)
                    if canvas:
                        canvas.yview_scroll(-10, "units")
                elif isinstance(widget, ctk.CTkCanvas):
                    widget.yview_scroll(-10, "units")
            except (AttributeError, tk.TclError):
                pass
            return "break"
        
        def _on_page_down(event: tk.Event) -> str:
            """Handle Page Down key."""
            try:
                if isinstance(widget, ctk.CTkScrollableFrame):
                    canvas = self._get_scrollable_frame_canvas(widget)
                    if canvas:
                        canvas.yview_scroll(10, "units")
                elif isinstance(widget, ctk.CTkCanvas):
                    widget.yview_scroll(10, "units")
            except (AttributeError, tk.TclError):
                pass
            return "break"
        
        # Store the current focused widget for keyboard scrolling
        if not hasattr(self, '_focused_scrollable_widget'):
            self._focused_scrollable_widget = None  # type: ignore
        
        def _on_widget_click(event: tk.Event) -> None:
            """Set this widget as the focused scrollable widget when clicked."""
            self._focused_scrollable_widget = widget  # type: ignore
        
        def _on_widget_enter(event: tk.Event) -> None:
            """Set this widget as focused when mouse enters."""
            self._focused_scrollable_widget = widget  # type: ignore
        
        # Bind click and enter events to set focus
        try:
            widget.bind("<Button-1>", _on_widget_click, add="+")
            widget.bind("<Enter>", _on_widget_enter, add="+")
        except (AttributeError, tk.TclError):
            pass
        
        # Set up global keyboard handlers if not already done
        if not hasattr(self, '_keyboard_bindings_set'):
            self._setup_global_keyboard_handlers()
            self._keyboard_bindings_set = True  # type: ignore

    def _setup_global_keyboard_handlers(self) -> None:
        """Set up global keyboard handlers for all scrollable widgets."""
        
        def _handle_up_key(event: tk.Event) -> str:
            """Handle global Up arrow key."""
            if hasattr(self, '_focused_scrollable_widget') and self._focused_scrollable_widget:  # type: ignore
                widget = self._focused_scrollable_widget  # type: ignore
                try:
                    if isinstance(widget, ctk.CTkScrollableFrame):
                        canvas = self._get_scrollable_frame_canvas(widget)
                        if canvas:
                            canvas.yview_scroll(-1, "units")
                    elif isinstance(widget, ctk.CTkCanvas):
                        widget.yview_scroll(-1, "units")
                    return "break"
                except (AttributeError, tk.TclError):
                    pass
            return "continue"
        
        def _handle_down_key(event: tk.Event) -> str:
            """Handle global Down arrow key."""
            if hasattr(self, '_focused_scrollable_widget') and self._focused_scrollable_widget:  # type: ignore
                widget = self._focused_scrollable_widget  # type: ignore
                try:
                    if isinstance(widget, ctk.CTkScrollableFrame):
                        canvas = self._get_scrollable_frame_canvas(widget)
                        if canvas:
                            canvas.yview_scroll(1, "units")
                    elif isinstance(widget, ctk.CTkCanvas):
                        widget.yview_scroll(1, "units")
                    return "break"
                except (AttributeError, tk.TclError):
                    pass
            return "continue"
        
        def _handle_left_key(event: tk.Event) -> str:
            """Handle global Left arrow key."""
            if hasattr(self, '_focused_scrollable_widget') and self._focused_scrollable_widget:  # type: ignore
                widget = self._focused_scrollable_widget  # type: ignore
                try:
                    if isinstance(widget, ctk.CTkCanvas):
                        widget.xview_scroll(-1, "units")
                        return "break"
                except (AttributeError, tk.TclError):
                    pass
            return "continue"
        
        def _handle_right_key(event: tk.Event) -> str:
            """Handle global Right arrow key."""
            if hasattr(self, '_focused_scrollable_widget') and self._focused_scrollable_widget:  # type: ignore
                widget = self._focused_scrollable_widget  # type: ignore
                try:
                    if isinstance(widget, ctk.CTkCanvas):
                        widget.xview_scroll(1, "units")
                        return "break"
                except (AttributeError, tk.TclError):
                    pass
            return "continue"
        
        def _handle_page_up_key(event: tk.Event) -> str:
            """Handle global Page Up key."""
            if hasattr(self, '_focused_scrollable_widget') and self._focused_scrollable_widget:  # type: ignore
                widget = self._focused_scrollable_widget  # type: ignore
                try:
                    if isinstance(widget, ctk.CTkScrollableFrame):
                        canvas = self._get_scrollable_frame_canvas(widget)
                        if canvas:
                            canvas.yview_scroll(-10, "units")
                    elif isinstance(widget, ctk.CTkCanvas):
                        widget.yview_scroll(-10, "units")
                    return "break"
                except (AttributeError, tk.TclError):
                    pass
            return "continue"
        
        def _handle_page_down_key(event: tk.Event) -> str:
            """Handle global Page Down key."""
            if hasattr(self, '_focused_scrollable_widget') and self._focused_scrollable_widget:  # type: ignore
                widget = self._focused_scrollable_widget  # type: ignore
                try:
                    if isinstance(widget, ctk.CTkScrollableFrame):
                        canvas = self._get_scrollable_frame_canvas(widget)
                        if canvas:
                            canvas.yview_scroll(10, "units")
                    elif isinstance(widget, ctk.CTkCanvas):
                        widget.yview_scroll(10, "units")
                    return "break"
                except (AttributeError, tk.TclError):
                    pass
            return "continue"
        
        # Bind global keyboard events
        try:
            self.bind_all("<Up>", _handle_up_key)  # type: ignore
            self.bind_all("<Down>", _handle_down_key)  # type: ignore
            self.bind_all("<Left>", _handle_left_key)  # type: ignore
            self.bind_all("<Right>", _handle_right_key)  # type: ignore
            self.bind_all("<Prior>", _handle_page_up_key)  # type: ignore
            self.bind_all("<Next>", _handle_page_down_key)  # type: ignore
        except (AttributeError, tk.TclError):
            pass


class ScrollableWindow(ScrollableMixin, ctk.CTk):
    """A CTk window with automatic touchpad scrolling support."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        # Enable scrolling after the window is created
        self.after(200, self.enable_touchpad_scrolling)


class ScrollableToplevel(ScrollableMixin, ctk.CTkToplevel):
    """A CTkToplevel window with automatic touchpad scrolling support."""

    def __init__(self, master: Optional[Any] = None, **kwargs: Any) -> None:
        super().__init__(master, **kwargs)
        # Enable scrolling after the window is created
        self.after(200, self.enable_touchpad_scrolling)
