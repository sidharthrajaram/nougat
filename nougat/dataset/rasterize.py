"""
Copyright (c) Meta Platforms, Inc. and affiliates.

This source code is licensed under the MIT license found in the
LICENSE file in the root directory of this source tree.
"""
import argparse
# import fitz
import logging
from pathlib import Path
from pdf2image import convert_from_path
from pdf2image.exceptions import (
    PDFInfoNotInstalledError,
    PDFPageCountError,
    PDFSyntaxError
)
from tqdm import tqdm
import io
from typing import Optional, List, Union


def rasterize_paper(
    pdf: Union[Path, bytes],
    outpath: Optional[Path] = None,
    dpi: int = 200,
    return_pil=False,
    pages=None,
) -> Optional[List[io.BytesIO]]:
    """
    Rasterize a PDF file to PNG images.

    Args:
        pdf (Path): The path to the PDF file.
        outpath (Optional[Path], optional): The output directory. If None, the PIL images will be returned instead. Defaults to None.
        dpi (int, optional): The output DPI. Defaults to 96.
        return_pil (bool, optional): Whether to return the PIL images instead of writing them to disk. Defaults to False.
        pages (Optional[List[int]], optional): The pages to rasterize. If None, all pages will be rasterized. Defaults to None.

    Returns:
        Optional[List[io.BytesIO]]: The PIL images if `return_pil` is True, otherwise None.
    """
    pils = []
    if outpath is None:
        return_pil = True
    try:
        # TODO: add logic for pdf is the file itself (app.py)
        if isinstance(pdf, (str, Path)):
            # pdf_doc = fitz.open(pdf)
            page_images = convert_from_path(pdf, dpi=dpi, use_pdftocairo=True)
            print(len(page_images))
            print(page_images)
        else:
            logging.info("Provided file path is not a PDF.")
        if pages is None:
            pages = range(len(page_images))
        for i in pages:
            # pix = page_images[i].get_pixmap(dpi=dpi)
            # image = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
            if return_pil:
                page_bytes = io.BytesIO()
                page_images[i].save(page_bytes, "bmp")
                pils.append(page_bytes)
            # else:
                # page_images[i].save(f"image_{i+1}.png")
                # page_images[i].save((outpath / ("%02d.png" % (i + 1))), "png")
    except Exception as e:
        logging.error(e)
    if return_pil:
        return pils


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--pdfs", nargs="+", type=Path, help="PDF files", required=True)
    parser.add_argument("--out", type=Path, help="Output dir", default=None)
    parser.add_argument(
        "--dpi", type=int, default=96, help="What resolution the pages will be saved"
    )
    parser.add_argument(
        "--pages", type=int, nargs="+", default=None, help="list of page numbers"
    )
    args = parser.parse_args()
    if args.pages:
        args.pages = [p - 1 for p in args.pages]
    for pdf_file in tqdm(args.pdfs):
        assert pdf_file.exists() and pdf_file.is_file()
        outpath: Path = args.out or (pdf_file.parent / pdf_file.stem)
        outpath.mkdir(exist_ok=True)
        rasterize_paper(pdf_file, outpath, pages=args.pages, dpi=args.dpi)
