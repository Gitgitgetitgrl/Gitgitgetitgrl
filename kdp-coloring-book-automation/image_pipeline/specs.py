"""Print specification constants (from the finalized Print Guidelines).

Single source of truth for trim sizes, bleed math, resolution, and margins used
by apply_bleed.py and build_interior_pdf.py. Values match docs/print-guidelines.md.
"""
from dataclasses import dataclass

DPI = 300                      # required minimum resolution
BLEED_IN = 0.125               # 1/8" bleed rule
MIN_OUTER_MARGIN_IN = 0.25     # non-bleed outer margin minimum


@dataclass(frozen=True)
class Format:
    name: str
    trim_w_in: float
    trim_h_in: float
    bleed: bool

    @property
    def pdf_w_in(self) -> float:
        # KDP full-bleed adds 0.125" on the outside edges only.
        # Square print bleed page: 8.5 + 0.125 = 8.625 wide.
        return round(self.trim_w_in + (BLEED_IN if self.bleed else 0), 3)

    @property
    def pdf_h_in(self) -> float:
        # Height adds bleed top AND bottom: 8.5 + 0.25 = 8.75 tall.
        return round(self.trim_h_in + (2 * BLEED_IN if self.bleed else 0), 3)

    def px(self, inches: float) -> int:
        return round(inches * DPI)


# The three finalized output formats.
PRINT_SQUARE_NONBLEED = Format("print_square_nonbleed", 8.5, 8.5, bleed=False)
PRINT_SQUARE_BLEED = Format("print_square_bleed", 8.5, 8.5, bleed=True)
EBOOK = Format("ebook", 8.5, 11.0, bleed=False)

FORMATS = {f.name: f for f in (PRINT_SQUARE_NONBLEED, PRINT_SQUARE_BLEED, EBOOK)}

# Sanity checks matching the guideline table (8.625 x 8.75 bleed PDF).
assert PRINT_SQUARE_BLEED.pdf_w_in == 8.625
assert PRINT_SQUARE_BLEED.pdf_h_in == 8.75
assert PRINT_SQUARE_NONBLEED.pdf_w_in == 8.5
assert EBOOK.pdf_h_in == 11.0
