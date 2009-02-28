Project Documentation
*********************

Work on Documentation for an Upcoming Releases
==============================================

Work on documentation for upcoming releases should be done in the `draft`
folder. These docs are configured to use the trunk source code (see `conf.py`).

To build these docs run the following from the `docs_source` folder::

   sphinx-build draft html

This will create an unversioned folder named "html" containing the html. There
is currently no plan to publish the trunk docs as html, so don't check them in.

To run the doctect blocks::

   sphinx-build -b doctest draft html


Maintenance of Documentation for Current Release
================================================

Corrections, improvements, and additions to the current live documentation
should be done in the `release` folder. These docs are configured to use
the relevant tagged source code folder (verify in `conf.py`).
To build these docs, run the following from the `docs_source` folder::

   sphinx-build release ../docs

This will update the versioned live documentation. Please make sure that
the source files (in `release`) are in sync with the built files (in `docs`)
before checking in. Note that the project's documentation is served
directly from subversion, so the check-in will be instantly published.

Notes
=====

* The trunk versions of CHANGES.txt and INSTALL.txt are used by both `release`
  and `draft`.





