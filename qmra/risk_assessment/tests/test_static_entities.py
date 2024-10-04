from unittest import TestCase
from assertpy import assert_that
from qmra.risk_assessment.models import DefaultPathogens, DefaultPathogenModel, DefaultSources, DefaultSourceModel, \
    DefaultTreatmentModel, DefaultTreatments, PathogenGroup, DefaultExposures, DefaultExposureModel


class TestDefaultPathogens(TestCase):
    expected_length = 37
    def test_properties(self):
        under_test = DefaultPathogens

        assert_that(under_test.raw_data).is_instance_of(dict)
        assert_that(len(under_test.raw_data)).is_equal_to(self.expected_length)

        assert_that(under_test.data).is_instance_of(dict)
        assert_that(under_test.data[list(under_test.data.keys())[0]]).is_instance_of(DefaultPathogenModel)
        assert_that(len(under_test.data)).is_equal_to(self.expected_length)

    def test_get(self):
        under_test = DefaultPathogens

        rotavirus = under_test.get("Rotavirus")
        assert_that(rotavirus).is_instance_of(DefaultPathogenModel)
        assert_that(rotavirus.name).is_equal_to("Rotavirus")
        assert_that(rotavirus.group).is_equal_to(PathogenGroup.Viruses)

        jejuni = under_test.get("Campylobacter jejuni")
        assert_that(jejuni).is_instance_of(DefaultPathogenModel)
        assert_that(jejuni.name).is_equal_to("Campylobacter jejuni")
        assert_that(jejuni.group).is_equal_to(PathogenGroup.Bacteria)

        parvum = under_test.get("Cryptosporidium parvum")
        assert_that(parvum).is_instance_of(DefaultPathogenModel)
        assert_that(parvum.name).is_equal_to("Cryptosporidium parvum")
        assert_that(parvum.group).is_equal_to(PathogenGroup.Protozoa)

    def test_choices(self):
        under_test = DefaultPathogens

        choices = under_test.choices()
        # print(choices)
        assert_that(choices).is_instance_of(list)
        # assert_that(len(choices)).is_equal_to(self.expected_length+2)  # other, blank
        assert_that(choices[0]).is_instance_of(tuple)
        assert_that(choices[0][0]).is_instance_of(str)
        assert_that(choices[0][1]).is_instance_of(str)


class TestDefaultSources(TestCase):
    expected_length = 8

    def test_properties(self):
        under_test = DefaultSources

        assert_that(under_test.raw_data).is_instance_of(dict)
        assert_that(len(under_test.raw_data)).is_equal_to(self.expected_length)

        assert_that(under_test.data).is_instance_of(dict)
        assert_that(under_test.data[list(under_test.data.keys())[0]]).is_instance_of(DefaultSourceModel)
        assert_that(len(under_test.data)).is_equal_to(self.expected_length)

    def test_choices(self):
        under_test = DefaultSources

        choices = under_test.choices()
        # print(choices)
        assert_that(choices).is_instance_of(list)
        # assert_that(len(choices)).is_equal_to(self.expected_length+2)  # other, blank
        assert_that(choices[0]).is_instance_of(tuple)
        assert_that(choices[0][0]).is_instance_of(str)
        assert_that(choices[0][1]).is_instance_of(str)


class TestDefaultTreatments(TestCase):
    expected_length = 28

    def test_properties(self):
        under_test = DefaultTreatments

        assert_that(under_test.raw_data).is_instance_of(dict)
        assert_that(len(under_test.raw_data)).is_equal_to(self.expected_length)

        assert_that(under_test.data).is_instance_of(dict)
        assert_that(under_test.data[list(under_test.data.keys())[0]]).is_instance_of(DefaultTreatmentModel)
        assert_that(len(under_test.data)).is_equal_to(self.expected_length)

    def test_choices(self):
        under_test = DefaultTreatments

        choices = under_test.choices()
        # print(choices)
        assert_that(choices).is_instance_of(list)
        # assert_that(len(choices)).is_equal_to(self.expected_length+2)  # other, blank
        assert_that(choices[0]).is_instance_of(tuple)
        assert_that(choices[0][0]).is_instance_of(str)
        assert_that(choices[0][1]).is_instance_of(str)


class TestDefaultExposures(TestCase):
    expected_length = 8

    def test_properties(self):
        under_test = DefaultExposures

        assert_that(under_test.raw_data).is_instance_of(dict)
        assert_that(len(under_test.raw_data)).is_equal_to(self.expected_length)

        assert_that(under_test.data).is_instance_of(dict)
        assert_that(under_test.data[list(under_test.data.keys())[0]]).is_instance_of(DefaultExposureModel)
        assert_that(len(under_test.data)).is_equal_to(self.expected_length)

    def test_choices(self):
        under_test = DefaultExposures

        choices = under_test.choices()
        # print(choices)
        assert_that(choices).is_instance_of(list)
        # assert_that(len(choices)).is_equal_to(self.expected_length+2)  # other, blank
        assert_that(choices[0]).is_instance_of(tuple)
        assert_that(choices[0][0]).is_instance_of(str)
        assert_that(choices[0][1]).is_instance_of(str)