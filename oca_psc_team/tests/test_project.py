# Copyright 2019 Surekha Technologies (https://www.surekhatech.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo.exceptions import AccessError, ValidationError
from odoo.tests import common


class TestProject(common.TransactionCase):

    def setUp(self):
        super(TestProject, self).setUp()

        self.psc_category_1 = self.env['psc.category'].create({
            'name': 'PSC category 1',
            'description': 'Modules related to PSC category 1',
        })

        self.psc_category_2 = self.env['psc.category'].create({
            'name': 'PSC category 2',
            'description': 'Modules related to PSC category 2',
        })

        self.project_1 = self.env['project.project'].create({
            'name': 'Project 1',
            'label_tasks': 'Task 1',
            'psc_category_id': self.psc_category_1.id,
        })

        self.project_2 = self.env['project.project'].create({
            'name': 'Project 2',
            'label_tasks': 'Task 2',
        })

        self.github_repository_1 = self.env['github.repository'].create({
            'organization_id': self.ref(
                'oca_psc_team.github_organization_1_demo'),
            'name': 'Repository 1',
            'project_id': self.project_1.id
        })

        self.github_repository_2 = self.env['github.repository'].create({
            'organization_id': self.ref(
                'oca_psc_team.github_organization_1_demo'),
            'name': 'Repository 2',
        })

    def test_project_short_description_validation(self):
        with self.assertRaises(ValidationError):
            self.project_1.write({
                'short_description': 'This project aims to deal with modules'
                                     ' related to the webclient of Odoo '
                                     'version 11.',
            })

    def test_github_project_link(self):
        # assign project to github repository.
        self.github_repository_2.write({
            'project_id': self.project_1.id
        })

        self.assertEqual(len(self.project_1.github_repository_ids), 2)

        # assign github repository to project.
        self.project_2.write({
            'github_repository_ids': [(6, 0, [self.github_repository_1.id])]
        })

        self.assertEqual(
            self.github_repository_1.project_id,
            self.project_2
        )

    def test_project_psc_category_link(self):
        self.psc_category_1.write({
            'project_ids': [(4, self.project_2.id)]
        })

        self.assertEqual(len(self.psc_category_1.project_ids), 2)

        self.project_1.write({
            'psc_category_id': self.psc_category_2.id,
            'description': 'Modules related to PSC category 1',
        })

        self.assertEqual(
            self.psc_category_2.project_ids,
            self.project_1
        )


class TestPscCategoryAccessRight(common.TransactionCase):

    def setUp(self):
        super(TestPscCategoryAccessRight, self).setUp()

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

    def test_project_user_access_right(self):
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

    def test_project_manager_access_right(self):
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
