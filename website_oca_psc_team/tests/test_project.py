# Copyright 2019 Surekha Technologies (https://www.surekhatech.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo.tests import common


class TestProject(common.TransactionCase):

    def setUp(self):
        super(TestProject, self).setUp()

        self.project = self.env['project.project'].create({
            'name': 'Website Redesign',
            'label_tasks': 'Task',
        })

    def test_description(self):

        self.project.write({
            'description': 'This project aims to deal with modules'
                           ' related to the webclient of Odoo.',
        })

        self.assertEqual(
            self.project.description,
            '<p>This project aims to deal with modules '
            'related to the webclient of Odoo.</p>')
