import customtkinter as ctk
import pandas as pd
import tkinter as tk

from src.ui.styles import get_component_style, ComponentStyle, get_color_safe


class Table(ctk.CTkFrame):
    def __init__(
            self,
            data: pd.DataFrame,
            master: ctk.CTk | ctk.CTkToplevel,
            title: str = "",
            to_show_index: bool = True,
            **kwargs,
    ) -> None:
        super().__init__(master, **kwargs)

        # Apply centralized styles
        style: ComponentStyle = get_component_style("table")
        bg_color: str = get_color_safe("table", "bg_color")
        header_bg_color: str = get_color_safe("table", "header_bg_color")
        text_color: str = get_color_safe("table", "text_color")
        alt_row_color: str = get_color_safe("table", "alt_row_color")
        border_color: str = get_color_safe("table", "border_color")
        
        # Font configuration
        cell_font_size: int = style.font.get("size", 9)
        header_font_size: int = style.font.get("header_size", 10)
        font_family: str = style.font.get("family", "Arial")
        
        # Spacing configuration
        cell_padx: int = style.spacing.get("padx", 1)
        cell_pady: int = style.spacing.get("pady", 1)

        # Set the background color for the entire table
        self.configure(bg_color=bg_color)

        if title:
            # Create a label for the title using grid
            title_label = ctk.CTkLabel(self, text=title, bg_color=bg_color, fg_color=bg_color)
            title_label.grid(row=0, column=0, columnspan=len(data.columns) + (1 if to_show_index else 0), sticky="ew")

        # Create a canvas to hold the table and scrollbars
        canvas = ctk.CTkCanvas(self, bg=bg_color)
        canvas.grid(row=1, column=0, sticky="nsew")

        # Add scrollbars
        v_scrollbar = ctk.CTkScrollbar(self, orientation='vertical', command=canvas.yview)
        v_scrollbar.grid(row=1, column=1, sticky='ns')
        h_scrollbar = ctk.CTkScrollbar(self, orientation='horizontal', command=canvas.xview)
        h_scrollbar.grid(row=2, column=0, sticky='ew')

        canvas.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

        # Create a frame inside the canvas
        table_frame = ctk.CTkFrame(canvas, bg_color=bg_color)
        canvas.create_window((0, 0), window=table_frame, anchor='nw')

        # Calculate column widths based on content
        col_widths: list[int] = []
        for col in data.columns:
            if isinstance(col, tuple):
                # Only consider the last level of the MultiIndex for width calculation
                max_content_width: int = max(
                    data[col].astype(str).apply(len).max(),
                    len(str(col[-1]))  # Use the last level of the MultiIndex
                )
            else:
                max_content_width = max(data[col].astype(str).apply(len).max(), len(str(col)))

            col_widths.append(max_content_width + 2)  # Add small padding

        # Add index width
        index_width: int = max(data.index.map(lambda x: len(str(x))).max(), len("Index")) + 2

        # Handle MultiIndex columns
        if isinstance(data.columns, pd.MultiIndex):
            # Create headers for each level of the MultiIndex
            for level in range(data.columns.nlevels):
                col_start = 0
                while col_start < len(data.columns):
                    col_end = col_start
                    # Find the range of columns with the same top-level header
                    while (col_end + 1 < len(data.columns) and
                           data.columns[col_start][0] == data.columns[col_end + 1][0]):
                        col_end += 1

                    # Create a header for the top-level
                    if level == 0:
                        header_frame = ctk.CTkFrame(table_frame, bg_color=border_color)
                        header_frame.grid(
                            row=level,
                            column=col_start + (1 if to_show_index else 0),
                            columnspan=(col_end - col_start + 1),
                            sticky="nsew",
                            padx=cell_padx,
                            pady=cell_pady,
                        )
                        header = tk.Text(
                            header_frame,
                            height=1,
                            width=sum(col_widths[col_start:col_end + 1]),
                            font=(font_family, header_font_size, "bold"),  # Bold font for headers
                            bg=header_bg_color,  # Use theme-based header background color
                            fg=text_color,  # Use theme-based text color
                            bd=0,  # No border
                            highlightthickness=0,  # No highlight border
                            wrap="none"  # No text wrapping
                        )
                        header.insert("1.0", data.columns[col_start][0])
                        header.tag_configure("center", justify='center')
                        header.tag_add("center", "1.0", "end")
                        header.config(state="disabled")  # Make the text read-only
                        header.pack(fill="both", expand=True)

                    # Create headers for the second level
                    for col in range(col_start, col_end + 1):
                        header_frame = ctk.CTkFrame(table_frame, bg_color=border_color)
                        header_frame.grid(
                            row=level + 1,
                            column=col + (1 if to_show_index else 0),
                            sticky="nsew",
                            padx=cell_padx,
                            pady=cell_pady,
                        )
                        header = tk.Text(
                            header_frame,
                            height=1,
                            width=col_widths[col],
                            font=(font_family, header_font_size, "bold"),  # Bold font for headers
                            bg=header_bg_color,  # Use theme-based header background color
                            fg=text_color,  # Use theme-based text color
                            bd=0,  # No border
                            highlightthickness=0,  # No highlight border
                            wrap="none"  # No text wrapping
                        )
                        header.insert("1.0", data.columns[col][1])
                        header.tag_configure("center", justify='center')
                        header.tag_add("center", "1.0", "end")
                        header.config(state="disabled")  # Make the text read-only
                        header.pack(fill="both", expand=True)

                    col_start = col_end + 1
        else:
            # Create a single row of headers
            for i, column in enumerate(data.columns):
                header_frame = ctk.CTkFrame(table_frame, bg_color=border_color)
                header_frame.grid(row=0, column=i + (1 if to_show_index else 0), sticky="nsew", padx=cell_padx, pady=cell_pady)
                header = tk.Text(
                    header_frame,
                    height=1,
                    width=col_widths[i],
                    font=("Arial", 10, "bold"),  # Bold font for headers
                    bg=header_bg_color,  # Use theme-based header background color
                    fg=text_color,  # Use theme-based text color
                    bd=0,  # No border
                    highlightthickness=0,  # No highlight border
                    wrap="none"  # No text wrapping
                )
                header.insert("1.0", column)
                header.tag_configure("center", justify='center')
                header.tag_add("center", "1.0", "end")
                header.config(state="disabled")  # Make the text read-only
                header.pack(fill="both", expand=True)

        # Create the table cells
        for i, (index, row) in enumerate(data.iterrows()):
            # Determine the background color for the row
            row_bg_color: str = bg_color if i % 2 == 0 else alt_row_color

            # Add index cell only if to_show_index is True
            if to_show_index:
                index_frame = ctk.CTkFrame(table_frame, bg_color=border_color)
                index_frame.grid(row=i + data.columns.nlevels, column=0, sticky="nsew", padx=cell_padx, pady=cell_pady)
                index_cell = tk.Text(
                    index_frame,
                    height=1,
                    width=index_width,
                    font=(font_family, cell_font_size),  # Cell font
                    bg=header_bg_color,  # Use theme-based index cell background color
                    fg=text_color,  # Use theme-based text color
                    bd=0,  # No border
                    highlightthickness=0,  # No highlight border
                    wrap="none"  # No text wrapping
                )
                index_cell.insert("1.0", str(index))
                index_cell.tag_configure("center", justify='center')
                index_cell.tag_add("center", "1.0", "end")
                index_cell.config(state="disabled")  # Make the text read-only
                index_cell.pack(fill="both", expand=True)

            for j, value in enumerate(row):
                # Adjust column index if index column is not shown
                col_index = j + 1 if to_show_index else j
                cell_frame = ctk.CTkFrame(table_frame, bg_color=border_color)
                cell_frame.grid(row=i + data.columns.nlevels, column=col_index, sticky="nsew", padx=cell_padx, pady=cell_pady)
                cell = tk.Text(
                    cell_frame,
                    height=1,
                    width=col_widths[j],
                    font=(font_family, cell_font_size),  # Cell font
                    bg=row_bg_color,  # Use theme-based row background color
                    fg=text_color,  # Use theme-based text color
                    bd=0,  # No border
                    highlightthickness=0,  # No highlight border
                    wrap="none"  # No text wrapping
                )
                cell.insert("1.0", str(value))
                cell.tag_configure("center", justify='center')
                cell.tag_add("center", "1.0", "end")
                cell.config(state="disabled")  # Make the text read-only
                cell.pack(fill="both", expand=True)

        # Make the table adaptive
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Update scroll region
        table_frame.update_idletasks()
        canvas.config(scrollregion=canvas.bbox("all"))
