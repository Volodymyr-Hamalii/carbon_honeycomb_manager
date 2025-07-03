import customtkinter as ctk


class PlotWindow(ctk.CTkToplevel):
    def __init__(
            self,
            master: ctk.CTkFrame | ctk.CTk,
            title: str = "Plot",
            **kwargs,
    ) -> None:
        super().__init__(master, **kwargs)
        self.title(title)
        self.geometry("1500x1500")

        # Placeholder for plot area
        self.plot_area: ctk.CTkLabel = ctk.CTkLabel(self, text="Plot will be displayed here")
        self.plot_area.pack(expand=True, fill='both')
