# test_models.py
from django.core.exceptions import ValidationError
from django.utils.translation import activate
from django.test import TestCase
from catalog.models import Group
from django.utils.translation import override

class GroupModelTest(TestCase):
    def test_group_str_method(self):
        """
        Test __str__ method for a Group model.
        """
        group = Group.objects.create(group_name_cs="Skupina CZ", group_name_en="Group EN")

        # Test for the Czech language
        activate("cs")
        self.assertEqual(str(group), "Skupina CZ")

        # Test for English language
        activate("en")
        self.assertEqual(str(group), "Group EN")

        # Test the string representation with an unrecognized language (default to English)
        activate("de")
        self.assertEqual(str(group), "Group EN")


class GroupModelCleanTest(TestCase):
    def test_clean_method_raises_error_for_identical_names(self):
        """
        Test that the `clean()` method raises a ValidationError if the Czech
        and English group names are identical.
        """

        group = Group(group_name_cs="Same Name", group_name_en="Same Name")

        # Test češtiny
        with override("cs"):
            with self.assertRaises(ValidationError) as context:
                group.clean()
            self.assertIn("České i anglické pojmenování skupiny musí být odlišné", str(context.exception))

        # Test angličtiny
        with override("en"):
            with self.assertRaises(ValidationError) as context:
                group.clean()
            self.assertIn("The Czech and English group name must be different", str(context.exception))


