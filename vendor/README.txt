Windows LibTIFF binaries for tiff2pdf
=====================================

Before building the release (or running on Windows), copy into this folder:

  tiff2pdf.exe
  libtiff-5.dll   (and any other DLLs required by your build)

Obtain them from a LibTIFF 4.7+ Windows build, for example:
  https://download.osgeo.org/libtiff/

Place all DLLs in the same directory as tiff2pdf.exe.

Development on Linux: install `tiff2pdf` on PATH, or place a Linux binary here as `tiff2pdf`.

These files are gitignored; do not commit large binaries unless you intend to.
