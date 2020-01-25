def read_file(filename):
    with open(filename) as f:
        return f.read()


def test_good_html_parse():
    html = read_file("tests/tag_test_data_page.html")
    assert(html)
    assert(len(html) > 0)
