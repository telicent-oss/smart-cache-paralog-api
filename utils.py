
__license__ = """
Copyright (c) Telicent Ltd.

This software is licensed under the terms found in the LICENSE file of this resository. 

The above copyright notice and license conditions shall be included in all
copies or substantial portions of the Software.
"""

def flatten_out(data, return_first_obj=False):
    results = []
    if data["results"]["bindings"] is not None:
        for stmt in data["results"]["bindings"]:
            obj = {}
            for v in data["head"]["vars"]:
                if v in stmt and stmt[v] is not None:
                    obj[v] = stmt[v]["value"]
            results.append(obj)
    if return_first_obj:
        return results[0]
    else:
        return results

def map_flood_areas(data):
    bindings = data['results']['bindings']
    head = data['head']['vars']

    flood_areas = {}
    if bindings is not None:
        for binding in bindings:

            if binding[head[0]]['value']not in flood_areas.keys():
                flood_areas[binding[head[0]]['value']] = {
                    'uri': binding[head[0]]['value'],
                    'name': binding[head[1]]['value'],
                    'polygon_uri': binding[head[2]]['value'],
                    'flood_areas': []
                }
            flood_areas[binding[head[0]]['value']]['flood_areas'].append({
                'uri': binding[head[3]]['value'],
                'name': binding[head[4]]['value'],
                'polygon_uri': binding[head[5]]['value']
            })

    return list(flood_areas.values())


pass_through_headers = [
    'x-amzn-oidc-data',
    'x-amzn-oidc-identity',
    'x-amzn-oidc-accesstoken'
]

def aggregate(data, agg_var):
    results = {}
    if data["results"]["bindings"] is not None:
        for stmt in data["results"]["bindings"]:
            if stmt[agg_var]['value'] in results:
                obj = results[stmt[agg_var]['value']]
            else:
                obj = {}
                for v in data['head']['vars']:
                    if v != agg_var:
                        obj[v] = []
                results[stmt[agg_var]['value']] = obj
            for v in data['head']['vars']:
                if v in stmt and v != agg_var:

                    obj[v].append(stmt[v]['value'])
    return results

def get_headers(headers):
    forward_headers = {}
    for h in pass_through_headers:
        hv = headers.get(h)
        if hv is not None:
            forward_headers[h] = hv
    return forward_headers

def create_assessments_string(assessments):
    assessment_string = '('
    for ass in assessments:
        assessment_string = assessment_string + "<"+ass+">,"
    assessment_string = assessment_string[:-1]+")"
    return assessment_string
