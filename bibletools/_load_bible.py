"""Load and convert Bible XML files."""

from xml.etree import ElementTree


# pylint: disable=too-many-locals
def _parse_xml_to_dict(
    xml: str,
    testament_path: str | None = None,
    book_spec: tuple[str, str] = ("b", "n"),
    chapter_spec: tuple[str, str] = ("c", "n"),
    verse_spec: tuple[str, str] = ("v", "n"),
) -> dict:
    """Convert a Bible XML string to a nested dictionary.

    Structure:

    {
      "book_name": {
        chapter_number: {
          verse_number: "Verse text..."
          },
          ...
        },
        ...
      },
      ...
    }

    Parameters
    ----------
    xml
        XML content as a string.

    Returns
    -------
    dict
        Nested dictionary of books, chapters, and verses with text.
    """
    root = ElementTree.fromstring(xml)
    bible_dict = {}

    testaments = (
        [root] if testament_path is None else root.findall(testament_path)
    )
    for testament in testaments:

        book_path, book_attrib = book_spec
        for book in testament.findall(book_path):
            book_name = book.attrib[book_attrib]
            book_dict = {}

            chapter_path, chapter_attrib = chapter_spec
            for chapter in book.findall(chapter_path):
                chapter_name = chapter.attrib[chapter_attrib]
                chapter_dict = {}

                verse_path, verse_attrib = verse_spec
                for verse in chapter.findall(verse_path):
                    verse_name = verse.attrib[verse_attrib]
                    text = (verse.text or "").strip()
                    chapter_dict[verse_name] = text

                book_dict[chapter_name] = chapter_dict

            bible_dict[book_name] = book_dict

    return bible_dict
