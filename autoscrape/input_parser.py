import re

import exrex


class InputParser:
    def __init__(self, input):
        self.input = input

    def str2bool(self, string):
        if not string:
            return False
        if string.lower() in ["false", "no", "n", "0"]:
            return False
        return True

    def character_iteration_input_generator(self, length=1):
        chars = string.ascii_lowercase
        if self.form_input_range:
            chars = self.form_input_range

        for input in product(chars, repeat=length):

            inp = "".join(input)
            if self.wildcard:
                inp += self.wildcard

            yield [{
                "index": self.form_input_index,
                "string": inp,
            }]

    def generate(self):
        """
        Make a form input generator by parsing our input string. Output
        is a multidimensional array, where the first dimension is
        independent searches to attempt and the second dimension is
        which inputs for fill. Example:

        From this input string:

          "i:0:[a-z]%,c:1:True,s:2:France"

        We get the following output generator:

            [
              [
                { "index": 0, "string": "a%", "type": "input" }
                { "index": 1, "select": True, "type": "checkbox" }
                { "index": 2, "string": "France", "type": "select" }
              ],
              ...,
              [
                { "index": 0, "string": "z%", "type": "input" },
                { "index": 1, "select": True, "type": "checkbox" }
                { "index": 2, "string": "France", "type": "select" }
              ]
            ]

        This will do all searches with input 0 filled with a-z and the
        remaining specified inputs filled as desired (input 1, a checkbox,
        checked and input 2, a choice select, selected to the "France"
        option).
        """
        # split the independent searches first
        inputs = re.split(r'(?<!\\);', self.input)
        for inp in inputs:
            indiv_search = []
            # split the inputs to be filled per search
            indiv_inputs_list = re.split(r'(?<!\\),', inp)
            for indiv_inputs in indiv_inputs_list:
                # input type, input index, action
                itype, ix, action = indiv_inputs.split(":", 2)
                action = action.replace("\,", ",").replace("\;", ";")
                # action_gen = list(exrex.generate(action))
                ix = int(ix)
                if itype == "i":
                    indiv_search.append({
                        "index": ix,
                        "type": "input",
                        "string": action,
                    })
                elif itype == "s":
                    indiv_search.append({
                        "index": ix,
                        "type": "select",
                        "string": action,
                    })
                elif itype == "c":
                    indiv_search.append({
                        "index": ix,
                        "type": "checkbox",
                        "action": self.str2bool(action),
                    })
                else:
                    raise Exception("Invalid input type found: %s" % itype)

            yield indiv_search

        # # now, since the "action" on some of the individual searches above
        # # can have regex, we need to unroll them, one-by-one, and expand
        # # the regex into a generator yielding all specified searches
        # expanded = []
        # for search in searches:
        #     print("search", search)
        #     indiv_search = []
        #     for ix in range(len(search)):
        #         this = search[ix]
        #         # don't do anything special for checkboxes, it's boolean
        #         if this["type"] == "checkbox":
        #             indiv_search.append(this)
        #             continue
        #         for string in exrex.generate(this["string"]):
        #             indiv_search.append({
        #                 "index": this["index"],
        #                 "type": this["type"],
        #                 "string": string
        #             })
        #             self.append_rest(ix, search)
        #         print("indiv_input", indiv_input)
        # return expanded

