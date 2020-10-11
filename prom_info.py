#!/usr/bin/env python

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import requests, json
from ansible.module_utils.basic import AnsibleModule
from prometheus_client.parser import text_string_to_metric_families

def run_module():
    module_args = dict(
        metrics=dict(required=True),
        hosts=dict(type='str')
    )

    result = dict(
        changed=False,
        metrics=dict(type='str')
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    if module.check_mode:
        module.exit_json(**result)

    args = json.loads(module.params['metrics'].strip().replace('\'', '\"'))
    hosts = json.loads(module.params['hosts'].strip().replace('\'', '\"'))
    metrics = {}
    
    for host in hosts:
        host_metrics = {}
        metrics_url = 'http://%s:9100/metrics' % host

        try:
            r = requests.get(metrics_url)
        except: 
            module.fail_json(msg='No metrics on %s was found' % metrics_url, **result)

        try:
            for family in text_string_to_metric_families(r.text):
                if family.name in args:
                    host_metrics[family.name] = family.samples[0].value
                    print(family.samples[0])
        except:
            module.fail_json(msg='Error occuped', **result)
        
        metrics[host] = host_metrics

    result['metrics'] = metrics
    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()
