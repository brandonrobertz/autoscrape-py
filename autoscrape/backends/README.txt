class Scraper():
    required:
      def get_clickable(self, type=None):
      def fetch(self, url):
      def click(self, tag, iterating_form=False):
      def back(self):
      def download_page(self, url):
      def page_html(self):
      def page_url(self):
      def element_text(self, element=None):
      def lookup_by_tag(self, tag):

    form-capable:
      def get_forms(self):
      def get_buttons(self):
      def input(self, tag, input):
      def input_select_option(self, tag, option_str):
      def input_checkbox(self, tag, to_check):
      def submit(self, tag):

    interactive:
      def elem_stats(self, elem):
      def expand_key_substitutions(self, input):
      def disable_target(self, elem):
      def scrolltoview(self, elem):
      def click_at_position_over_element(self, elem):

    selenium housekeeping:
      def __del__(self):
      def __init__(self, driver="Firefox", leave_host=False, load_images=False)
      def _driver_exec(self, fn, *args, **kwargs):
      def _wait_check(self, driver):
      def _loadwait(self, fn, *args, **kwargs):

Actions:
    fetch(url)
    click(clickable_index)
    back()

State (embedding lists of each):
    get_clickable()
    get_forms()
    get_buttons()

