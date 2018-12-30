import os
from urllib.parse import urlparse


def get_filename_from_url(url):
    """
    Take a fully-qualified URL and turn it into a filename. For
    example, turn a url like this:

        https://www.cia.gov/library/readingroom/docs/%5B15423241%5D.pdf

    Using the parsed URL:

        ParseResult(scheme='https', netloc='www.cia.gov',
            path='/library/readingroom/docs/%5B15423241%5D.pdf

    Returing this representation (a string):

        _library_readingroom_docs_%5B15423241%5D.pdf

    NOTE: If no extension is found on the page, .html is appended.
    """
    parsed = urlparse(url)
    host = parsed.netloc
    # split filename/path and extension
    file_parts = os.path.splitext(parsed.path)
    file_part = file_parts[0].replace("/", "_")
    extension = file_parts[1] or ".html"
    filename = "%s_%s" % (host, file_part)
    if parsed.query:
        query_part = "_".join(parsed.query.split("&"))
        filename = "%s__%s" % (filename, query_part)
    return "%s%s" % (filename, extension)


def get_extension_from_url(url):
        # try and extract the extension from the URL
        path = urlparse(url).path
        ext = os.path.splitext(path)[1]
        ext = ext if ext else "html"
        if ext[0] == ".":
            ext = ext[1:]
        return ext

