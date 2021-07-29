import csv
import os
from datetime import datetime
from functools import cached_property
from pathlib import Path
from typing import List, Dict, Set

import requests

from src.constants import NEWSAPI_URL, SOURCES_PARENT_DIR, TIMESTAMP_FORMAT, FILE_NAME_PATTERN
from src.helpers import name_to_snake_case, get_secret_key


class CSVSaver:
    @staticmethod
    def _create_sources_dirs(sources_with_headlines: Dict[str, list]) -> None:
        for source in sources_with_headlines:
            if not sources_with_headlines[source]:
                continue
            Path(os.path.join(SOURCES_PARENT_DIR, source)).mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _compose_file_path(source: str) -> str:
        current_sys_timestamp = datetime.now().strftime(TIMESTAMP_FORMAT)
        return os.path.join(SOURCES_PARENT_DIR, source,
                            FILE_NAME_PATTERN.format(current_sys_timestamp))

    def save_to_csv(self, sources_with_headlines: Dict[str, list]) -> None:
        self._create_sources_dirs(sources_with_headlines)
        for source in sources_with_headlines:
            csv_file = self._compose_file_path(source)
            try:
                with open(csv_file, 'w') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow(sources_with_headlines[source])
            except IOError as e:
                print(e)


class NewsApiClient:
    def __init__(self):
        self.saver = CSVSaver()
        self._params = {'apiKey': get_secret_key(), 'language': 'en'}

    @cached_property
    def sources_names(self) -> Set[str]:
        response: dict = requests.get(NEWSAPI_URL + 'sources', params=self._params).json()
        return {source['name'] for source in response['sources']}

    @cached_property
    def top_headlines(self) -> List[dict]:
        response: dict = requests.get(NEWSAPI_URL + 'top-headlines', params=self._params).json()
        return response['articles']

    def _get_headlines_for_sources(self) -> Dict[str, list]:
        sources_with_headlines = {}
        for article in self.top_headlines:
            article_source_name = article['source']['name']
            if article_source_name not in self.sources_names:
                continue
            sources_with_headlines.setdefault(name_to_snake_case(article_source_name), []) \
                .append(article['title'])
        return sources_with_headlines

    def download_sources_with_headlines(self) -> None:
        sources_with_headlines = self._get_headlines_for_sources()
        self.saver.save_to_csv(sources_with_headlines)
