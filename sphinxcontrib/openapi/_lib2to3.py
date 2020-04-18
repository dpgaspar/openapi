"""Partial OpenAPI v2.x to OpenAPI v3.x converter."""


def convert(spec, *args, **kwargs):
    return Lib2to3(*args, **kwargs).convert(spec)


def is_vendor_extension(key):
    return key.lower().startswith("x-")


def copyover(source, destination, properties, vendor_extensions=True):
    for key, value in source.items():
        if any([
            key in properties,
            vendor_extensions and is_vendor_extension(key),
        ]):
            destination[key] = value

    return destination


class Lib2to3:

    def convert(self, spec):
        return self.convert_paths(spec["paths"])

    def convert_paths(self, paths):
        retval = {}

        for endpoint, path in paths.items():
            if is_vendor_extension(endpoint):
                retval[endpoint] = path
            else:
                retval[endpoint] = self.convert_path(path)
        return retval

    def convert_path(self, path):
        retval = {}

        for key, value in path.items():
            if key == "parameters" or is_vendor_extension(key):
                retval[key] = value
            else:
                retval[key] = self.convert_operation(value)
        return retval

    def convert_operation(self, operation):
        retval = {}
        copyover = {"tags", "summary", "description", "externalDocs", "operationId", "deprecated"}

        for key, value in operation.items():
            if key in copyover or is_vendor_extension(key):
                retval[key] = value

        if "parameters" in operation:
            request_body = self.convert_request_body(operation)
            if request_body:
                retval["requestBody"] = request_body
            retval["parameters"] = self.convert_parameters(operation["parameters"])
        retval["responses"] = self.convert_responses(operation["responses"])
        return retval

    def convert_request_body(self, operation):
        retval = {}

        for parameter in operation["parameters"]:
            if parameter["in"] == "body":
                copyover(parameter, retval, {"description", "required"})
                mimetypes = operation.get("consumes") or ["*/*"]
                content = {}
                if "schema" in parameter:
                    content["schema"] = parameter["schema"]
                retval["content"] = {mimetypes[0]: content}
                break

        return retval

    def convert_parameters(self, parameters):
        return [
            self.convert_parameter(parameter)
            for parameter in parameters
            # If a parameter is one of the backward compatible type, delegate
            # the call the converter function. Incompatible types, such as
            # 'formData' and/or 'body' must be handled separately since they
            # are reflected on the operation level in 3.x.
            if parameter["in"] in {"query", "header", "path"}
        ]

    def convert_parameter(self, parameter):
        collection_format = parameter.pop("collectionFormat", None)

        schema = {
            key: value
            for key, value in parameter.items()
            if all([
                key not in {"name", "in", "description", "required"},
                not is_vendor_extension(key)
            ])
        }
        parameter = {
            key: value
            for key, value in parameter.items()
            if key not in schema
        }
        parameter["schema"] = schema

        if parameter["in"] in {"path", "header"} and collection_format == "csv":
            parameter["style"] = "simple"
        elif parameter["in"] in {"query"} and collection_format:
            styles = {
                "csv": {"style": "form", "explode": False},
                "multi": {"style": "form", "explode": True},
                "ssv": {"style": "spaceDelimited"},
                "pipes": {"style": "pipeDelimited"},
                # OpenAPI 3.x does not explicitly say what is the alternative
                # to 'collectionFormat=tsv'. We have no other option but to
                # ignore it. Fortunately, we don't care much as it's not used
                # by the renderer.
                "tsv": {},
            }
            parameter.update(styles[collection_format])

        return parameter

    def convert_responses(self, responses):
        return responses

    def convert_response(self, response):
        return response
