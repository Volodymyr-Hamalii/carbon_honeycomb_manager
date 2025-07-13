import customtkinter as ctk

from src.interfaces import IGeneralView, IGeneralPresenter


class GeneralView(ctk.CTk, IGeneralView):
    """ General view with default logic. """
    presenter: IGeneralPresenter

    def set_presenter(self, presenter: IGeneralPresenter) -> None:
        self.presenter: IGeneralPresenter = presenter
