from robot.libraries.BuiltIn import BuiltIn
from bs4 import BeautifulSoup
import json
from MyLibrary import MyLibrary


class RetrieveDOMElements:

    def __init__(self):
        self.read_json = MyLibrary()

    @staticmethod
    def get_current_url():
        """Return the current URL of the browser."""
        # url = self.driver.current_url
        selenium_lib = BuiltIn().get_library_instance('SeleniumLibrary')
        url = selenium_lib.driver.current_url
        print(f"The current url is: {url}")
        return url

    @staticmethod
    def get_elements_from_url():
        # Initialize a WebDriver instance
        selenium_lib = BuiltIn().get_library_instance('SeleniumLibrary')

        # Get the page source HTML
        page_source = selenium_lib.driver.page_source

        # Parse the HTML using BeautifulSoup
        soup = BeautifulSoup(page_source, 'html.parser')

        # Find all elements in the HTML
        elements = soup.find_all()

        # Convert elements to JSON format
        elements_json = []
        for element in elements:
            element_json = {
                'tag_name': element.name,
                'attributes': dict(element.attrs),
                'text': element.text.strip()
            }
            elements_json.append(element_json)

        # Serialize the list of dictionaries to JSON format
        return json.dumps(elements_json)

    def filter_elements_by_tag_name(self, json_file_content):
        dom_elements = json.loads(self.get_elements_from_url())
        # Load JSON file content
        # json_data = self.read_json.read_json_file(json_file_content)

        # Extract tag name from JSON file
        tag_name = self.read_json.read_json_file(json_file_content).get("tagName")
        print(f"json file tag name: {tag_name}")
        # Filter elements based on tag name
        filtered_elements = [element for element in dom_elements if element.get("tag_name") == tag_name]

        # Return the filtered elements list
        return filtered_elements
