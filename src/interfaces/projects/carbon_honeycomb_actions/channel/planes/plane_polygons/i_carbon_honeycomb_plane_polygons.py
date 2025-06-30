from src.interfaces.entities.figures.i_flat_figure import IFlatFigure

__all__: list[str] = [
    "ICarbonHoneycombPolygon",
    "ICarbonHoneycombHexagon",
    "ICarbonHoneycombPentagon",
]


class ICarbonHoneycombPolygon(IFlatFigure):
    pass


class ICarbonHoneycombHexagon(ICarbonHoneycombPolygon):
    pass


class ICarbonHoneycombPentagon(ICarbonHoneycombPolygon):
    pass
