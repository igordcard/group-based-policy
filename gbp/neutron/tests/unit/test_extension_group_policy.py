#  Licensed under the Apache License, Version 2.0 (the "License"); you may
#  not use this file except in compliance with the License. You may obtain
#  a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#  WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#  License for the specific language governing permissions and limitations
#  under the License.

import copy

import mock
from neutron.openstack.common import uuidutils
from neutron.plugins.common import constants
from neutron.tests import base
from neutron.tests.unit import test_api_v2
from neutron.tests.unit import test_api_v2_extension
from webob import exc

from gbp.neutron.extensions import group_policy as gp

_uuid = uuidutils.generate_uuid
_get_path = test_api_v2._get_path
GP_PLUGIN_BASE_NAME = (
    gp.GroupPolicyPluginBase.__module__ + '.' +
    gp.GroupPolicyPluginBase.__name__)
GROUPPOLICY_URI = 'grouppolicy'
POLICY_TARGETS_URI = GROUPPOLICY_URI + '/' + 'policy_targets'
POLICY_TARGET_GROUPS_URI = GROUPPOLICY_URI + '/' + 'policy_target_groups'
L2_POLICIES_URI = GROUPPOLICY_URI + '/' + 'l2_policies'
L3_POLICIES_URI = GROUPPOLICY_URI + '/' + 'l3_policies'
POLICY_RULES_URI = GROUPPOLICY_URI + '/' + 'policy_rules'
POLICY_CLASSIFIERS_URI = GROUPPOLICY_URI + '/' + 'policy_classifiers'
POLICY_ACTIONS_URI = GROUPPOLICY_URI + '/' + 'policy_actions'
POLICY_RULE_SETS_URI = GROUPPOLICY_URI + '/' + 'policy_rule_sets'
NET_SVC_POLICIES_URI = GROUPPOLICY_URI + '/' + 'network_service_policies'


class GroupPolicyExtensionTestCase(test_api_v2_extension.ExtensionTestCase):
    fmt = 'json'

    def setUp(self):
        super(GroupPolicyExtensionTestCase, self).setUp()
        plural_mappings = {
            'l2_policy': 'l2_policies', 'l3_policy': 'l3_policies',
            'network_service_policy': 'network_service_policies'}
        self._setUpExtension(
            GP_PLUGIN_BASE_NAME, constants.GROUP_POLICY,
            gp.RESOURCE_ATTRIBUTE_MAP, gp.Group_policy, GROUPPOLICY_URI,
            plural_mappings=plural_mappings)
        self.instance = self.plugin.return_value

    def _test_create_policy_target(self, data, expected_value,
                                   default_data=None):
        if not default_data:
            default_data = data
        self.instance.create_policy_target.return_value = expected_value
        res = self.api.post(_get_path(POLICY_TARGETS_URI, fmt=self.fmt),
                            self.serialize(data),
                            content_type='application/%s' % self.fmt)
        self.instance.create_policy_target.assert_called_once_with(
            mock.ANY, policy_target=default_data)
        self.assertEqual(exc.HTTPCreated.code, res.status_int)
        res = self.deserialize(res)
        self.assertIn('policy_target', res)
        self.assertEqual(expected_value, res['policy_target'])

    def _get_create_policy_target_default_attrs(self):
        return {'name': '', 'description': ''}

    def _get_create_policy_target_attrs(self):
        return {'name': 'ep1', 'policy_target_group_id': _uuid(),
                'tenant_id': _uuid(), 'description': 'test policy_target'}

    def _get_update_policy_target_attrs(self):
        return {'name': 'new_name'}

    def test_create_policy_target_with_defaults(self):
        policy_target_id = _uuid()
        data = {'policy_target': {'policy_target_group_id': _uuid(),
                                  'tenant_id': _uuid()}}
        default_attrs = self._get_create_policy_target_default_attrs()
        default_data = copy.copy(data)
        default_data['policy_target'].update(default_attrs)
        expected_value = dict(default_data['policy_target'])
        expected_value['id'] = policy_target_id

        self._test_create_policy_target(data, expected_value, default_data)

    def test_create_policy_target(self):
        policy_target_id = _uuid()
        data = {'policy_target': self._get_create_policy_target_attrs()}
        expected_value = dict(data['policy_target'])
        expected_value['id'] = policy_target_id

        self._test_create_policy_target(data, expected_value)

    def test_list_policy_targets(self):
        policy_target_id = _uuid()
        expected_value = [{'tenant_id': _uuid(), 'id': policy_target_id}]

        self.instance.get_policy_targets.return_value = expected_value

        res = self.api.get(_get_path(POLICY_TARGETS_URI, fmt=self.fmt))

        self.instance.get_policy_targets.assert_called_once_with(
            mock.ANY, fields=mock.ANY, filters=mock.ANY)
        self.assertEqual(exc.HTTPOk.code, res.status_int)
        res = self.deserialize(res)
        self.assertIn('policy_targets', res)
        self.assertEqual(expected_value, res['policy_targets'])

    def test_get_policy_target(self):
        policy_target_id = _uuid()
        expected_value = {'tenant_id': _uuid(), 'id': policy_target_id}

        self.instance.get_policy_target.return_value = expected_value

        res = self.api.get(_get_path(POLICY_TARGETS_URI, id=policy_target_id,
                                     fmt=self.fmt))

        self.instance.get_policy_target.assert_called_once_with(
            mock.ANY, policy_target_id, fields=mock.ANY)
        self.assertEqual(exc.HTTPOk.code, res.status_int)
        res = self.deserialize(res)
        self.assertIn('policy_target', res)
        self.assertEqual(expected_value, res['policy_target'])

    def test_update_policy_target(self):
        policy_target_id = _uuid()
        update_data = {'policy_target': self._get_update_policy_target_attrs()}
        expected_value = {'tenant_id': _uuid(), 'id': policy_target_id}

        self.instance.update_policy_target.return_value = expected_value

        res = self.api.put(_get_path(POLICY_TARGETS_URI, id=policy_target_id,
                                     fmt=self.fmt),
                           self.serialize(update_data))

        self.instance.update_policy_target.assert_called_once_with(
            mock.ANY, policy_target_id, policy_target=update_data)
        self.assertEqual(exc.HTTPOk.code, res.status_int)
        res = self.deserialize(res)
        self.assertIn('policy_target', res)
        self.assertEqual(expected_value, res['policy_target'])

    def test_delete_policy_target(self):
        self._test_entity_delete('policy_target')

    def _test_create_policy_target_group(self, data, expected_value,
                                         default_data=None):
        if not default_data:
            default_data = data

        self.instance.create_policy_target_group.return_value = expected_value
        res = self.api.post(_get_path(POLICY_TARGET_GROUPS_URI, fmt=self.fmt),
                            self.serialize(data),
                            content_type='application/%s' % self.fmt)
        self.instance.create_policy_target_group.assert_called_once_with(
            mock.ANY, policy_target_group=default_data)
        self.assertEqual(exc.HTTPCreated.code, res.status_int)
        res = self.deserialize(res)
        self.assertIn('policy_target_group', res)
        self.assertEqual(expected_value, res['policy_target_group'])

    def _get_create_policy_target_group_default_attrs(self):
        return {'name': '', 'description': '', 'l2_policy_id': None,
                'provided_policy_rule_sets': {},
                'consumed_policy_rule_sets': {},
                'network_service_policy_id': None}

    def _get_create_policy_target_group_attrs(self):
        return {'name': 'ptg1', 'tenant_id': _uuid(),
                'description': 'test policy_target group',
                'l2_policy_id': _uuid(),
                'provided_policy_rule_sets': {_uuid(): None},
                'consumed_policy_rule_sets': {_uuid(): None},
                'network_service_policy_id': _uuid()}

    def _get_update_policy_target_group_attrs(self):
        return {'name': 'new_name'}

    def test_create_policy_target_group_with_defaults(self):
        policy_target_group_id = _uuid()
        data = {'policy_target_group': {'tenant_id': _uuid()}}
        default_attrs = self._get_create_policy_target_group_default_attrs()
        default_data = copy.copy(data)
        default_data['policy_target_group'].update(default_attrs)
        expected_value = copy.deepcopy(default_data['policy_target_group'])
        expected_value['id'] = policy_target_group_id

        self._test_create_policy_target_group(data, expected_value,
                                              default_data)

    def test_create_policy_target_group(self):
        policy_target_group_id = _uuid()
        data = {'policy_target_group':
                self._get_create_policy_target_group_attrs()}
        expected_value = copy.deepcopy(data['policy_target_group'])
        expected_value['id'] = policy_target_group_id

        self._test_create_policy_target_group(data, expected_value)

    def test_list_policy_target_groups(self):
        policy_target_group_id = _uuid()
        expected_value = [{'tenant_id': _uuid(), 'id': policy_target_group_id}]

        self.instance.get_policy_target_groups.return_value = expected_value

        res = self.api.get(_get_path(POLICY_TARGET_GROUPS_URI, fmt=self.fmt))

        self.instance.get_policy_target_groups.assert_called_once_with(
            mock.ANY, fields=mock.ANY, filters=mock.ANY)
        self.assertEqual(exc.HTTPOk.code, res.status_int)
        res = self.deserialize(res)
        self.assertIn('policy_target_groups', res)
        self.assertEqual(expected_value, res['policy_target_groups'])

    def test_get_policy_target_group(self):
        policy_target_group_id = _uuid()
        expected_value = {'tenant_id': _uuid(), 'id': policy_target_group_id}

        self.instance.get_policy_target_group.return_value = expected_value

        res = self.api.get(_get_path(POLICY_TARGET_GROUPS_URI,
                                     id=policy_target_group_id,
                                     fmt=self.fmt))

        self.instance.get_policy_target_group.assert_called_once_with(
            mock.ANY, policy_target_group_id, fields=mock.ANY)
        self.assertEqual(exc.HTTPOk.code, res.status_int)
        res = self.deserialize(res)
        self.assertIn('policy_target_group', res)
        self.assertEqual(expected_value, res['policy_target_group'])

    def test_update_policy_target_group(self):
        policy_target_group_id = _uuid()
        update_data = {'policy_target_group':
                       self._get_update_policy_target_group_attrs()}
        expected_value = {'tenant_id': _uuid(), 'id': policy_target_group_id}

        self.instance.update_policy_target_group.return_value = expected_value

        res = self.api.put(_get_path(POLICY_TARGET_GROUPS_URI,
                                     id=policy_target_group_id, fmt=self.fmt),
                           self.serialize(update_data))

        self.instance.update_policy_target_group.assert_called_once_with(
            mock.ANY, policy_target_group_id, policy_target_group=update_data)
        self.assertEqual(exc.HTTPOk.code, res.status_int)
        res = self.deserialize(res)
        self.assertIn('policy_target_group', res)
        self.assertEqual(expected_value, res['policy_target_group'])

    def test_delete_policy_target_group(self):
        self._test_entity_delete('policy_target_group')

    def _test_create_l2_policy(self, data, expected_value, default_data=None):
        if not default_data:
            default_data = data
        self.instance.create_l2_policy.return_value = expected_value
        res = self.api.post(_get_path(L2_POLICIES_URI, fmt=self.fmt),
                            self.serialize(data),
                            content_type='application/%s' % self.fmt)
        self.instance.create_l2_policy.assert_called_once_with(
            mock.ANY, l2_policy=default_data)
        self.assertEqual(exc.HTTPCreated.code, res.status_int)
        res = self.deserialize(res)
        self.assertIn('l2_policy', res)
        self.assertEqual(expected_value, res['l2_policy'])

    def _get_create_l2_policy_default_attrs(self):
        return {'name': '', 'description': ''}

    def _get_create_l2_policy_attrs(self):
        return {'name': 'l2p1', 'tenant_id': _uuid(),
                'description': 'test L2 policy', 'l3_policy_id': _uuid()}

    def _get_update_l2_policy_attrs(self):
        return {'name': 'new_name'}

    def test_create_l2_policy_with_defaults(self):
        l2_policy_id = _uuid()
        data = {'l2_policy': {'tenant_id': _uuid(), 'l3_policy_id': _uuid()}}
        default_attrs = self._get_create_l2_policy_default_attrs()
        default_data = copy.copy(data)
        default_data['l2_policy'].update(default_attrs)
        expected_value = dict(default_data['l2_policy'])
        expected_value['id'] = l2_policy_id

        self._test_create_l2_policy(data, expected_value, default_data)

    def test_create_l2_policy(self):
        l2_policy_id = _uuid()
        data = {'l2_policy': self._get_create_l2_policy_attrs()}
        expected_value = dict(data['l2_policy'])
        expected_value['id'] = l2_policy_id

        self._test_create_l2_policy(data, expected_value)

    def test_list_l2_policies(self):
        l2_policy_id = _uuid()
        expected_value = [{'tenant_id': _uuid(), 'id': l2_policy_id}]

        self.instance.get_l2_policies.return_value = expected_value

        res = self.api.get(_get_path(L2_POLICIES_URI, fmt=self.fmt))

        self.instance.get_l2_policies.assert_called_once_with(
            mock.ANY, fields=mock.ANY, filters=mock.ANY)
        self.assertEqual(exc.HTTPOk.code, res.status_int)
        res = self.deserialize(res)
        self.assertIn('l2_policies', res)
        self.assertEqual(expected_value, res['l2_policies'])

    def test_get_l2_policy(self):
        l2_policy_id = _uuid()
        expected_value = {'tenant_id': _uuid(), 'id': l2_policy_id}

        self.instance.get_l2_policy.return_value = expected_value

        res = self.api.get(_get_path(L2_POLICIES_URI, id=l2_policy_id,
                                     fmt=self.fmt))

        self.instance.get_l2_policy.assert_called_once_with(
            mock.ANY, l2_policy_id, fields=mock.ANY)
        self.assertEqual(exc.HTTPOk.code, res.status_int)
        res = self.deserialize(res)
        self.assertIn('l2_policy', res)
        self.assertEqual(expected_value, res['l2_policy'])

    def test_update_l2_policy(self):
        l2_policy_id = _uuid()
        update_data = {'l2_policy': self._get_update_l2_policy_attrs()}
        expected_value = {'tenant_id': _uuid(), 'id': l2_policy_id}

        self.instance.update_l2_policy.return_value = expected_value

        res = self.api.put(_get_path(L2_POLICIES_URI, id=l2_policy_id,
                                     fmt=self.fmt),
                           self.serialize(update_data))

        self.instance.update_l2_policy.assert_called_once_with(
            mock.ANY, l2_policy_id, l2_policy=update_data)
        self.assertEqual(exc.HTTPOk.code, res.status_int)
        res = self.deserialize(res)
        self.assertIn('l2_policy', res)
        self.assertEqual(expected_value, res['l2_policy'])

    def test_delete_l2_policy(self):
        self._test_entity_delete('l2_policy')

    def _test_create_l3_policy(self, data, expected_value, default_data=None):
        if not default_data:
            default_data = data
        self.instance.create_l3_policy.return_value = expected_value
        res = self.api.post(_get_path(L3_POLICIES_URI, fmt=self.fmt),
                            self.serialize(data),
                            content_type='application/%s' % self.fmt)
        self.instance.create_l3_policy.assert_called_once_with(
            mock.ANY, l3_policy=default_data)
        self.assertEqual(exc.HTTPCreated.code, res.status_int)
        res = self.deserialize(res)
        self.assertIn('l3_policy', res)
        self.assertEqual(res['l3_policy'], expected_value)

    def _get_create_l3_policy_default_attrs(self):
        return {'name': '', 'description': '', 'ip_version': 4,
                'ip_pool': '10.0.0.0/8', 'subnet_prefix_length': 24}

    def _get_create_l3_policy_attrs(self):
        return {'name': 'l3p1', 'tenant_id': _uuid(),
                'description': 'test L3 policy', 'ip_version': 6,
                'ip_pool': 'fd01:2345:6789::/48',
                'subnet_prefix_length': 64}

    def _get_update_l3_policy_attrs(self):
        return {'name': 'new_name'}

    def test_create_l3_policy_with_defaults(self):
        l3_policy_id = _uuid()
        data = {'l3_policy': {'tenant_id': _uuid()}}
        default_attrs = self._get_create_l3_policy_default_attrs()
        default_data = copy.copy(data)
        default_data['l3_policy'].update(default_attrs)
        expected_value = dict(default_data['l3_policy'])
        expected_value['id'] = l3_policy_id

        self._test_create_l3_policy(data, expected_value, default_data)

    def test_create_l3_policy(self):
        l3_policy_id = _uuid()
        data = {'l3_policy': self._get_create_l3_policy_attrs()}
        expected_value = dict(data['l3_policy'])
        expected_value.update({'id': l3_policy_id})

        self._test_create_l3_policy(data, expected_value)

    def test_list_l3_policies(self):
        l3_policy_id = _uuid()
        expected_value = [{'tenant_id': _uuid(), 'id': l3_policy_id}]

        self.instance.get_l3_policies.return_value = expected_value

        res = self.api.get(_get_path(L3_POLICIES_URI, fmt=self.fmt))

        self.instance.get_l3_policies.assert_called_once_with(
            mock.ANY, fields=mock.ANY, filters=mock.ANY)
        self.assertEqual(exc.HTTPOk.code, res.status_int)
        res = self.deserialize(res)
        self.assertIn('l3_policies', res)
        self.assertEqual(expected_value, res['l3_policies'])

    def test_get_l3_policy(self):
        l3_policy_id = _uuid()
        expected_value = {'tenant_id': _uuid(), 'id': l3_policy_id}

        self.instance.get_l3_policy.return_value = expected_value

        res = self.api.get(_get_path(L3_POLICIES_URI, id=l3_policy_id,
                                     fmt=self.fmt))

        self.instance.get_l3_policy.assert_called_once_with(
            mock.ANY, l3_policy_id, fields=mock.ANY)
        self.assertEqual(exc.HTTPOk.code, res.status_int)
        res = self.deserialize(res)
        self.assertIn('l3_policy', res)
        self.assertEqual(expected_value, res['l3_policy'])

    def test_update_l3_policy(self):
        l3_policy_id = _uuid()
        update_data = {'l3_policy': self._get_update_l3_policy_attrs()}
        expected_value = {'tenant_id': _uuid(), 'id': l3_policy_id}

        self.instance.update_l3_policy.return_value = expected_value

        res = self.api.put(_get_path(L3_POLICIES_URI, id=l3_policy_id,
                                     fmt=self.fmt),
                           self.serialize(update_data))

        self.instance.update_l3_policy.assert_called_once_with(
            mock.ANY, l3_policy_id, l3_policy=update_data)
        self.assertEqual(exc.HTTPOk.code, res.status_int)
        res = self.deserialize(res)
        self.assertIn('l3_policy', res)
        self.assertEqual(expected_value, res['l3_policy'])

    def test_delete_l3_policy(self):
        self._test_entity_delete('l3_policy')

    def _test_create_policy_action(self, data, expected_value,
                                   default_data=None):
        if not default_data:
            default_data = data

        self.instance.create_policy_action.return_value = expected_value
        res = self.api.post(_get_path(POLICY_ACTIONS_URI, fmt=self.fmt),
                            self.serialize(data),
                            content_type='application/%s' % self.fmt)
        self.instance.create_policy_action.assert_called_once_with(
            mock.ANY, policy_action=default_data)
        self.assertEqual(exc.HTTPCreated.code, res.status_int)
        res = self.deserialize(res)
        self.assertIn('policy_action', res)
        self.assertEqual(expected_value, res['policy_action'])

    def _get_create_policy_action_default_attrs(self):
        return {'name': '',
                'description': '',
                'action_type': 'allow',
                'action_value': None}

    def _get_create_policy_action_attrs(self):
        return {'name': 'pa1',
                'tenant_id': _uuid(),
                'description': 'test policy action',
                'action_type': 'redirect',
                'action_value': _uuid()}

    def _get_update_policy_action_attrs(self):
        return {'name': 'new_name'}

    def test_create_policy_action_with_defaults(self):
        policy_action_id = _uuid()
        data = {'policy_action': {'tenant_id': _uuid()}}
        default_attrs = self._get_create_policy_action_default_attrs()
        default_data = copy.copy(data)
        default_data['policy_action'].update(default_attrs)
        expected_value = dict(default_data['policy_action'])
        expected_value['id'] = policy_action_id

        self._test_create_policy_action(data, expected_value, default_data)

    def test_create_policy_action(self):
        policy_action_id = _uuid()
        data = {'policy_action': self._get_create_policy_action_attrs()}
        expected_value = dict(data['policy_action'])
        expected_value['id'] = policy_action_id

        self._test_create_policy_action(data, expected_value)

    def test_list_policy_actions(self):
        policy_action_id = _uuid()
        expected_value = [{'tenant_id': _uuid(),
                           'id': policy_action_id}]

        instance = self.plugin.return_value
        instance.get_policy_actions.return_value = expected_value

        res = self.api.get(_get_path(POLICY_ACTIONS_URI, fmt=self.fmt))

        instance.get_policy_actions.assert_called_once_with(mock.ANY,
                                                            fields=mock.ANY,
                                                            filters=mock.ANY)
        self.assertEqual(res.status_int, exc.HTTPOk.code)

    def test_get_policy_action(self):
        policy_action_id = _uuid()
        expected_value = {'tenant_id': _uuid(),
                          'id': policy_action_id}

        instance = self.plugin.return_value
        instance.get_policy_action.return_value = expected_value

        res = self.api.get(_get_path(POLICY_ACTIONS_URI,
                                     id=policy_action_id, fmt=self.fmt))

        instance.get_policy_action.assert_called_once_with(mock.ANY,
                                                           policy_action_id,
                                                           fields=mock.ANY)
        self.assertEqual(res.status_int, exc.HTTPOk.code)
        res = self.deserialize(res)
        self.assertIn('policy_action', res)
        self.assertEqual(expected_value, res['policy_action'])

    def test_update_policy_action(self):
        policy_action_id = _uuid()
        update_data = {'policy_action':
                       self._get_update_policy_action_attrs()}
        expected_value = {'tenant_id': _uuid(),
                          'id': policy_action_id}

        instance = self.plugin.return_value
        instance.update_policy_action.return_value = expected_value

        res = self.api.put(_get_path(POLICY_ACTIONS_URI,
                                     id=policy_action_id,
                                     fmt=self.fmt),
                           self.serialize(update_data))

        instance.update_policy_action.assert_called_once_with(
            mock.ANY, policy_action_id, policy_action=update_data)
        self.assertEqual(res.status_int, exc.HTTPOk.code)
        res = self.deserialize(res)
        self.assertIn('policy_action', res)
        self.assertEqual(expected_value, res['policy_action'])

    def test_delete_policy_action(self):
        self._test_entity_delete('policy_action')

    def _test_create_policy_classifier(self, data, expected_value,
                                       default_data=None):
        if not default_data:
            default_data = data

        self.instance.create_policy_classifier.return_value = expected_value
        res = self.api.post(_get_path(POLICY_CLASSIFIERS_URI, fmt=self.fmt),
                            self.serialize(data),
                            content_type='application/%s' % self.fmt)
        self.instance.create_policy_classifier.assert_called_once_with(
            mock.ANY, policy_classifier=default_data)
        self.assertEqual(exc.HTTPCreated.code, res.status_int)
        res = self.deserialize(res)
        self.assertIn('policy_classifier', res)
        self.assertEqual(expected_value, res['policy_classifier'])

    def _get_create_policy_classifier_default_attrs(self):
        return {'name': '',
                'description': '',
                'protocol': None,
                'port_range': None,
                'direction': None}

    def _get_create_policy_classifier_attrs(self):
        return {'name': 'pc1',
                'description': 'test policy classifier',
                'tenant_id': _uuid(),
                'protocol': 'tcp',
                'port_range': '100:200',
                'direction': 'in'}

    def _get_update_policy_classifier_attrs(self):
        return {'name': 'new_name'}

    def test_create_policy_classifier_with_defaults(self):
        policy_classifier_id = _uuid()
        data = {'policy_classifier': {'tenant_id': _uuid()}}
        default_attrs = self._get_create_policy_classifier_default_attrs()
        default_data = copy.copy(data)
        default_data['policy_classifier'].update(default_attrs)
        expected_value = dict(default_data['policy_classifier'])
        expected_value['id'] = policy_classifier_id

        self._test_create_policy_classifier(data, expected_value, default_data)

    def test_create_policy_classifier(self):
        policy_classifier_id = _uuid()
        data = {'policy_classifier':
                self._get_create_policy_classifier_attrs()}
        expected_value = dict(data['policy_classifier'])
        expected_value['id'] = policy_classifier_id

        self._test_create_policy_classifier(data, expected_value)

    def test_list_policy_classifiers(self):
        policy_classifier_id = _uuid()
        expected_value = [{'tenant_id': _uuid(),
                           'id': policy_classifier_id}]

        instance = self.plugin.return_value
        instance.get_policy_classifiers.return_value = expected_value

        res = self.api.get(_get_path(POLICY_CLASSIFIERS_URI, fmt=self.fmt))

        instance.get_policy_classifiers.assert_called_once_with(
            mock.ANY, fields=mock.ANY, filters=mock.ANY)
        self.assertEqual(res.status_int, exc.HTTPOk.code)

    def test_get_policy_classifier(self):
        policy_classifier_id = _uuid()
        expected_value = {'tenant_id': _uuid(),
                          'id': policy_classifier_id}

        instance = self.plugin.return_value
        instance.get_policy_classifier.return_value = expected_value

        res = self.api.get(_get_path(POLICY_CLASSIFIERS_URI,
                                     id=policy_classifier_id, fmt=self.fmt))

        instance.get_policy_classifier.assert_called_once_with(
            mock.ANY, policy_classifier_id, fields=mock.ANY)
        self.assertEqual(res.status_int, exc.HTTPOk.code)
        res = self.deserialize(res)
        self.assertIn('policy_classifier', res)
        self.assertEqual(expected_value, res['policy_classifier'])

    def test_update_policy_classifier(self):
        policy_classifier_id = _uuid()
        update_data = {'policy_classifier':
                       self._get_update_policy_classifier_attrs()}
        expected_value = {'tenant_id': _uuid(),
                          'id': policy_classifier_id}

        instance = self.plugin.return_value
        instance.update_policy_classifier.return_value = expected_value

        res = self.api.put(_get_path(POLICY_CLASSIFIERS_URI,
                                     id=policy_classifier_id,
                                     fmt=self.fmt),
                           self.serialize(update_data))

        instance.update_policy_classifier.assert_called_once_with(
            mock.ANY, policy_classifier_id, policy_classifier=update_data)
        self.assertEqual(res.status_int, exc.HTTPOk.code)
        res = self.deserialize(res)
        self.assertIn('policy_classifier', res)
        self.assertEqual(expected_value, res['policy_classifier'])

    def test_delete_policy_classifier(self):
        self._test_entity_delete('policy_action')

    def _test_create_policy_rule(self, data, expected_value,
                                 default_data=None):
        if not default_data:
            default_data = data

        self.instance.create_policy_rule.return_value = expected_value
        res = self.api.post(_get_path(POLICY_RULES_URI, fmt=self.fmt),
                            self.serialize(data),
                            content_type='application/%s' % self.fmt)
        self.instance.create_policy_rule.assert_called_once_with(
            mock.ANY, policy_rule=default_data)
        self.assertEqual(exc.HTTPCreated.code, res.status_int)
        res = self.deserialize(res)
        self.assertIn('policy_rule', res)
        self.assertEqual(expected_value, res['policy_rule'])

    def _get_create_policy_rule_default_attrs(self):
        return {'name': '',
                'description': '',
                'enabled': True,
                'policy_actions': []}

    def _get_create_policy_rule_attrs(self):
        return {'name': 'pr1',
                'description': 'test policy rule',
                'tenant_id': _uuid(),
                'enabled': True,
                'policy_classifier_id': _uuid(),
                'policy_actions': [_uuid()]}

    def _get_update_policy_rule_attrs(self):
        return {'name': 'new_name'}

    def test_create_policy_rule_with_defaults(self):
        policy_rule_id = _uuid()
        data = {'policy_rule': {'tenant_id': _uuid(), 'policy_classifier_id':
                                _uuid()}}
        default_attrs = self._get_create_policy_rule_default_attrs()
        default_data = copy.copy(data)
        default_data['policy_rule'].update(default_attrs)
        expected_value = dict(default_data['policy_rule'])
        expected_value['id'] = policy_rule_id

        self._test_create_policy_rule(data, expected_value, default_data)

    def test_create_policy_rule(self):
        policy_rule_id = _uuid()
        data = {'policy_rule':
                self._get_create_policy_rule_attrs()}
        expected_value = dict(data['policy_rule'])
        expected_value['id'] = policy_rule_id

        self._test_create_policy_rule(data, expected_value)

    def test_list_policy_rules(self):
        policy_rule_id = _uuid()
        expected_value = [{'tenant_id': _uuid(),
                           'id': policy_rule_id}]

        instance = self.plugin.return_value
        instance.get_policy_rules.return_value = expected_value

        res = self.api.get(_get_path(POLICY_RULES_URI, fmt=self.fmt))

        instance.get_policy_rules.assert_called_once_with(mock.ANY,
                                                          fields=mock.ANY,
                                                          filters=mock.ANY)
        self.assertEqual(res.status_int, exc.HTTPOk.code)

    def test_get_policy_rule(self):
        policy_rule_id = _uuid()
        expected_value = {'tenant_id': _uuid(),
                          'id': policy_rule_id}

        instance = self.plugin.return_value
        instance.get_policy_rule.return_value = expected_value

        res = self.api.get(_get_path(POLICY_RULES_URI,
                                     id=policy_rule_id, fmt=self.fmt))

        instance.get_policy_rule.assert_called_once_with(
            mock.ANY, policy_rule_id, fields=mock.ANY)
        self.assertEqual(res.status_int, exc.HTTPOk.code)
        res = self.deserialize(res)
        self.assertIn('policy_rule', res)
        self.assertEqual(expected_value, res['policy_rule'])

    def test_update_policy_rule(self):
        policy_rule_id = _uuid()
        update_data = {'policy_rule':
                       self._get_update_policy_rule_attrs()}
        expected_value = {'tenant_id': _uuid(),
                          'id': policy_rule_id}

        instance = self.plugin.return_value
        instance.update_policy_rule.return_value = expected_value

        res = self.api.put(_get_path(POLICY_RULES_URI,
                                     id=policy_rule_id,
                                     fmt=self.fmt),
                           self.serialize(update_data))

        instance.update_policy_rule.assert_called_once_with(
            mock.ANY, policy_rule_id, policy_rule=update_data)
        self.assertEqual(res.status_int, exc.HTTPOk.code)
        res = self.deserialize(res)
        self.assertIn('policy_rule', res)
        self.assertEqual(expected_value, res['policy_rule'])

    def test_delete_policy_rule(self):
        self._test_entity_delete('policy_action')

    def _test_create_policy_rule_set(self, data, expected_value,
                                     default_data=None):
        if not default_data:
            default_data = data

        self.instance.create_policy_rule_set.return_value = expected_value
        res = self.api.post(_get_path(POLICY_RULE_SETS_URI, fmt=self.fmt),
                            self.serialize(data),
                            content_type='application/%s' % self.fmt)
        self.instance.create_policy_rule_set.assert_called_once_with(
            mock.ANY, policy_rule_set=default_data)
        self.assertEqual(res.status_int, exc.HTTPCreated.code)
        res = self.deserialize(res)
        self.assertIn('policy_rule_set', res)
        self.assertEqual(expected_value, res['policy_rule_set'])

    def _get_create_policy_rule_set_default_attrs(self):
        return {'name': '',
                'description': '',
                'child_policy_rule_sets': [],
                'policy_rules': []}

    def _get_create_policy_rule_set_attrs(self):
        return {'name': 'policy_rule_set1',
                'description': 'test policy_rule_set',
                'tenant_id': _uuid(),
                'child_policy_rule_sets': [_uuid()],
                'policy_rules': [_uuid()]}

    def _get_update_policy_rule_set_attrs(self):
        return {'name': 'new_name'}

    def test_create_policy_rule_set_with_defaults(self):
        policy_rule_set_id = _uuid()
        data = {'policy_rule_set': {'tenant_id': _uuid()}}
        default_attrs = self._get_create_policy_rule_set_default_attrs()
        default_data = copy.copy(data)
        default_data['policy_rule_set'].update(default_attrs)
        expected_value = dict(default_data['policy_rule_set'])
        expected_value['id'] = policy_rule_set_id

        self._test_create_policy_rule_set(data, expected_value, default_data)

    def test_create_policy_rule_set(self):
        policy_rule_set_id = _uuid()
        data = {'policy_rule_set':
                self._get_create_policy_rule_set_attrs()}
        expected_value = dict(data['policy_rule_set'])
        expected_value['id'] = policy_rule_set_id

        self._test_create_policy_rule_set(data, expected_value)

    def test_list_policy_rule_sets(self):
        policy_rule_set_id = _uuid()
        expected_value = [{'tenant_id': _uuid(),
                           'id': policy_rule_set_id}]

        instance = self.plugin.return_value
        instance.get_policy_rule_sets.return_value = expected_value

        res = self.api.get(_get_path(POLICY_RULE_SETS_URI, fmt=self.fmt))

        instance.get_policy_rule_sets.assert_called_once_with(
            mock.ANY, fields=mock.ANY, filters=mock.ANY)
        self.assertEqual(res.status_int, exc.HTTPOk.code)

    def test_get_policy_rule_set(self):
        policy_rule_set_id = _uuid()
        expected_value = {'tenant_id': _uuid(),
                          'id': policy_rule_set_id}

        instance = self.plugin.return_value
        instance.get_policy_rule_set.return_value = expected_value

        res = self.api.get(_get_path(POLICY_RULE_SETS_URI,
                                     id=policy_rule_set_id, fmt=self.fmt))

        instance.get_policy_rule_set.assert_called_once_with(
            mock.ANY, policy_rule_set_id, fields=mock.ANY)
        self.assertEqual(res.status_int, exc.HTTPOk.code)
        res = self.deserialize(res)
        self.assertIn('policy_rule_set', res)
        self.assertEqual(expected_value, res['policy_rule_set'])

    def test_update_policy_rule_set(self):
        policy_rule_set_id = _uuid()
        update_data = {'policy_rule_set':
                       self._get_update_policy_rule_set_attrs()}
        expected_value = {'tenant_id': _uuid(),
                          'id': policy_rule_set_id}

        instance = self.plugin.return_value
        instance.update_policy_rule_set.return_value = expected_value

        res = self.api.put(_get_path(POLICY_RULE_SETS_URI,
                                     id=policy_rule_set_id,
                                     fmt=self.fmt),
                           self.serialize(update_data))

        instance.update_policy_rule_set.assert_called_once_with(
            mock.ANY, policy_rule_set_id, policy_rule_set=update_data)
        self.assertEqual(res.status_int, exc.HTTPOk.code)
        res = self.deserialize(res)
        self.assertIn('policy_rule_set', res)
        self.assertEqual(expected_value, res['policy_rule_set'])

    def test_delete_policy_rule_set(self):
        self._test_entity_delete('policy_rule_set')

    def _test_create_network_service_policy(
        self, data, expected_value, default_data=None):
        if not default_data:
            default_data = data
        create_svc_policy = self.instance.create_network_service_policy
        create_svc_policy.return_value = expected_value
        res = self.api.post(_get_path(NET_SVC_POLICIES_URI, fmt=self.fmt),
                            self.serialize(data),
                            content_type='application/%s' % self.fmt)
        create_svc_policy.assert_called_once_with(
            mock.ANY, network_service_policy=default_data)
        self.assertEqual(exc.HTTPCreated.code, res.status_int)
        res = self.deserialize(res)
        self.assertIn('network_service_policy', res)
        self.assertEqual(expected_value, res['network_service_policy'])

    def _get_create_network_service_policy_default_attrs(self):
        return {'name': '', 'description': '',
                'network_service_params': []}

    def _get_create_network_service_policy_attrs(self):
        return {'name': 'nsp1', 'tenant_id': _uuid(),
                'description': 'test Net Svc Policy',
                'network_service_params': [{'type': 'ip_single', 'name': 'vip',
                                            'value': 'self_subnet'}]}

    def _get_update_network_service_policy_attrs(self):
        return {'name': 'new_name'}

    def test_create_network_service_policy_with_defaults(self):
        network_service_policy_id = _uuid()
        data = {'network_service_policy': {'tenant_id': _uuid()}}
        default_attrs = self._get_create_network_service_policy_default_attrs()
        default_data = copy.copy(data)
        default_data['network_service_policy'].update(default_attrs)
        expected_value = dict(default_data['network_service_policy'])
        expected_value['id'] = network_service_policy_id

        self._test_create_network_service_policy(
            data, expected_value, default_data)

    def test_create_network_service_policy(self):
        network_service_policy_id = _uuid()
        data = {'network_service_policy':
                self._get_create_network_service_policy_attrs()}
        expected_value = copy.deepcopy(data['network_service_policy'])
        expected_value['id'] = network_service_policy_id

        self._test_create_network_service_policy(data, expected_value)

    def test_list_network_service_policies(self):
        network_service_policy_id = _uuid()
        expected_value = [{'tenant_id': _uuid(),
                           'id': network_service_policy_id}]

        get_svc_policies = self.instance.get_network_service_policies
        get_svc_policies.return_value = expected_value

        res = self.api.get(_get_path(NET_SVC_POLICIES_URI, fmt=self.fmt))

        get_svc_policies.assert_called_once_with(
            mock.ANY, fields=mock.ANY, filters=mock.ANY)
        self.assertEqual(exc.HTTPOk.code, res.status_int)
        res = self.deserialize(res)
        self.assertIn('network_service_policies', res)
        self.assertEqual(expected_value, res['network_service_policies'])

    def test_get_network_service_policy(self):
        network_service_policy_id = _uuid()
        expected_value = {'tenant_id': _uuid(),
                          'id': network_service_policy_id}

        self.instance.get_network_service_policy.return_value = expected_value

        res = self.api.get(_get_path(NET_SVC_POLICIES_URI,
                                     id=network_service_policy_id,
                                     fmt=self.fmt))

        self.instance.get_network_service_policy.assert_called_once_with(
            mock.ANY, network_service_policy_id, fields=mock.ANY)
        self.assertEqual(exc.HTTPOk.code, res.status_int)
        res = self.deserialize(res)
        self.assertIn('network_service_policy', res)
        self.assertEqual(expected_value, res['network_service_policy'])

    def test_update_network_service_policy(self):
        network_service_policy_id = _uuid()
        update_data = {'network_service_policy':
                       self._get_update_network_service_policy_attrs()}
        expected_value = {'tenant_id': _uuid(),
                          'id': network_service_policy_id}

        update_svc_policy = self.instance.update_network_service_policy
        update_svc_policy.return_value = expected_value

        res = self.api.put(_get_path(NET_SVC_POLICIES_URI,
                                     id=network_service_policy_id,
                                     fmt=self.fmt),
                           self.serialize(update_data))

        update_svc_policy.assert_called_once_with(
            mock.ANY, network_service_policy_id,
            network_service_policy=update_data)
        self.assertEqual(exc.HTTPOk.code, res.status_int)
        res = self.deserialize(res)
        self.assertIn('network_service_policy', res)
        self.assertEqual(expected_value, res['network_service_policy'])

    def test_delete_network_service_policy(self):
        self._test_entity_delete('network_service_policy')


class TestGroupPolicyAttributeConverters(base.BaseTestCase):

    def test_convert_action_to_case_insensitive(self):
        self.assertEqual(
            gp.convert_action_to_case_insensitive('ALLOW'), 'allow')
        self.assertEqual(gp.convert_action_to_case_insensitive('In'), 'in')
        self.assertEqual(gp.convert_action_to_case_insensitive('bi'), 'bi')
        self.assertEqual(gp.convert_action_to_case_insensitive(''), '')

    def test_convert_port_to_string(self):
        self.assertEqual(gp.convert_port_to_string(100), '100')
        self.assertEqual(gp.convert_port_to_string('200'), '200')
        self.assertEqual(gp.convert_port_to_string(''), '')

    def test_convert_protocol_check_valid_protocols(self):
        self.assertEqual(gp.convert_protocol('tcp'), constants.TCP)
        self.assertEqual(gp.convert_protocol('TCP'), constants.TCP)
        self.assertEqual(gp.convert_protocol('udp'), constants.UDP)
        self.assertEqual(gp.convert_protocol('UDP'), constants.UDP)
        self.assertEqual(gp.convert_protocol('icmp'), constants.ICMP)
        self.assertEqual(gp.convert_protocol('ICMP'), constants.ICMP)

    def test_convert_protocol_check_invalid_protocols(self):
        self.assertRaises(gp.GroupPolicyInvalidProtocol,
                          gp.convert_protocol, 'garbage')

    def test_convert_numeric_protocol(self):
        self.assertIsInstance(gp.convert_protocol('2'), str)

    def test_convert_bad_protocol(self):
        for val in ['bad', '256', '-1']:
            self.assertRaises(
                gp.GroupPolicyInvalidProtocol, gp.convert_protocol, val)


class TestGroupPolicyAttributeValidators(base.BaseTestCase):

    def test_validate_port_range(self):
        self.assertIsNone(gp._validate_port_range(None))
        self.assertIsNone(gp._validate_port_range('10'))
        self.assertIsNone(gp._validate_port_range(10))
        self.assertEqual(gp._validate_port_range(-1),
                         "Invalid port '-1', valid range 0 < port < 65536")
        self.assertEqual(gp._validate_port_range('66000'),
                         "Invalid port '66000', valid range 0 < port < 65536")
        self.assertIsNone(gp._validate_port_range('10:20'))
        self.assertIsNone(gp._validate_port_range('1:65535'))
        self.assertEqual(gp._validate_port_range('0:65535'),
                         "Invalid port '0', valid range 0 < port < 65536")
        self.assertEqual(gp._validate_port_range('1:65536'),
                         "Invalid port '65536', valid range 0 < port < 65536")
        msg = gp._validate_port_range('abc:efg')
        self.assertEqual(msg, "Port value 'abc' is not a valid number")
        msg = gp._validate_port_range('1:efg')
        self.assertEqual(msg, "Port value 'efg' is not a valid number")
        msg = gp._validate_port_range('-1:10')
        self.assertEqual(msg,
                         "Invalid port '-1', valid range 0 < port < 65536")
        msg = gp._validate_port_range('66000:10')
        self.assertEqual(msg,
                         "Invalid port '66000', valid range 0 < port < 65536")
        msg = gp._validate_port_range('10:66000')
        self.assertEqual(msg,
                         "Invalid port '66000', valid range 0 < port < 65536")
        msg = gp._validate_port_range('1:-10')
        self.assertEqual(msg,
                         "Invalid port '-10', valid range 0 < port < 65536")
        msg = gp._validate_port_range('1:2:3')
        self.assertEqual(msg, "Port value '2:3' is not a valid number")
        msg = gp._validate_port_range('3:2')
        self.assertEqual(
            msg, "Invalid port range: 3:2, valid range 0 < port1 < port2")
        msg = gp._validate_port_range('2:2')
        self.assertEqual(
            msg, "Invalid port range: 2:2, valid range 0 < port1 < port2")

    def test_validate_network_service_params(self):
        test_params = [{'type': 'ip_single', 'name': 'vip_internal',
                       'value': 'self_subnet'}]
        self.assertIsNone(gp._validate_network_svc_params(test_params))
        test_params = [{'type': 'ip_pool', 'name': 'vip_internal',
                       'value': 'external_subnet'},
                       {'type': 'string', 'name': 'abc', 'value': 'xyz'}]
        self.assertIsNone(gp._validate_network_svc_params(test_params))

    def test_validate_network_service_params_not_a_listt(self):
        test_params = 'ip'
        msg = gp._validate_network_svc_params(test_params)
        self.assertEqual(msg, "'ip' is not a list")

    def test_validate_network_service_params_element_not_a_dict(self):
        test_params = ['ip']
        msg = gp._validate_network_svc_params(test_params)
        self.assertEqual(msg, "'ip' is not a dictionary")

    def test_validate_network_service_params_bad_type(self):
        test_params = [{'type': 'ip_', 'name': 'vip', 'value': 'self_subnet'}]
        msg = gp._validate_network_svc_params(test_params)
        self.assertEqual(
            msg, "Network service param type(s) 'ip_' not supported")

    def test_validate_network_service_params_bad_key(self):
        test_params = [{'type': 'ip_pool', 'n': 'vip', 'value': 'self_subnet'}]
        msg = gp._validate_network_svc_params(test_params)
        self.assertEqual(
            msg, "Unknown key(s) 'n' in network service params")

    def test_validate_network_service_params_bad_value(self):
        test_params = [{'type': 'ip_pool', 'name': 'vip', 'value': 'subnet'}]
        msg = gp._validate_network_svc_params(test_params)
        self.assertEqual(
            msg, "Network service param value 'subnet' is not supported")