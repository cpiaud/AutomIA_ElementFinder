from robot.libraries.BuiltIn import BuiltIn
from bs4 import BeautifulSoup
import json

from selenium.webdriver.common.by import By

from MyLibrary import MyLibrary


class RetrieveDOMElements:

    def __init__(self):
        self.mylibrary = MyLibrary()

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

        # Extract tag name from JSON file
        tag_name = self.mylibrary.read_json_file(json_file_content).get("tagName")

        # Filter elements based on tag name
        filtered_elements = [element for element in dom_elements if element.get("tag_name") == tag_name]

        # Return the filtered elements list
        return filtered_elements

    def extract_values(self, scanned_element_json, attribute_weight):
        sorted_list = self.mylibrary.read_properties_file(attribute_weight)
        json_data = self.mylibrary.read_json_file(scanned_element_json)
        extracted_values = []
        for key, _ in sorted_list:
            if key in json_data:
                extracted_values.append((key, json_data[key]))
        return extracted_values

    def filter_elements_by_attributes(self, scanned_element_json, attribute_weight):
        starting_list = self.filter_elements_by_tag_name(scanned_element_json)
        sorted_tag_list = self.extract_values(scanned_element_json, attribute_weight)
        current_cached_list = starting_list

        filtered_elements = []
        # Filter elements based on tag name
        for attribute_name, value in sorted_tag_list:
            for element in current_cached_list:
                if attribute_name in element['attributes'] and element['attributes'][attribute_name] == value:
                    filtered_elements.append(element)

            if len(filtered_elements) == 1:
                current_cached_list = filtered_elements
                print("Element found")
                break
            elif len(filtered_elements) > 1:
                if filtered_elements < current_cached_list:
                    current_cached_list = filtered_elements
                else:
                    filtered_elements = current_cached_list
                    print("Multiple Elements found")
            else:
                print("No Element found")

        return current_cached_list

    def find_elements_by_IA(self, scanned_element_json_name):
        attribute_weight = "test/resources/selectorWeight.properties"
        scanned_element_path_name = 'test/objectrepository/%s.json' % scanned_element_json_name
        unique_element = self.filter_elements_by_attributes(scanned_element_path_name, attribute_weight)
        print(self.build_xpath(unique_element[0]))

        return self.build_xpath(unique_element[0])

    @staticmethod
    def build_xpath(element_dict):
        tag_name = element_dict['tag_name']
        attributes = element_dict['attributes']
        text_value = element_dict['text']

        xpath = f"//{tag_name}"

        # Generate attribute strings with 'and' between them
        attribute_strings = []
        for key, value in attributes.items():
            if isinstance(value, list):
                # Convert list to string with single value
                value = value[0]
            attribute_strings.append(f"@{key}='{value}'")
        attribute_string = ' and '.join(attribute_strings)

        # Add attribute string to XPath if it's not empty
        if attribute_string:
            xpath += f"[{attribute_string}]"

        # Add text attribute if it is not empty
        if text_value:
            xpath += f"[text()='{text_value}']"

        # formatted_xpath = 'xpath:' + xpath

        return xpath

# Method 2 of getting web elements and filtering by driver

    def filter_elements_by_attributes_by_driver(self, scanned_element_json, attribute_weight):
        selenium_lib = BuiltIn().get_library_instance('SeleniumLibrary')
        tag_name = self.mylibrary.read_json_file(scanned_element_json).get("tagName")
        starting_list = self.filter_elements_by_tag_name_by_driver(scanned_element_json)
        sorted_tag_list = self.extract_values(scanned_element_json, attribute_weight)
        current_cached_list = starting_list

        filtered_elements = []
        for attribute_name, value in sorted_tag_list:
            xpath = "//" + tag_name + "[@" + attribute_name + "='" + value + "']"

            filtered_elements = selenium_lib.driver.find_elements(By.XPATH, xpath)

            if len(filtered_elements) == 1:
                current_cached_list = filtered_elements
                print("Element found")
                break
            elif len(filtered_elements) > 1:
                if filtered_elements < current_cached_list:
                    current_cached_list = filtered_elements
                else:
                    filtered_elements = current_cached_list
                    print("Multiple Elements found")
            else:
                print("No Element found")

        return current_cached_list

    def filter_elements_by_tag_name_by_driver(self, json_scanned_element_content):
        selenium_lib = BuiltIn().get_library_instance('SeleniumLibrary')

        # Extract tag name from JSON file
        tag_name = self.mylibrary.read_json_file(json_scanned_element_content).get("tagName")
        script = f"return document.getElementsByTagName('{tag_name}')"
        dom_elements = selenium_lib.driver.execute_script(script)
        return dom_elements

    def find_elements_by_ia_with_driver(self, scanned_element_json_name):
        attribute_weight = "test/resources/selectorWeight.properties"
        scanned_element_path_name = 'test/objectrepository/%s.json' % scanned_element_json_name
        unique_element = self.filter_elements_by_attributes_by_driver(scanned_element_path_name, attribute_weight)
        return unique_element