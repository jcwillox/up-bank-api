import json

import pytest
import yaml


class YamlSerializer(object):
    @staticmethod
    def deserialize(cassette_string):
        cassette_dict = yaml.safe_load(cassette_string)

        if "interactions" in cassette_dict:
            for item in cassette_dict["interactions"]:
                body = item["response"]["body"]
                if "yaml" in body:
                    body["string"] = json.dumps(body["yaml"])
                    del body["yaml"]

        return cassette_dict

    @staticmethod
    def serialize(cassette_dict):
        if "interactions" in cassette_dict:
            for item in cassette_dict["interactions"]:
                body = item["response"]["body"]
                if "string" in body:
                    body["yaml"] = json.loads(body["string"])
                    del body["string"]

                # compatibility with aiohttp
                if "url" not in item["response"]:
                    item["response"]["url"] = item["request"]["uri"]

                for x in [
                    "Date",
                    "Etag",
                    "ETag",
                    "X-Runtime",
                    "X-Request-Id",
                    "X-RateLimit-Remaining",
                ]:
                    item["response"]["headers"].pop(x, None)

        cassette_string = yaml.safe_dump(cassette_dict)
        return cassette_string


def pytest_recording_configure(vcr):
    vcr.register_serializer("yaml", YamlSerializer())
    vcr.serializer = "yaml"


@pytest.fixture(scope="module")
def vcr_config():
    return {"filter_headers": ["Authorization"]}
