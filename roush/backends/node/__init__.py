#!/usr/bin/env python

from roush import backends
import roush.webapp.ast


class NodeBackend(backends.Backend):
    def __init__(self):
        super(NodeBackend, self).__init__(__file__)

    def additional_constraints(self, api, action, ns):
        if action == 'set_fact':
            if not 'key' in ns:
                raise ValueError('no key in ns')
            key = ns['key']

            # see what backend this key is in...
            for name, obj in backends.backend_objects.iteritems():
                if key in obj.facts:
                    return ['"%s" in attrs.backends' % name]

            return None
        if action == 'set_parent':
            if not 'parent' in ns:
                raise ValueError('no parent set')
            parent = api._model_get_by_id('nodes', ns['parent'])
            if 'container' in parent['facts'].get('backends', {}):
                inherited_facts = parent['facts'].get('inherited', {})
                return ['facts.%s="%s"' % (k, v)
                        for k, v in inherited_facts.items()]
            else:
                # cannot set_parent to something that isn't a container
                return None
        return []

    def set_parent(self, api, node_id, **kwargs):
        parent = kwargs['parent']
        api._model_update_by_id('nodes', node_id,
                                {'parent_id': parent})
        return True

    def set_fact(self, api, node_id, **kwargs):
        key, value = kwargs['key'], kwargs['value']
        # if the fact exists, update it, else create it.
        oldkeys = api._model_query('facts', 'node_id=%s and key=%s' %
                                   (node_id, key))

        if len(oldkeys) > 0:
            # update
            api._model_update_by_id('facts', {'id': oldkeys[0]['id'],
                                              'value': value})
        else:
            api._model_create('facts', {'node_id': node_id,
                                        'key': key,
                                        'value': value})

        return True

    def add_backend(self, api, node_id, **kwargs):
        backend = kwargs['backend']
        self.logger.debug('running add_backend')

        roush.webapp.ast.apply_expression(
            node_id, 'facts.backends = union(facts.backends, backend)', api)

        return True
