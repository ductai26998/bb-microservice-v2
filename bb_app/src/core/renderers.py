from rest_framework.renderers import JSONRenderer


class ApiRenderer(JSONRenderer):
    def render(self, data, accepted_media_type=None, renderer_context=None):
        response_dict = {
            "detail": None,
            "data": None,
            "error": None,
        }
        error = {}
        if data.get("detail"):
            response_dict["detail"] = data.get("detail")
        if data.get("data"):
            response_dict["data"] = data.get("data")
        if data.get("messages"):
            error["messages"] = data.get("messages")
        if data.get("code"):
            error["code"] = data.get("code")
        if error:
            response_dict["error"] = error
        return super().render(response_dict, accepted_media_type, renderer_context)
