from robot.libraries.BuiltIn import BuiltIn
from bs4 import BeautifulSoup
import json

from selenium.webdriver.common.by import By

from AutomIAlib import AutomIAlib


class FindWebElements:

    def __init__(self) -> None:
        self.AutomIAlib = AutomIAlib()

    @staticmethod
    def get_elements_from_url() -> list[any]:
        """
        Retrieve all DOM elements from the current page.

        Returns:
            str: A JSON string representation of all DOM elements.
        """
        # Initialize a SeleniumLibrary instance
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

    def filter_elements_by_tag_name(self, json_file_content:str) -> list[any]:
        """
        Filter elements by tag name specified in the JSON file.

        Args:
            json_file_content (str): Path to the JSON file containing the tag name.

        Returns:
            list: A list of filtered elements.
        """
        # Get all DOM elements from the current page
        dom_elements = json.loads(self.get_elements_from_url())

        # Extract tag name from JSON file
        tag_name = self.AutomIAlib.read_json_file(json_file_content).get("tagName")

        # Filter elements based on tag name
        filtered_elements = [element for element in dom_elements if element.get("tag_name") == tag_name]

        # Return the filtered elements list
        return filtered_elements

    def extract_values(self, scanned_element_json:any, attribute_weight_file_path:str) -> any:
        """
        Extract values from JSON based on attribute weights.

        Args:
            scanned_element_json (any): scanned element JSON data.
            attribute_weight_file_path (str): Path to the attribute weight properties file.

        Returns:
            list: A list of tuples containing attribute and its value.
        """
        # Read the attribute weight properties file
        sorted_list = self.AutomIAlib.read_properties_file(attribute_weight_file_path)

        # Extract values based on the sorted attribute list
        extracted_values = []
        for key, _ in sorted_list:
            if key in scanned_element_json:
                extracted_values.append((key, scanned_element_json[key]))

        return extracted_values

    def filter_elements_by_attributes_by_driver(self, scanned_element_path:str, attribute_weight_file_path:str) -> any:
        """
        Filter elements by attributes using Selenium WebDriver.

        Args:
            scanned_element_path (str): Path to the scanned element JSON file.
            attribute_weight_file_path (str): Path to the attribute weight properties file.

        Returns:
            list: A list of filtered elements.
        """
        # Initialize a SeleniumLibrary instance
        selenium_lib = BuiltIn().get_library_instance('SeleniumLibrary')

        # Get the data of the element json file
        scanned_element_json = self.AutomIAlib.read_json_file(scanned_element_path)
        
        # Get the tagName of the element to retrieve in the DOM
        tag_name = scanned_element_json.get("tagName")
        
        # Get all the DOM elements possible for the element to find
        starting_list = self.filter_elements_by_tag_name_by_driver(tag_name)
        
        # Get all the attribute and their value to begin the search
        sorted_tag_list = self.extract_values(scanned_element_json, attribute_weight_file_path)
        
        # The most accurate list of possible element found by the attributes search
        current_cached_list = starting_list
        
        # The list of possible elements found by the current attribute
        filtered_elements = []

        for attribute_name, value in sorted_tag_list:
            if attribute_name == "textContent":
                xpath = f"//{tag_name}[contains(., '{value}')]"
            else:
                xpath = f"//{tag_name}[@{attribute_name}='{value}']"

            filtered_elements = selenium_lib.driver.find_elements(By.XPATH, xpath)

            if len(filtered_elements) == 1: # Element found
                current_cached_list = filtered_elements
                break
            elif len(filtered_elements) > 1: # Multiple elements found
                if len(filtered_elements) < len(current_cached_list):
                    current_cached_list = filtered_elements
                else:
                    filtered_elements = current_cached_list

            # TODO no elements or mutiple elements error handling missing

        return current_cached_list

    def filter_elements_by_tag_name_by_driver(self, tag_name:str) -> any:
        """
        Filter elements by tag name using Selenium WebDriver.

        Args:
            tag_name (str): tag name of the scanned element JSON file.

        Returns:
            list: A list of DOM elements.
        """
        # Initialize a SeleniumLibrary instance
        selenium_lib = BuiltIn().get_library_instance('SeleniumLibrary')

        # Get DOM elements by tag name
        script = f"return document.getElementsByTagName('{tag_name}')"
        dom_elements = selenium_lib.driver.execute_script(script)

        return dom_elements
    
    def find_elements_by_ia_with_driver(self, scanned_element_json_name:str) -> any:
        """
        Find elements by IA using Selenium WebDriver.

        Args:
            scanned_element_json_name (str): Name of the scanned element JSON file.

        Returns:
            list: A list of unique elements found.
        """
        # Path to the attributes weight definition file
        attribute_weight_file_path = "resources/selectorWeight.properties"

        # Pathname of the json element file
        scanned_element_path = f'{scanned_element_json_name}.json'

        return self.filter_elements_by_attributes_by_driver(scanned_element_path, attribute_weight_file_path)