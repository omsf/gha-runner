This project us `mkdoc` to for building API documentation.
To get started with editing these docs run the following:

```bash
pip install -e .[docs]
```

This will install all the pieces necessary to get started when building our docs!

## Adding new informationl pages
Adding a new page is as simple as creating a new markdown file in this directory.
Note, to have an item show up on the sidebar, you will need to also modify the `mkdocs.yml` to add include the new item.

## Modifying code documentation
We are using [`mkdocstrings`](https://mkdocstrings.github.io/) to auto-generate docs for the library API, if you need to make changes, make them in the code itself using Numpydoc for our style.
