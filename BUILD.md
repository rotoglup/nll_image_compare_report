The `exe` is built using `PyInstaller`, which is setup like below (tested using Python 3.7.9).

```
pip install -r requirements-dev.txt
```

Then run `PyInstaller` using the custom `spec` file to product the single file bundle.

```
pyinstaller nll_image_compare_report.spec
```

The resulting file is then found in `dist/` folder.
