from bs4 import BeautifulSoup
from robot.libraries.BuiltIn import BuiltIn

from selenium.webdriver.common.by import By

from AutomIAlib import AutomIAlib

class FindWebElements:
    
    # Path to the attributes weight definition file
    attributes_weight_file_path = "resources/attributesWeight.properties"

    def __init__(self) -> None:
        self.AutomIAlib = AutomIAlib()

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

    def get_element_attributes(self, scanned_element_json:any) -> list[any]:
        """
        Get all the attributes and their weight of the scanned_element_json.
        if one of the found attribute has no weight define in the attributes_weight file, is default weight will be 10

        Args:
            scanned_element_json (json): scanned element JSON data.
        
        Returns:
            list[(key, value, weight)]: A list of tuples containing this attribute key is value and is weight.
        """
        # Read the attribute weight properties file
        file_attributes = self.AutomIAlib.read_properties_file(self.attributes_weight_file_path)
        # Extract values based on the sorted attribute list
        attributes = []

        for attr in scanned_element_json:
            in_attributes_weight_file = False

            if attr in ['parents', 'siblings']: # special case
                continue
            for key, weight in file_attributes:
                if attr == key:
                    in_attributes_weight_file = True
                    attributes.append((attr, scanned_element_json[attr], weight))
                    break
            if not in_attributes_weight_file:
                attributes.append((attr, scanned_element_json[attr], 10))

        return sorted(attributes, key=lambda elm: elm[2], reverse=True) # sort the attributes by decreasing weight order

    def get_by_attributes(self, scanned_element_json:any) -> list[any]:
        """
        Get all corresponding elements with the attributes of the scanned element.

        Args:
            scanned_element_json (json): scanned element JSON data.

        Returns:
            list: A list of filtered elements.
        """
        # Initialize a SeleniumLibrary instance
        selenium_lib = BuiltIn().get_library_instance('SeleniumLibrary')
        # Get the tagName of the element to retrieve in the DOM
        tag_name = scanned_element_json.get("tagName")
        # Get all the DOM elements possible for the element to find
        starting_list = self.filter_elements_by_tag_name_by_driver(tag_name)
        # Get all the attribute and their value to begin the search
        sorted_tag_list = self.get_element_attributes(scanned_element_json)
        # The most accurate list of possible element found by the attributes search
        current_cached_list = starting_list
        # The list of possible elements found by the current attribute
        filtered_elements = []

        for attribute_name, value, _ in sorted_tag_list:
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

        return current_cached_list

    def check_by_siblings(self, siblings, soup) -> list[any]:
        is_one_child_found = False
        childrens = []
        res = []

        for sc in soup.children:
            if sc != "\n":
                childrens.append(sc)
                res.append(sc)

        for c in childrens:
            for s in siblings:
                same_element = True
                for attr in s.keys():
                    match attr:
                        case 'tagName':
                            same_element = c.name.__eq__(s[attr])
                        case 'textContent':
                            same_element = c.get_text().strip().__eq__(s[attr])
                        case _:
                            same_element = c[attr][0].strip().__eq__(s[attr])
                    if not same_element:
                        break
                if same_element:
                    is_one_child_found = True
                    res.remove(c)
                    continue
        return res if is_one_child_found else []

    def get_to_parent(self, parents, siblings, soup, a) -> list[any]:
        find_elements = []

        if not parents:
            e = self.check_by_siblings(siblings, soup)
            for el in e:
                find_elements.append(el)
        else:
            for elm in soup.find_all(parents[len(parents) - 1]["tagName"]):
                if (len(parents) - 1 >= 0):
                    e = self.get_to_parent(parents[:-1], siblings, elm, a - 1)
                    if e:
                        find_elements.extend(e)

        return find_elements if find_elements else None

    def get_by_siblings_and_parents(self, scanned_element_json:any) -> any:
        """
        Get all corresponding elements with the parents and siblings of the scanned element.

        Args:
            scanned_element_json (json): scanned element JSON data.

        Returns:
            list: A list of the plausible corresponding elements.
        """
        # Initialize a SeleniumLibrary instance
        selenium_lib = BuiltIn().get_library_instance('SeleniumLibrary')
        soup = BeautifulSoup(selenium_lib.driver.page_source, 'html.parser')

        soupElms = self.get_to_parent(scanned_element_json["parents"][:-1], scanned_element_json["siblings"], soup, len(scanned_element_json["parents"]) - 1)
        BuiltIn().log_to_console(soupElms)
        # TODO Add the retrieving method from soup element to web element
        exit(0)
        return

    
    def find_elements_by_ia_with_driver(self, scanned_element_json_name:str) -> any:
        """
        Find elements by IA using Selenium WebDriver.

        Args:
            scanned_element_json_name (str): Name of the scanned element JSON file.

        Returns:
            list: A list of unique elements found.
        """
        # Get the data of the element json file
        scanned_element_json = self.AutomIAlib.read_json_file(f'{scanned_element_json_name}.json')
        attributes_way_result = self.get_by_attributes(scanned_element_json)
        
        # TODO reinforce the error handling
        if (True): # len(attributes_way_result) != 1
            return self.get_by_siblings_and_parents(scanned_element_json)
        return attributes_way_result
    
def create_element_xpath(self, element:any) -> str:
        """
        Create the xpath of an element using all of his attributes

        Args:
            element (json): all the attribute and value that compose the element

        Returns:
            str: the xpath of the element.
        """
        xpath = f"//{element['tagName']}["
        is_starting_attribute = True

        for attr in element:
            match attr:
                case 'tagName':
                    continue
                case 'textContent':
                    if not is_starting_attribute:
                        xpath += f" and contains(., '{element[attr]}')"
                    else:
                        xpath += f"contains(., '{element[attr]}')"
                case _:
                    if not is_starting_attribute:
                        xpath += f" and @{attr}='{element[attr]}'"
                    else:
                        xpath += f"@{attr}='{element[attr]}'"
            is_starting_attribute = False
        return xpath + "]"


    # def create_element_xpath(self, element:any) -> str:
    #     """
    #     Create the xpath of an element using all of his attributes

    #     Args:
    #         element (json): all the attribute and value that compose the element

    #     Returns:
    #         str: the xpath of the element.
    #     """
    #     xpath = f"//{element['tagName']}["
    #     is_starting_attribute = True

    #     for attr in element:
    #         match attr:
    #             case 'tagName':
    #                 continue
    #             case 'textContent':
    #                 if not is_starting_attribute:
    #                     xpath += f" and contains(., '{element[attr]}')"
    #                 else:
    #                     xpath += f"contains(., '{element[attr]}')"
    #             case _:
    #                 if not is_starting_attribute:
    #                     xpath += f" and @{attr}='{element[attr]}'"
    #                 else:
    #                     xpath += f"@{attr}='{element[attr]}'"
    #         is_starting_attribute = False
    #     return xpath + "]"

    # def get_by_siblings_and_parents(self, scanned_element_json:any) -> any:
    #     """
    #     Get all corresponding elements with the parents and siblings of the scanned element.

    #     Args:
    #         scanned_element_json (json): scanned element JSON data.

    #     Returns:
    #         list: A list of the plausible corresponding elements.
    #     """
    #     # Initialize a SeleniumLibrary instance
    #     selenium_lib = BuiltIn().get_library_instance('SeleniumLibrary')
    #     first_parent = scanned_element_json.get('parents')[0]
    #     siblings = scanned_element_json.get('siblings')

    #     parent_childs = selenium_lib.driver.find_elements(By.XPATH, self.create_element_xpath(first_parent) + '/child::*')
    #     res = []
    #     for child in parent_childs:
    #         res.append(child)

    #     BuiltIn().log_to_console(self.create_element_xpath(first_parent) + '/child::*')
    #     BuiltIn().log_to_console(len(parent_childs))
    #     BuiltIn().log_to_console(parent_childs)
    #     for child in parent_childs:
    #         BuiltIn().log_to_console("[===========new element===========]")
    #         BuiltIn().log_to_console("Child : " + child.tag_name)
    #         for sibling in siblings:
    #             same_element = True
    #             BuiltIn().log_to_console("sibling : " + sibling["tagName"])
    #             BuiltIn().log_to_console(sibling.keys())
    #             for attr in sibling.keys():
    #                 BuiltIn().log_to_console(attr)
    #                 BuiltIn().log_to_console('+' + sibling[attr] + '+')
    #                 BuiltIn().log_to_console('+' + child.get_attribute(attr).strip().lower() + '+')
    #                 if sibling[attr] != child.get_attribute(attr).strip().lower():
    #                     same_element = False
    #                     break
    #                 BuiltIn().log_to_console("<--------->")
    #             BuiltIn().log_to_console(same_element)
    #             if same_element:
    #                 BuiltIn().log_to_console("Child remove !")
    #                 res.remove(child)
    #                 break
    #     return res