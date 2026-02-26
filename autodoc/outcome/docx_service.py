"""Define a docx templating service that allows for inline images."""

from io import BytesIO
from typing import Optional, Tuple

import requests
from docx.shared import Cm, Inches, Length, Mm
from docxtpl import DocxTemplate, InlineImage
from loguru import logger
from PIL import Image, ImageOps


class DocxTemplateService:
    """Define a Template rendering service, that allows for self referential inline images."""

    def __init__(self, document: DocxTemplate):
        """Initialise with the document template."""
        self.document = document

    def render(self, data: dict) -> None:
        """Render the given data to the document."""

        def get_width_and_height(**kwargs) -> Tuple[Optional[Length], Optional[Length]]:
            """Extract width and heights."""
            width = height = None

            if _width := kwargs.get("width_mm"):
                width = Mm(_width)

            if _width := kwargs.get("width_cm"):
                width = Cm(_width)

            if _width := kwargs.get("width_inches"):
                width = Inches(_width)

            if _height := kwargs.get("height_mm"):
                height = Mm(_height)

            if _height := kwargs.get("height_cm"):
                height = Cm(_height)

            if _height := kwargs.get("height_inches"):
                height = Inches(_height)

            return width, height

        def fetch_inline_image_file(file_path: str, **kwargs) -> InlineImage:

            with open(file_path, "rb") as f:
                file_binary = f.read()

            file_stream = normalize_image_for_word(file_binary)

            width, height = get_width_and_height(**kwargs)
            return InlineImage(self.document, file_stream, width=width, height=height)

        def fetch_inline_image_url(url: str, **kwargs) -> InlineImage:

            logger.info(f"Processing Image URL: {url}")

            response = requests.get(url)
            response.raise_for_status()

            image_stream = normalize_image_for_word(response.content)

            width, height = get_width_and_height(**kwargs)
            return InlineImage(self.document, image_stream, width=width, height=height)

        data["_image_file"] = fetch_inline_image_file
        data["_image_url"] = fetch_inline_image_url

        self.document.render(data)


PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


def normalize_image_for_word(data: bytes) -> BytesIO:
    """If image is already PNG: return as-is, otherwise: normalize and re-encode."""
    if data.startswith(PNG_SIGNATURE):
        return BytesIO(data)

    stream = BytesIO(data)
    stream.seek(0)

    with Image.open(stream) as img:
        img = ImageOps.exif_transpose(img)

        has_alpha = img.mode in ("RGBA", "LA") or (img.mode == "P" and "transparency" in img.info)

        out = BytesIO()

        if has_alpha:
            img.save(out, format="PNG")
        else:
            img = img.convert("RGB")
            img.save(
                out,
                format="JPEG",
                quality=95,
                subsampling=0,
                optimize=True,
            )

    out.seek(0)
    return out
