@echo off
REM Build Windows single-exe release (run from project root on Windows).
python -m pip install -r requirements.txt
if not exist vendor\tiff2pdf.exe (
    echo ERROR: vendor\tiff2pdf.exe missing. See vendor\README.txt
    exit /b 1
)
pyinstaller --noconfirm --clean --onefile --windowed tiff2pdf.spec
echo.
echo Output: dist\Tiff2Pdf.exe
echo Distribute only this file (no _internal folder needed).
