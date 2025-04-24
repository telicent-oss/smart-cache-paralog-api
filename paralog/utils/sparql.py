__license__ = """
Copyright (c) Telicent Ltd.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""


async def flatten_out(data, return_first_obj=False):
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


async def map_flood_areas(data):
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


async def aggregate(data, agg_var):
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
