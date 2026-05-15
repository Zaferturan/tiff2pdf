@echo off
REM Build Windows one-folder release (run from project root on Windows).
python -m pip install -r requirements.txt
if not exist vendor\tiff2pdf.exe (
    echo ERROR: vendor\tiff2pdf.exe missing. See vendor\README.txt
    exit /b 1
)
pyinstaller --noconfirm tiff2pdf.spec
echo.
echo Output: dist\Tiff2Pdf\Tiff2Pdf.exe
echo Copy the entire dist\Tiff2Pdf folder to target machines.
