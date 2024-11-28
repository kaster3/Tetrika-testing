import csv
import os

import pytest
import tempfile
from unittest.mock import patch, AsyncMock

from task2.solution import WikiParser, write_result_csv
from aiohttp import ClientSession
from bs4 import BeautifulSoup


class TestWikiParser:
    @pytest.mark.asyncio
    @patch("task2.solution.WikiParser.get_page_data", new_callable=AsyncMock)
    async def test_get_page_data(self, mock_get_page_data):
        mock_get_page_data.return_value = BeautifulSoup("<html></html>", "lxml")
        session = AsyncMock(spec=ClientSession)
        soup = await WikiParser.get_page_data(session, "http://localhost:8000")
        assert isinstance(soup, BeautifulSoup)
        mock_get_page_data.assert_called_once_with(session, "http://localhost:8000")


    def test_get_pages(self):
        mock_html = """
        <div class="ts-module-Индекс_категории-container">
            <ul>
                <li><a href="/wikipedia">Ав</a></li>
                <li><a href="/tetrika.ru">Ан</a></li>
            </ul>
        </div>
        """
        soup = BeautifulSoup(mock_html, "lxml")
        paths, letters = WikiParser.get_pages(soup)
        assert paths == ["/wikipedia", "/tetrika.ru"]
        assert letters == ["Ав", "Ан"]


    @pytest.mark.parametrize(
        "start_points, animal_names, expected_in_next_pages",
        [
            (["Ав", "Ан"], ["Австралия", "Авеню"], True),
            (["Ав", "Ан"], ["Австралия", "Анна"], False),
        ],
    )
    def test_find_intersections(self, start_points, animal_names, expected_in_next_pages):
        parser = WikiParser()
        parser.start_points = start_points
        soup = BeautifulSoup("<a href='/Следующая_страница.com'>Следующая страница</a>", "lxml")
        parser.find_intersections(animal_names, soup)
        url = f"{parser.domain}/Следующая_страница.com"
        if expected_in_next_pages:
            assert url in parser.next_pages
        else:
            assert url not in parser.next_pages


    def test_write_result_csv(self):
        data = [("A", 10), ("B", 20)]
        with tempfile.NamedTemporaryFile(delete=True, mode='w', encoding='utf-8-sig', newline='') as temp_file:
            temp_file_name = temp_file.name
            write_result_csv(result=data, name=temp_file_name)
            with open(temp_file_name, 'r', encoding='utf-8-sig') as file:
                reader = csv.reader(file)
                contents = list(reader)
            assert contents == [["A", "10"], ["B", "20"]]
