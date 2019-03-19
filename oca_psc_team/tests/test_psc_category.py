# Copyright 2019 Surekha Technologies (https://www.surekhatech.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo.exceptions import AccessError
from odoo.tests import common


class TestPscCategoryAccessRights(common.TransactionCase):

    def setUp(self):
        super(TestPscCategoryAccessRights, self).setUp()

        user_obj = self.env['res.users'].with_context(
            {'no_reset_password': True, 'mail_create_nosubscribe': True})

        self.project_user = user_obj.create({
            'name': 'User 1',
            'login': 'project_user',
            'email': 'project_user@example.com',
            'notification_type': 'inbox',
            'groups_id': [
                (6, 0, [self.env.ref('project.group_project_user').id])]
        })

        self.project_manager = user_obj.create({
            'name': 'User 2',
            'login': 'project_manager',
            'email': 'project_manager@example.com',
            'notification_type': 'inbox',
            'groups_id': [
                (6, 0, [self.env.ref('project.group_project_manager').id])]
        })

        self.psc_category_1 = self.env['psc.category'].create({
            'name': 'PSC Category 1',
            'description': 'Modules related to PSC category 1',
        })

    def test_project_user_access_rights(self):
        self.env = self.env(user=self.project_user)

        # check for read access
        self.assertEqual(
            self.psc_category_1.name, 'PSC Category 1'
        )

        # check for create access
        with self.assertRaises(AccessError):
            self.psc_category_2 = self.env['psc.category'].create({
                'name': 'PSC Category 2',
                'description': 'Modules related to PSC category 2',
            })

        # check for unlink access
        with self.assertRaises(AccessError):
            self.psc_category_1.sudo(self.project_user).unlink()

        # check for write access
        with self.assertRaises(AccessError):
            self.psc_category_1.sudo(self.project_user).write({
                'description': 'Test description'
            })

    def test_project_manager_access_rights(self):
        self.env = self.env(user=self.project_manager)

        # check for read access
        self.assertEqual(
            self.psc_category_1.name, 'PSC Category 1'
        )

        # check for create access
        self.psc_category_2 = self.env['psc.category'].create({
            'name': 'PSC Category 2',
            'description': 'Modules related to PSC category 1',
        })

        # check for unlink access
        self.psc_category_2.sudo(self.project_manager).unlink()

        # check for write access
        self.psc_category_1.sudo(self.project_manager).write({
            'description': 'Test description'
        })
