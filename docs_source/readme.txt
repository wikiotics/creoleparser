Project Documentation
*********************

Work on Documentation for an Upcoming Releases
==============================================

When working on documentation for an upcoming releases, make sure `draft/conf.py`
is configured to use the trunk source code.

To build these docs run the following from the `docs_source` folder::

   sphinx-build draft html

This will create an unversioned folder named "html" containing the html. There
is currently no plan to publish the trunk docs as html, so don't check them in.

To run the doctect blocks::

   sphinx-build -b doctest draft html


Maintenance of Documentation for Current Release
================================================

To build docs for a tagged release, configure `draft/conf.py` to point to the
correct tagged source code folder.

To build these docs, run the following from the `docs_source` folder::

   sphinx-build draft ../docs

This will update the versioned live documentation. Note that the project's
documentation is served directly from subversion, so the check-in will be
instantly published.

Notes
=====

* The trunk versions of CHANGES.txt and INSTALL.txt are used regardless of
the conf.py setting.





