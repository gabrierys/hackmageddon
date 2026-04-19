from src.parsers.timeline_parser import extract_valid_event_tables


SAMPLE_HTML = """
<html>
  <head><title>Cyber Attacks Timeline</title></head>
  <body>
    <table>
      <tr><th>Foo</th><th>Bar</th></tr>
      <tr><td>1</td><td>2</td></tr>
    </table>

    <table>
      <tr>
        <th>ID</th>
        <th>Date Reported</th>
        <th>Attack</th>
        <th>Target</th>
      </tr>
      <tr>
        <td>1</td>
        <td>01/01/2024</td>
        <td>Ransomware</td>
        <td>Healthcare</td>
      </tr>
    </table>
  </body>
</html>
"""


def test_extract_only_valid_timeline_table():
    tables = extract_valid_event_tables(SAMPLE_HTML)
    assert len(tables) == 1
    df = tables[0]
    assert "Date Reported" in df.columns
    assert "Attack" in df.columns
    assert "Target" in df.columns
    assert df.iloc[0]["Attack"] == "Ransomware"
