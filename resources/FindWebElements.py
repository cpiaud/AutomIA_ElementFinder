from robot.libraries.BuiltIn import BuiltIn
from bs4 import BeautifulSoup
import json
import os

from selenium.webdriver.common.by import By

from AutomIAlib import AutomIAlib


class FindWebElements:

    def __init__(self):
        self.AutomIAlib = AutomIAlib()

    @staticmethod
    def get_current_url():
        """
        Return the current URL of the browser.

        Returns:
            str: The current URL of the browser.
        """
        # Retrieve the SeleniumLibrary instance from Robot Framework
        selenium_lib = BuiltIn().get_library_instance('SeleniumLibrary')

        # Get the current URL from the Selenium WebDriver
        url = selenium_lib.driver.current_url
        print(f"The current url is: {url}")
        return url

    @staticmethod
    def get_elements_from_url():
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

    def filter_elements_by_tag_name(self, json_file_content):
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

    def extract_values(self, scanned_element_json, attribute_weight):
        """
        Extract values from JSON based on attribute weights.

        Args:
            scanned_element_json (str): Path to the scanned element JSON file.
            attribute_weight (str): Path to the attribute weight properties file.

        Returns:
            list: A list of tuples containing attribute and its value.
        """
        # Read the attribute weight properties file
        sorted_list = self.AutomIAlib.read_properties_file(attribute_weight)

        # Read the scanned element JSON file
        json_data = self.AutomIAlib.read_json_file(scanned_element_json)

        # Extract values based on the sorted attribute list
        extracted_values = []
        for key, _ in sorted_list:
            if key in json_data:
                extracted_values.append((key, json_data[key]))

        return extracted_values

    def filter_elements_by_attributes(self, scanned_element_json, attribute_weight):
        """
        Filter elements by attributes using weights.

        Args:
            scanned_element_json (str): Path to the scanned element JSON file.
            attribute_weight (str): Path to the attribute weight properties file.

        Returns:
            list: A list of filtered elements.
        """
        # Get the initial list of elements filtered by tag name
        starting_list = self.filter_elements_by_tag_name(scanned_element_json)

        # Extract attribute values sorted by weight
        sorted_tag_list = self.extract_values(scanned_element_json, attribute_weight)
        
        current_cached_list = starting_list
        filtered_elements = []

        # Filter elements based on tag name
        for attribute_name, value in sorted_tag_list:
            # Iterate through the current list of cached elements
            for element in current_cached_list:
                 # Check if the current element has the current attribute and if the attribute value matches
                if attribute_name in element['attributes'] and element['attributes'][attribute_name] == value:
                    # If the attribute matches, add the element to the filtered elements list
                    filtered_elements.append(element)

            # If only one element is found after filtering by the current tag name
            if len(filtered_elements) == 1:
                # Update the current cached list to only contain this unique element
                current_cached_list = filtered_elements
                print("Element found")
                break # Exit the loop early since a unique element is found
            elif len(filtered_elements) > 1:
                # If multiple elements are found, check if the filtered list is smaller than the current cached list
                if len(filtered_elements) < len(current_cached_list):
                     # Update the current cached list to the new filtered list
                    current_cached_list = filtered_elements
                else:
                    # If the new filtered list is not smaller, retain the current cached list
                    filtered_elements = current_cached_list
                    print("Multiple Elements found")
            else:
                # If no elements are found, print a message indicating no matches
                print("No Element found")

        return current_cached_list

    def find_elements_by_IA(self, scanned_element_json_name):
        """
        Find elements by IA.

        Args:
            scanned_element_json_name (str): Name of the scanned element JSON file.

        Returns:
            str: XPath of the unique element found.
        """

        attribute_weight = "resources/selectorWeight.properties"
        scanned_element_path_name = f'{scanned_element_json_name}.json'
        unique_element = self.filter_elements_by_attributes(scanned_element_path_name, attribute_weight)
        print(self.build_xpath(unique_element[0]))

        return self.build_xpath(unique_element[0])

    @staticmethod
    def build_xpath(element_dict):
        """
        Build XPath from element dictionary.

        Args:
            element_dict (dict): Dictionary containing element information.

        Returns:
            str: XPath of the element.
        """
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
        """
        Filter elements by attributes using Selenium WebDriver.

        Args:
            scanned_element_json (str): Path to the scanned element JSON file.
            attribute_weight (str): Path to the attribute weight properties file.

        Returns:
            list: A list of filtered elements.
        """
        selenium_lib = BuiltIn().get_library_instance('SeleniumLibrary')
        tag_name = self.AutomIAlib.read_json_file(scanned_element_json).get("tagName")
        starting_list = self.filter_elements_by_tag_name_by_driver(scanned_element_json)
        sorted_tag_list = self.extract_values(scanned_element_json, attribute_weight)
        current_cached_list = starting_list

        filtered_elements = []
        for attribute_name, value in sorted_tag_list:
            xpath = f"//{tag_name}[@{attribute_name}='{value}']"

            filtered_elements = selenium_lib.driver.find_elements(By.XPATH, xpath)

            if len(filtered_elements) == 1:
                current_cached_list = filtered_elements
                print("Element found")
                break
            elif len(filtered_elements) > 1:
                if len(filtered_elements) < len(current_cached_list):
                    current_cached_list = filtered_elements
                else:
                    filtered_elements = current_cached_list
                    print("Multiple Elements found")
            else:
                print("No Element found")

        return current_cached_list

    def filter_elements_by_tag_name_by_driver(self, json_scanned_element_content):
        """
        Filter elements by tag name using Selenium WebDriver.

        Args:
            json_scanned_element_content (str): Path to the scanned element JSON file.

        Returns:
            list: A list of DOM elements.
        """
        selenium_lib = BuiltIn().get_library_instance('SeleniumLibrary')

        # Extract tag name from JSON file
        tag_name = self.AutomIAlib.read_json_file(json_scanned_element_content).get("tagName")
        script = f"return document.getElementsByTagName('{tag_name}')"
        dom_elements = selenium_lib.driver.execute_script(script)
        return dom_elements

    def find_elements_by_ia_with_driver(self, scanned_element_json_name):
        """
        Find elements by IA using Selenium WebDriver.

        Args:
            scanned_element_json_name (str): Name of the scanned element JSON file.

        Returns:
            list: A list of unique elements found.
        """
        attribute_weight = "resources/selectorWeight.properties"
        scanned_element_path_name = f'{scanned_element_json_name}.json'
        unique_element = self.filter_elements_by_attributes_by_driver(scanned_element_path_name, attribute_weight)
        return unique_element