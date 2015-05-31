Slides N-Up
===========

Simple script to take a bunch of slides and create a single output document ready for printing.

Useful for slides from lectures on openbook exams for example.

Usage
-----

Provide output filename and list of files to process:

```ShellSession
$ /path/to/slidenup.py slides.pdf lecture-01.pdf lecture-02.pdf lecture-slides-*.pdf
```

No user-friendly CLI configuration yet, just edit the lines at beginning of the script.

Default settings n-up every file to a landscape 3x2 grid, numbering and labeling them on top. Page numbers of the final document are on the bottom.

Dependencies
------------

You will need `pdfjam`, `pdftk`, `pdfinfo` and `pdflatex` with `fancyhdr`, `geometry` and `multido` packages.

All of this can be found in package repositories for most common platforms.

License
-------

This code is released under the MIT license.
