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

