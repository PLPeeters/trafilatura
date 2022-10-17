"""
Test for transformation to TEI.
"""
from lxml.etree import Element, fromstring, tostring

from trafilatura.metadata import Document
from trafilatura.xml import check_tei, write_fullheader


def test_publisher_added_before_availability_in_publicationStmt():
    # add publisher string
    teidoc = Element("TEI", xmlns="http://www.tei-c.org/ns/1.0")
    metadata = Document()
    metadata.sitename = "The Publisher"
    metadata.license = "CC BY-SA 4.0"
    metadata.categories = metadata.tags = ["cat"]
    header = write_fullheader(teidoc, metadata)
    publicationstmt = header.find(".//{*}fileDesc/{*}publicationStmt")
    assert [child.tag for child in publicationstmt.getchildren()] == [
        "publisher",
        "availability",
    ]
    assert publicationstmt[0].text == "The Publisher"

    teidoc = Element("TEI", xmlns="http://www.tei-c.org/ns/1.0")
    metadata = Document()
    metadata.hostname = "example.org"
    metadata.license = "CC BY-SA 4.0"
    metadata.categories = metadata.tags = ["cat"]
    header = write_fullheader(teidoc, metadata)
    publicationstmt = header.find(".//{*}fileDesc/{*}publicationStmt")
    assert [child.tag for child in publicationstmt.getchildren()] == [
        "publisher",
        "availability",
    ]
    assert publicationstmt[0].text == "example.org"

    teidoc = Element("TEI", xmlns="http://www.tei-c.org/ns/1.0")
    metadata = Document()
    metadata.hostname = "example.org"
    metadata.sitename = "Example"
    metadata.license = "CC BY-SA 4.0"
    metadata.categories = metadata.tags = ["cat"]
    header = write_fullheader(teidoc, metadata)
    publicationstmt = header.find(".//{*}fileDesc/{*}publicationStmt")
    assert [child.tag for child in publicationstmt.getchildren()] == [
        "publisher",
        "availability",
    ]
    assert publicationstmt[0].text == "Example (example.org)"
    # no publisher, add "N/A"
    teidoc = Element("TEI", xmlns="http://www.tei-c.org/ns/1.0")
    metadata = Document()
    metadata.categories = metadata.tags = ["cat"]
    metadata.license = "CC BY-SA 4.0"
    header = write_fullheader(teidoc, metadata)
    publicationstmt = header.find(".//{*}fileDesc/{*}publicationStmt")
    assert [child.tag for child in publicationstmt.getchildren()] == [
        "publisher",
        "availability",
    ]
    assert publicationstmt[0].text == "N/A"
    # no license, add nothing
    teidoc = Element("TEI", xmlns="http://www.tei-c.org/ns/1.0")
    metadata = Document()
    metadata.categories = metadata.tags = ["cat"]
    header = write_fullheader(teidoc, metadata)
    publicationstmt = header.find(".//{*}fileDesc/{*}publicationStmt")
    assert [child.tag for child in publicationstmt.getchildren()] == ["p"]


def test_unwanted_siblings_of_div_removed():
    xml_doc = fromstring("<TEI><text><body><div><div><p>text1</p></div><p>text2</p></div></body></text></TEI>")
    cleaned = check_tei(xml_doc, "fake_url")
    result =  [elem.tag for elem in cleaned.find(".//div").iter()]
    expected = ["div", "div", "p", "div", "p"]
    assert result == expected
    result_str = tostring(cleaned.find(".//body"), encoding="unicode")
    expected_str = "<body><div><div><p>text1</p></div><div><p>text2</p></div></div></body>"
    assert result_str == expected_str
    xml_doc = fromstring("<TEI><text><body><div><div/><list><item>text</item></list></div></body></text></TEI>")
    cleaned = check_tei(xml_doc, "fake_url")
    result = [elem.tag for elem in cleaned.find(".//div").iter()]
    expected = ["div", "div", "div", "list", "item"]
    assert result == expected
    xml_doc = fromstring("<TEI><text><body><div><div/><table><row><cell>text</cell></row></table></div></body></text></TEI>")
    cleaned = check_tei(xml_doc, "fake_url")
    result = [elem.tag for elem in cleaned.find(".//div").iter()]
    expected = ["div", "div", "div", "table", "row", "cell"]
    assert result == expected
    xml_doc = fromstring("<TEI><text><body><div><p>text1</p><div/><div/><p>text2</p></div></body></text></TEI>")
    cleaned = check_tei(xml_doc, "fake_url")
    result = tostring(cleaned.find(".//body"), encoding="unicode")
    expected = "<body><div><p>text1</p><div/><div/><div><p>text2</p></div></div></body>"
    assert result == expected
    xml_doc = fromstring("<TEI><text><body><div><div><p>text1</p></div><p>text2</p><p>text3</p></div></body></text></TEI>")
    cleaned = check_tei(xml_doc, "fake_url")
    result = [elem.tag for elem in cleaned.find(".//div").iter()]
    expected = ["div", "div", "p", "div", "p", "p"]
    assert result == expected
    xml_doc = fromstring("<TEI><text><body><div><p>text1</p><div/><p>text2</p><div/><p>text3</p></div></body></text></TEI>")
    cleaned = check_tei(xml_doc, "fake_url")
    result = [elem.tag for elem in cleaned.find(".//div").iter()]
    expected = ["div", "p", "div", "div", "p", "div", "div", "p"]
    assert result == expected
    xml_doc = fromstring("<TEI><text><body><div><p>text1</p><div/><p>text2</p><div/><list/></div></body></text></TEI>")
    cleaned = check_tei(xml_doc, "fake_url")
    result = [elem.tag for elem in cleaned.find(".//div").iter()]
    expected = ["div", "p", "div", "div", "p", "div", "div", "list"]
    assert result == expected
    xml_doc = fromstring("<TEI><text><body><div><p/><div/><p>text1</p><ab/><p>text2</p></div></body></text></TEI>")
    cleaned = check_tei(xml_doc, "fake_url")
    result_str = tostring(cleaned.find(".//body"), encoding="unicode")
    expected_str = "<body><div><p/><div/><div><p>text1</p><ab/><p>text2</p></div></div></body>"
    assert result_str == expected_str
    xml_doc = fromstring("<TEI><text><body><div><div/><ab/></div></body></text></TEI>")
    cleaned = check_tei(xml_doc, "fake_url")
    result_str = tostring(cleaned.find(".//body"), encoding="unicode")
    expected_str = "<body><div><div/><div><ab/></div></div></body>"
    assert result_str == expected_str
    xml_doc = fromstring("<TEI><text><body><div><div/><quote>text</quote></div></body></text></TEI>")
    cleaned = check_tei(xml_doc, "fake_url")
    result = [elem.tag for elem in cleaned.find(".//div").iter()]
    expected = ["div", "div", "div", "quote"]
    assert result == expected
    xml_doc = fromstring("<TEI><text><body><div><div/><lb/></div></body></text></TEI>")
    cleaned = check_tei(xml_doc, "fake_url")
    result = [elem.tag for elem in cleaned.find(".//div").iter()]
    assert result == ["div", "div", "lb"]
    xml_doc = fromstring("<TEI><text><body><div><div/><ab/></div></body></text></TEI>")
    cleaned = check_tei(xml_doc, "fake_url")
    result = [elem.tag for elem in cleaned.find(".//div").iter()]
    assert result == ["div", "div", "div", "ab"]
    xml_doc = fromstring("<TEI><text><body><div><div><p>text1</p></div><list/><ul><li>text2</li></ul></div></body></text></TEI>")
    cleaned = check_tei(xml_doc, "fake_url")
    result_str = tostring(cleaned.find(".//body"), encoding="unicode")
    expected_str = "<body><div><div><p>text1</p></div><div><list/></div></div></body>"
    assert result_str == expected_str
    xml_doc = fromstring("<TEI><text><body><div><div><p>text1</p></div><ul><li>text2</li></ul><list/></div></body></text></TEI>")
    cleaned = check_tei(xml_doc, "fake_url")
    result_str = tostring(cleaned.find(".//body"), encoding="unicode")
    expected_str = "<body><div><div><p>text1</p></div><div><list/></div></div></body>"
    assert result_str == expected_str
    xml_str = "<TEI><text><body><div><p/><div/></div></body></text></TEI>"
    result = tostring(check_tei(fromstring(xml_str), "fake_url"), encoding="unicode")
    assert result == xml_str
    xml_doc = fromstring("<TEI><text><body><div><div/><lb/>tail</div></body></text></TEI>")
    cleaned = check_tei(xml_doc, "fake_url")
    result = [elem.tag for elem in cleaned.find(".//div").iter()]
    assert result == ["div", "div", "div", "p"]


def test_tail_on_p_like_elements_removed():
    xml_doc = fromstring(
        """
    <TEI><text><body>
      <div>
        <p>text</p>former link
        <p>more text</p>former span
        <p>even more text</p>another span
      </div>
    </body></text></TEI>""")
    cleaned = check_tei(xml_doc, "fake_url")
    result = [(el.text, el.tail) for el in cleaned.iter('p')]
    assert result == [("text former link", None), ("more text former span", None), ("even more text another span", None)]
    xml_doc = fromstring("<TEI><text><body><div><head>title</head>some text<p>article</p></div></body></text></TEI>")
    cleaned = check_tei(xml_doc, "fake_url")
    result = [(elem.tag, elem.text, elem.tail) for elem in cleaned.find(".//div").iterdescendants()]
    assert result == [("ab", "title", None), ("p", "some text", None), ("p", "article", None)]
    xml_doc = fromstring("<TEI><text><body><div><ab>title</ab>tail<p>more text</p></div></body></text></TEI>")
    cleaned = check_tei(xml_doc, "fake_url")
    result = [(elem.tag, elem.text, elem.tail) for elem in cleaned.find(".//div").iterdescendants()]
    assert result == [("ab", "title", None), ("p", "tail", None), ("p", "more text", None)]
    xml_doc = fromstring("<TEI><text><body><div><p>text</p><lb/>tail</div></body></text></TEI>")
    cleaned = check_tei(xml_doc, "fake_url")
    result = [(elem.tag, elem.text, elem.tail) for elem in cleaned.find(".//div").iterdescendants()]
    assert result == [("p", "text", None), ("p", "tail", None)]
    xml_doc = fromstring("<TEI><text><body><div><p/>tail</div></body></text></TEI>")
    cleaned = check_tei(xml_doc, "fake_url")
    result = [(elem.tag, elem.text, elem.tail) for elem in cleaned.find(".//p").iter()]
    assert result == [("p", "tail", None)]


def test_head_with_children_converted_to_ab():
    xml_doc = fromstring("<text><head>heading</head><p>some text</p></text>")
    cleaned = check_tei(xml_doc, "fake_url")
    result = [
        (child.tag, child.text) if child.text is not None else child.tag
        for child in cleaned.iter()
    ]
    assert result == ["text", ("ab", "heading"), ("p", "some text")]
    xml_doc = fromstring("<text><head><p>text</p></head></text>")
    cleaned = check_tei(xml_doc, "fake_url")
    result = [(child.tag, child.text, child.tail) for child in cleaned.iter()]
    assert result == [("text", None, None), ("ab", "text", None)]
    head_with_mulitple_p = fromstring(
        "<text><head><p>first</p><p>second</p><p>third</p></head></text>"
    )
    cleaned = check_tei(head_with_mulitple_p, "fake_url")
    result = [(child.tag, child.text, child.tail) for child in cleaned.iter()]
    assert result == [
        ("text", None, None),
        ("ab", "first", None),
        ("lb", None, "second"),
        ("lb", None, "third"),
    ]
    xml_with_complex_head = fromstring(
        "<text><head><p>first</p><list><item>text</item></list><p>second</p><p>third</p></head></text>"
    )
    cleaned = check_tei(xml_with_complex_head, "fake_url")
    result = [(child.tag, child.text, child.tail) for child in cleaned.iter()]
    assert result == [
        ("text", None, None),
        ("ab", "first", None),
        ("list", None, "second"),
        ("item", "text", None),
        ("lb", None, "third"),
    ]
    xml_doc = fromstring("<text><head><list><item>text1</item></list><p>text2</p></head></text>")
    cleaned = check_tei(xml_doc, "fake_url")
    result = [(child.tag, child.text, child.tail) for child in cleaned.iter()]
    assert result == [
        ("text", None, None),
        ("ab", None, None),
        ("list", None, "text2"),
        ("item", "text1", None)
    ]
    xml_doc = fromstring("<text><head>heading</head><p>some text</p></text>")
    cleaned = check_tei(xml_doc, "fake_url")
    result = cleaned[0].attrib
    assert result == {"type":"header"}
    xml_doc = fromstring("<text><head rend='h3'>heading</head><p>some text</p></text>")
    cleaned = check_tei(xml_doc, "fake_url")
    result = cleaned[0].attrib
    assert result == {"type":"header", "rend":"h3"}
    tei_doc = fromstring("<TEI><teiheader/><text><body><head><p>text</p></head></body></text></TEI>")
    cleaned = check_tei(tei_doc, "fake_url")
    result = cleaned.find(".//ab")
    assert result.text == 'text'
    assert result.attrib == {"type":"header"}
    xml_doc = fromstring("<text><body><head>text1<p>text2</p></head></body></text>")
    cleaned = check_tei(xml_doc, "fake_url")
    result = [(child.tag, child.text, child.tail) for child in cleaned.find(".//ab").iter()]
    assert result == [("ab", "text1", None), ("lb", None, "text2")]
    xml_doc = fromstring(
    """<text>
            <body>
                <head>text1
                    <p>text2</p>
                </head>
            </body>
        </text>
    """
    )
    cleaned = check_tei(xml_doc, "fake_url")
    result = [(child.tag, child.text, child.tail) for child in cleaned.find(".//ab").iter()]
    assert result == [("ab", "text1", None), ("lb", None, "text2")]


if __name__ == "__main__":
    test_publisher_added_before_availability_in_publicationStmt()
    test_unwanted_siblings_of_div_removed()
    test_tail_on_p_like_elements_removed()
    test_head_with_children_converted_to_ab()