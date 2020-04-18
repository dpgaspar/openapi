"""Tests partial OpenAPI 2.x to OpenAPI 3.x converter."""

import pytest

from sphinxcontrib.openapi._lib2to3 import Lib2to3


@pytest.fixture(scope="function")
def testconverter():
    return Lib2to3()


@pytest.mark.parametrize(
    ["v2", "v3"],
    [
        pytest.param(
            {
                "name": "token",
                "in": "header",
                "description": "token to be passed as a header",
                "required": True,
                "type": "array",
                "items": {"type": "integer", "format": "int64"},
            },
            {
                "name": "token",
                "in": "header",
                "description": "token to be passed as a header",
                "required": True,
                "schema": {
                    "type": "array",
                    "items": {"type": "integer", "format": "int64"},
                },
            },
            id="in-header",
        ),
        pytest.param(
            {
                "name": "username",
                "in": "path",
                "description": "username to fetch",
                "required": True,
                "type": "string",
            },
            {
                "name": "username",
                "in": "path",
                "description": "username to fetch",
                "required": True,
                "schema": {"type": "string"},
            },
            id="in-path",
        ),
        pytest.param(
            {
                "name": "id",
                "in": "query",
                "description": "ID of the object to fetch",
                "required": False,
                "type": "array",
                "items": {"type": "string"},
            },
            {
                "name": "id",
                "in": "query",
                "description": "ID of the object to fetch",
                "required": False,
                "schema": {"type": "array", "items": {"type": "string"}},
            },
            id="in-query",
        ),
        pytest.param(
            {"name": "token", "in": "header", "type": "string"},
            {"name": "token", "in": "header", "schema": {"type": "string"}},
            id="in-header-minimal",
        ),
        pytest.param(
            {"name": "username", "in": "path", "required": True, "type": "string"},
            {
                "name": "username",
                "in": "path",
                "required": True,
                "schema": {"type": "string"},
            },
            id="in-path-minimal",
        ),
        pytest.param(
            {"name": "id", "in": "query", "type": "string"},
            {"name": "id", "in": "query", "schema": {"type": "string"}},
            id="in-query-minimal",
        ),
        pytest.param(
            {
                "name": "username",
                "in": "path",
                "required": True,
                "type": "array",
                "items": {"type": "string"},
                "collectionFormat": "csv",
            },
            {
                "name": "username",
                "in": "path",
                "required": True,
                "schema": {"type": "array", "items": {"type": "string"}},
                "style": "simple",
            },
            id="collectionFormat=csv/path",
        ),
        pytest.param(
            {
                "name": "username",
                "in": "header",
                "type": "array",
                "items": {"type": "string"},
                "collectionFormat": "csv",
            },
            {
                "name": "username",
                "in": "header",
                "schema": {"type": "array", "items": {"type": "string"}},
                "style": "simple",
            },
            id="collectionFormat=csv/header",
        ),
        pytest.param(
            {
                "name": "id",
                "in": "query",
                "type": "array",
                "items": {"type": "string"},
                "collectionFormat": "csv",
            },
            {
                "name": "id",
                "in": "query",
                "schema": {"type": "array", "items": {"type": "string"}},
                "style": "form",
                "explode": False,
            },
            id="collectionFormat=csv",
        ),
        pytest.param(
            {
                "name": "id",
                "in": "query",
                "type": "array",
                "items": {"type": "string"},
                "collectionFormat": "multi",
            },
            {
                "name": "id",
                "in": "query",
                "schema": {"type": "array", "items": {"type": "string"}},
                "style": "form",
                "explode": True,
            },
            id="collectionFormat=multi",
        ),
        pytest.param(
            {
                "name": "id",
                "in": "query",
                "type": "array",
                "items": {"type": "string"},
                "collectionFormat": "ssv",
            },
            {
                "name": "id",
                "in": "query",
                "schema": {"type": "array", "items": {"type": "string"}},
                "style": "spaceDelimited",
            },
            id="collectionFormat=ssv",
        ),
        pytest.param(
            {
                "name": "id",
                "in": "query",
                "type": "array",
                "items": {"type": "string"},
                "collectionFormat": "pipes",
            },
            {
                "name": "id",
                "in": "query",
                "schema": {"type": "array", "items": {"type": "string"}},
                "style": "pipeDelimited",
            },
            id="collectionFormat=pipes",
        ),
        pytest.param(
            {
                "name": "id",
                "in": "query",
                "type": "array",
                "items": {"type": "string"},
                "collectionFormat": "tsv",
            },
            {
                "name": "id",
                "in": "query",
                "schema": {"type": "array", "items": {"type": "string"}},
            },
            id="collectionFormat=tsv",
        ),
    ],
)
def test_convert_parameter(testconverter, v2, v3):
    assert testconverter.convert_parameter(v2) == v3


@pytest.mark.parametrize(
    ["v2", "v3"],
    [
        pytest.param(
            [
                {"name": "token", "in": "header", "type": "string"},
                {"name": "username", "in": "path", "required": True, "type": "string"},
                {"name": "id", "in": "query", "type": "string"},
            ],
            [
                {"name": "token", "in": "header", "schema": {"type": "string"}},
                {
                    "name": "username",
                    "in": "path",
                    "required": True,
                    "schema": {"type": "string"},
                },
                {"name": "id", "in": "query", "schema": {"type": "string"}},
            ],
            id="header/path/query",
        ),
        pytest.param(
            [
                {
                    "name": "user",
                    "in": "body",
                    "description": "user to add to the system",
                    "required": True,
                    "schema": {"$ref": "#/definitions/User"},
                },
            ],
            [],
            id="!body",
        ),
        pytest.param(
            [
                {
                    "name": "avatar",
                    "in": "formData",
                    "description": "The avatar of the user",
                    "type": "file",
                },
            ],
            [],
            id="!formData",
        ),
    ],
)
def test_convert_parameters(testconverter, v2, v3):
    assert testconverter.convert_parameters(v2) == v3
