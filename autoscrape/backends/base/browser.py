# -*- coding: UTF-8 -*-
from autoscrape.backends.base.tags import TaggerBase


class BrowserBase(TaggerBase):
    def _no_tags(self, data, l_type="path"):
        clean = []
        if type(data) == tuple:
            data = list(data)
        for p in data:
            name, t_args, kwargs = p
            args = list(t_args)
            if name == "click":
                if not args:
                    continue
                args[0] = "[tag]"
            clean.append((name, args, kwargs))
        return clean

    def click(self, tag, **kwargs):
        self.path.append((
            "click", [tag], {"url": url}
        ))
        node = "Click\n text: %s\n hash: %s" % (text, hash)
        node_meta = {
            "click": tag,
            "click_text": text,
            "click_iterating_form": None,
        }
        self.graph.add_node(
            node,
            **node_meta
        )
        self.graph.move_to_node(node)

    def fetch(self, url, initial=False):
        self.graph.add_root_node(node, url=url, action="fetch")

    def back(self):
        self.graph.move_to_parent()

    def input(self, tag, input):
        self.path.append(("input", ("", input,), {}))
        action = {
            "action": "input",
            "text": input,
            "tag": tag,
        }
        self.graph.add_action_to_current(action)

    def submit(self, tag, add_node=True):
        self.path.append(("submit", (tag,), {}))
        node = "Submit\n tag: %s" % (tag)
        node_meta = {
            "submit": tag,
        }
        self.graph.add_node(node, **node_meta)
        self.graph.move_to_node(node)
