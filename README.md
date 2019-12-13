A tool for generating an HTML change report between images in one or two folders.

> An example report can be seen [here](https://nllsoft.com/tools/nll_image_compare_report/example_report/), it has been generated using the `test-images-one-folder/` folder in the repo.

# Usage, two folders

![Usage illustration](doc/usage-illustration-two-folders.gif)

Drop two folders, containing images to compare, on the executable - the HTML report will be written in the parent folder.

Images with the same name are compared in the report.

# Usage, one folder

![Usage illustration](doc/usage-illustration-one-folder.gif)

Drop an images folder on the executable - the HTML report will be written in the folder.

Image names are used to detect the image variants, based on the `-` character.

For example, the two images :

* `my nice image - after.png`
* `my nice image - before.png`

will appear as one image `my nice image` in the report, with a slider to seen changes between `after` and `before` (alphabetical order)

Thanks to https://github.com/pehaa/beerslider for the slider code.