from src.cloud_client import S3Client
from src.news_api_client import NewsApiClient


# TODO: add logging
def main():
    news_api_client = NewsApiClient()
    s3_client = S3Client(sources_names=news_api_client.sources_names)
    news_api_client.download_sources_with_headlines()
    s3_client.upload_to_bucket()


if __name__ == '__main__':
    main()
