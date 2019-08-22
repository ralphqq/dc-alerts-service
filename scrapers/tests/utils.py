import uuid

from scrapy.http import Request, HtmlResponse


def make_response_object(filepath, callback=None, method='GET', meta=None):
    """Creates a Scrapy Response object from a local HTML file.

    Args:
        filepath (str): absolute path to HTML file
        callback (callable): the function that will be called
        method (str): HTTP method of request that generates response
        meta (dict): the initial values for the Request.meta attribute

    Returns:
        HtmlResponse object
    """
    # Read HTML file
    file_content = None
    with open(filepath, 'r', encoding='utf-8') as f:
        file_content = f.read()

    # Make a Request object
    request = Request(
        url=f'file:///{filepath}',
        callback=callback,
        method=method,
        meta=meta
    )

    return HtmlResponse(
        url=request.url,
        request=request,
        body=file_content.encode('utf-8')
    )


def make_fake_id():
    """Generates a 20-character UUID as str."""
    s = str(uuid.uuid4())
    return s[:20]
