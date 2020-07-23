import unittest
from tagging_converter import TaggingConverter
import tagging


class TestTaggingConverterArbitraryReordering(unittest.TestCase):
    """
        Tests for the tagging converter with arbitrary reordering
        enabled.
    """
    def test_compute_tags_in_order(self):
        """
            Test for when source tokens occur
            in the same relative order
        """
        dummy_phrase_vocabulary = ['and']
        editing_task = tagging.EditingTask([" word1 word2 <::::> word3 "])
        converter = TaggingConverter(dummy_phrase_vocabulary)

        result = [
            str(tag) for tag in converter.compute_tags(
                editing_task, "word1 word2 and word3 ")
        ]

        expected = ['KEEP|0', 'KEEP|1', 'KEEP|and', 'DELETE', 'KEEP|3']

        self.assertEqual(expected, result)

    def test_compute_tags_out_of_order(self):
        """
            Test for when the source tokens
            do not occur in the same relative order
        """
        dummy_phrase_vocabulary = ['and']
        editing_task = tagging.EditingTask([" word1 word2 <::::> word3 "])
        converter = TaggingConverter(dummy_phrase_vocabulary)

        result = [
            str(tag) for tag in converter.compute_tags(
                editing_task, "word2 word1 and word3 ")
        ]

        expected = ['KEEP|1', 'KEEP|0', 'KEEP|and', 'DELETE', 'KEEP|3']

        self.assertEqual(expected, result)

    def test_compute_tags_infeasible(self):
        """
            Test for when the target cannot
            be constructed by the given
            edit vocab and source tokens
        """
        dummy_phrase_vocabulary = ['and']
        editing_task = tagging.EditingTask([" word1 word2 <::::> word3 "])
        converter = TaggingConverter(dummy_phrase_vocabulary)

        result = [
            str(tag) for tag in converter.compute_tags(
                editing_task, "word2 word1 but word3 ")
        ]

        expected = []

        self.assertEqual(expected, result)


if __name__ == '__main__':
    unittest.main()
