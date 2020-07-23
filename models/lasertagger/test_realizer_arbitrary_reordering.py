import unittest
import tagging


class TestRealizerArbitraryReordering(unittest.TestCase):
    """
        Tests for the realizer with arbitrary reordering
        enabled.
    """
    def test_realize_output_in_order(self):
        """
            Test for when source tokens occur
            in the same relative order in the 
            target string
        """
        editing_task = tagging.EditingTask(["word1 word2 <::::> word3 "])

        tags_str = ['KEEP|0', 'KEEP|1', 'KEEP|and', 'DELETE', 'KEEP|3']
        tags = [tagging.Tag(tag) for tag in tags_str]

        result = editing_task.realize_output([tags])

        expected = "word1 word2 and word3 "

        self.assertEqual(expected, result)

    def test_realize_output_out_of_order(self):
        """
            Test for when the source tokens
            do not occur in the same relative order
            in the target string
        """
        editing_task = tagging.EditingTask(["word1 word2 <::::> word3 "])

        tags_str = ['KEEP|1', 'KEEP|0', 'KEEP|and', 'DELETE', 'KEEP|3']
        tags = [tagging.Tag(tag) for tag in tags_str]

        result = editing_task.realize_output([tags])

        expected = "word2 word1 and word3 "

        self.assertEqual(expected, result)


if __name__ == '__main__':
    unittest.main()
