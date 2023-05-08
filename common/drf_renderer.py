from rest_framework.compat import (INDENT_SEPARATORS, LONG_SEPARATORS,
                                   SHORT_SEPARATORS)
from rest_framework.renderers import JSONRenderer
from rest_framework.utils import json


class CustomRenderer(JSONRenderer):

     def render(self, data, accepted_media_type=None, renderer_context=None):
        """
        Render `data` into JSON, returning a bytestring.
        """        
        _data = {'code':0, 'msg':'操作成功'}
        if data is None:
            resp = renderer_context.get('response', None)
            if resp and resp.status_code == 204:
                resp.status_code = 200
            return self.json_dumps(_data, accepted_media_type, renderer_context)
        
        if isinstance(data, list):
            data = {'results': data}
        
        if not data.get('code', False):
            if data.get('count', False):
                _data.update(count = data['count'])
            if data.get('results', False):
                _data.update(data=data['results'])
            else:
                _data.update(data=data)
            data = _data
        return self.json_dumps(data, accepted_media_type, renderer_context)
        
     def json_dumps(self,data,accepted_media_type=None, renderer_context=None):
        renderer_context = renderer_context or {}
        indent = self.get_indent(accepted_media_type, renderer_context)

        if indent is None:
            separators = SHORT_SEPARATORS if self.compact else LONG_SEPARATORS
        else:
            separators = INDENT_SEPARATORS
        ret = json.dumps(
            data, cls=self.encoder_class,
            indent=indent, ensure_ascii=self.ensure_ascii,
            allow_nan=not self.strict, separators=separators
        )

        # We always fully escape \u2028 and \u2029 to ensure we output JSON
        # that is a strict javascript subset.
        # See: https://gist.github.com/damncabbage/623b879af56f850a6ddc
        ret = ret.replace('\u2028', '\\u2028').replace('\u2029', '\\u2029')
        return ret.encode()