import asyncio
import csv
import logging
import time
from collections import Counter
from collections.abc import Callable

import aiohttp
from aiohttp import ClientSession, ClientError
from bs4 import BeautifulSoup


def timer(func) -> Callable:
    async def wrapper(*args, **kwargs) -> Callable:
        start_time = time.time()
        result = await func(*args, **kwargs)
        end_time = time.time()
        log.info("Время выполнения %s функции: %.2f seconds" % (func.__name__, end_time - start_time))
        return result
    return wrapper


def write_result_csv(result: list[tuple[str, int]], name: str = "beasts.csv") -> None:
    with open(name, "w", encoding="utf-8-sig", newline="") as file:
        writer = csv.writer(file, delimiter=",", dialect="excel")
        for string in result:
            writer.writerow(string)



class WikiParser:
    domain = "https://ru.wikipedia.org"
    start_page = "https://ru.wikipedia.org/wiki/Категория:Животные_по_алфавиту"

    def __init__(self) -> None:
        self.names: set[str | None] = set()
        self.next_pages: list[str | None] = list()
        self.start_points: list[str | None] = list()


    @staticmethod
    async def get_page_data(session: ClientSession, url: str) -> BeautifulSoup:
        """
        Отдаем структуру страницы, основываясь на полученном url
        """
        try:
            async with session.get(url=url, timeout=10) as response:
                response.raise_for_status()
                return BeautifulSoup(await response.text(), "lxml")
        except asyncio.TimeoutError:
            print(f"Время вышло по запросу {url}")
        except ClientError as e:
            print(f"HTTP error while fetching {url}: {e}")
        except Exception as e:
            print(f"Неизвестная ошибка: {e.__class__.__name__}")


    @staticmethod
    def get_pages(soup: BeautifulSoup) -> tuple:
        """
        Получаем первые ссылки и сами промежуточные префиксы (Ав, Ан...)
        """
        postfixes = soup.select(
            selector="div.ts-module-Индекс_категории-container > ul > li > a"
        )
        paths, letters = zip(*[(path["href"], path.text) for path in postfixes])
        paths, letters = list(paths), list(letters)
        return paths, letters


    def find_intersections(self, animal_names: list[str], soup: BeautifulSoup) -> None:
        """
        Тут проверяем есть ли у нас животные у которых первые 2 буквы пересеклись с буквами
        промежуточных точек, если есть, то дальше парсить нет смысла, это сделала другая корутина,
        а если нет, то добавляем ссылку на следующую страницу животных
        """
        coroutine_own_data = self.start_points[:]

        if (start_point := f"{animal_names[0][0]}{animal_names[0][1]}") in coroutine_own_data:
            coroutine_own_data.remove(start_point)

        first_letters = set([f"{name[0]}{name[1]}" for name in animal_names])
        if not first_letters.intersection(set(coroutine_own_data)):
            if postfix := soup.find("a", string="Следующая страница"):
                self.next_pages.append(f"{self.domain}{postfix["href"]}")



    async def get_animals_from_page(self, session: ClientSession, url: str) -> None:
        """
        Тут вытаскиваем из конкретной страницы животных, которых мы
        еще не добавили в общий список и проверяем нет ли там Английских слов,
        затем, если список заполнен мы проверяем есть ли пересечения текущих животных с
        промежуточными точками (Ав, Аб...), и удаляем страницу из общего списка
        """
        soup = await self.get_page_data(session=session, url=url)
        page_animals = soup.select(
            selector="div.mw-category.mw-category-columns > div.mw-category-group > ul > li > a"
        )
        animal_names = [
            name for animal in page_animals
            if not ord((name := animal["title"])[0]) in range(65, 123)
        ]
        self.names.update(set(animal_names))

        if animal_names:
            self.find_intersections(animal_names=animal_names, soup=soup)
        self.next_pages.remove(url)


@timer
async def main(parser: WikiParser):
    """
    Функция получает структуру первой страницы через метод get_page_data,
    затем сохраняет ссылки на промежуточные url животных по алфавиту и промежуточные
    буквы этих ссылок (Ав, Аб...) через метод get_pages. Это нужно для отслеживания пересечения,
    чтобы каждая короутина знала до какой страницы ей парсить, пока не пропасят все
    страницы между промежуточными точками цикл не остановится, затем сохраняем результат
    """
    async with (aiohttp.ClientSession() as session):
        log.info("Начинаем парсить wiki, займет примерно 20 секунд...")
        first_page = await parser.get_page_data(session=session, url=parser.start_page)
        pages = parser.get_pages(soup=first_page)
        parser.next_pages = pages[0]
        parser.start_points = pages[1]

        while parser.next_pages:
            tasks_1 = [
                asyncio.create_task(parser.get_animals_from_page(session=session, url=url))
                for url in parser.next_pages
            ]
            await asyncio.gather(*tasks_1)

        log.info("Результат получен, идет запись в файл...")

        result = Counter([name[0] for name in list(parser.names)])
        sorted_result = (sorted(list(result.items()), key=lambda x: x[0]))
        write_result_csv(result=sorted_result)

        log.info("Файл успешно сохранен!")



if __name__ == "__main__":
    logging.basicConfig(level="INFO")
    log = logging.getLogger(__name__)

    parser_helper = WikiParser()
    asyncio.run(main(parser=parser_helper))
