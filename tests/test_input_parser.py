import unittest

from autoscrape.input_parser import InputParser


class TestInputParser(unittest.TestCase):
    def test_normal_string_parsing(self):
        inp_str = "i:0:string%,c:1:True,s:2:France"
        inputs_gen = InputParser(inp_str).generate()
        inputs = list(inputs_gen)
        self.assertEqual(len(inputs), 1)
        first_search = inputs[0]
        self.assertEqual(len(first_search), 3)

    def test_normal_string_multi_search_parsing(self):
        inp_str = "i:0:string1%,s:2:France;i:0:string2%,s:2:Russia"
        inputs_gen = InputParser(inp_str).generate()
        inputs = list(inputs_gen)
        self.assertEqual(len(inputs), 2)
        search = inputs[0]
        self.assertEqual(len(search), 2)
        self.assertEqual(search[0]["string"], "string1%")
        self.assertEqual(search[0]["type"], "input")
        self.assertEqual(search[0]["index"], 0)
        self.assertEqual(search[1]["string"], "France")
        self.assertEqual(search[1]["type"], "select")
        self.assertEqual(search[1]["index"], 2)
        search = inputs[1]
        self.assertEqual(len(search), 2)
        self.assertEqual(search[0]["string"], "string2%")
        self.assertEqual(search[0]["type"], "input")
        self.assertEqual(search[0]["index"], 0)
        self.assertEqual(search[1]["string"], "Russia")
        self.assertEqual(search[1]["type"], "select")
        self.assertEqual(search[1]["index"], 2)


if __name__ == "__main__":
    unittest.main()
