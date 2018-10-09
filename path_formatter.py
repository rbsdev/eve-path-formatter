import eve
import eve.render
from eve.endpoints import collections_endpoint, item_endpoint
from eve.render import request
from eve.utils import import_from_string
from flask import current_app as app


def _best_mime():
    """ Returns the best match between the requested mime type and the
    ones supported by Eve. Along with the mime, also the corresponding
    render function is returns.

    .. versionchanged:: 0.8
       Support for optional renderers via RENDERERS. XML and JSON
       configuration keywords removed.

    .. versionchanged:: 0.3
       Support for optional renderers via XML and JSON configuration keywords.
    """
    supported = []
    renders = {}
    for renderer_cls in app.config.get('RENDERERS'):
        renderer = import_from_string(renderer_cls)
        for mime_type in renderer.mime:
            #### >>> Added code
            if request.base_url.endswith('.{}'.format(getattr(renderer, "tag", "json").lower())):
                supported = []
                renders = {}
                supported.append(mime_type)
                renders[mime_type] = renderer
                break
            #### <<< Added code
            supported.append(mime_type)
            renders[mime_type] = renderer

    if len(supported) == 0:
        abort(500, description=debug_error_message(
            'Configuration error: no supported mime types')
              )

    best_match = request.accept_mimetypes.best_match(supported) or \
                 supported[0]
    return best_match, renders[best_match]


def _add_resource_url_rules(self, resource, settings):
    self.config['SOURCES'][resource] = settings['datasource']

    if settings['internal_resource']:
        return

    for ext in ['', '.json', '.xml']:
        url = '%s/%s' % (self.api_prefix, settings['url'])

        pretty_url = settings['url']
        if '<' in pretty_url:
            pretty_url = pretty_url[:pretty_url.index('<') + 1] + \
                         pretty_url[pretty_url.rindex(':') + 1:]
        self.config['URLS'][resource] = pretty_url

        # resource endpoint
        endpoint = resource + "|resource" + ext
        self.add_url_rule(url + ext, endpoint, view_func=collections_endpoint,
                          methods=settings['resource_methods'] + ['OPTIONS'])

        # item endpoint
        if settings['item_lookup']:
            item_url = '%s/<%s:%s>%s' % (url, settings['item_url'],
                                         settings['item_lookup_field'], ext)

            endpoint = resource + "|item_lookup" + ext
            self.add_url_rule(item_url, endpoint,
                              view_func=item_endpoint,
                              methods=settings['item_methods'] + ['OPTIONS'])
            if 'PATCH' in settings['item_methods']:
                # support for POST with X-HTTM-Method-Override header for
                # clients not supporting PATCH. Also see item_endpoint() in
                # endpoints.py
                try:
                    endpoint = resource + "|item_post_override" + ext
                    self.add_url_rule(item_url, endpoint, view_func=item_endpoint,
                                      methods=['POST'])
                except:
                    pass

            # also enable an alternative lookup/endpoint if allowed
            lookup = settings.get('additional_lookup')
            if lookup:
                l_type = settings['schema'][lookup['field']]['type']
                if l_type == 'integer':
                    item_url = '%s/<int:%s>%s' % (url, lookup['field'], ext)
                else:
                    item_url = '%s/<%s:%s>%s' % (url, lookup['url'],
                                                 lookup['field'], ext)
                endpoint = resource + "|item_additional_lookup" + ext
                self.add_url_rule(item_url, endpoint, view_func=item_endpoint,
                                  methods=['GET', 'OPTIONS'])

    import urllib
    output = []
    for rule in self.url_map.iter_rules():

        options = {}
        for arg in rule.arguments:
            options[arg] = "[{0}]".format(arg)

        methods = ','.join(rule.methods)
        line = urllib.parse.unquote("{:60s} {:40s} {:20s}".format(str(rule), rule.endpoint, methods))
        output.append(line)

    for line in sorted(output):
        self.logger.debug(line)


def install():
    eve.render._best_mime = _best_mime
    eve.Eve._add_resource_url_rules = _add_resource_url_rules
