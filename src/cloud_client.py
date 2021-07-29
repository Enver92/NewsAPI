import os
from pathlib import Path
from typing import Set

import boto3
from botocore.exceptions import ClientError

from src.constants import BUCKET_NAME, SOURCES_PARENT_DIR
from src.helpers import name_to_snake_case


class S3Client:
    def __init__(self, sources_names: Set[str], bucket_name: str = BUCKET_NAME):
        self._sources_names = sources_names
        self._bucket_name = bucket_name
        self._client = boto3.client('s3')

    def create_bucket(self) -> None:
        self._client.create_bucket(Bucket=self._bucket_name)

    def _create_sources_s3_folders(self) -> None:
        for source in self._sources_names:
            try:
                self._client.put_object(Bucket=self._bucket_name,
                                        Key=(name_to_snake_case(source) + '/'))
            except ClientError as e:
                print(e)

    def _upload_files(self) -> None:
        files_paths = Path(SOURCES_PARENT_DIR).glob('**/*.csv')
        for path in files_paths:
            path_str = str(path)
            obj_name, file_name = path_str.split(os.sep)[1:]
            try:
                self._client.upload_file(path_str, self._bucket_name, f'{obj_name}/{file_name}')
            except ClientError as e:
                print(e)

    def upload_to_bucket(self) -> None:
        self.create_bucket()
        self._create_sources_s3_folders()
        self._upload_files()
