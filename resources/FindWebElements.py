from collections import Counter
import time
import yaml
import re
import Levenshtein
from difflib import SequenceMatcher
from collections import Counter
from math import sqrt
from robot.libraries.BuiltIn import BuiltIn
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from AutomIAlib import AutomIAlib
from pathlib import Path

class FindWebElements:
    
    # Path to the attributes weight definition file
    attributes_weight_file_path = Path(__file__).parent / "attributesWeight.properties"
    seleniumInstanceName = "SeleniumLibrary"

    def __init__(self) -> None:
        self.AutomIAlib = AutomIAlib()
        config = yaml.safe_load(open(Path(__file__).parent / "settings.yaml"))
        self.seleniumInstanceName = config["SeleniumLibraryInstanceName"]
        self.SimilarityCoeffcientMin = config["SimilarityCoeffcientMin"]


    def filter_elements_by_tag_name_by_driver(self, tag_name:str) -> any:
        """
        Filter elements by tag name using Selenium WebDriver.

        Args:
            tag_name (str): tag name of the scanned element JSON file.

        Returns:
            list: A list of DOM elements.
        """
        # Initialize a SeleniumLibrary instance
        selenium_lib = BuiltIn().get_library_instance(self.seleniumInstanceName)
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
            if attr in ['parents', 'siblings', 'tagName']: # special case + tagName is not added to the list, the filter by tag is done separately to create the basic list of eligible elements
                continue
            for key, weight in file_attributes:
                if attr == key:
                    in_attributes_weight_file = True
                    print("Attibut traité : " + attr)
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
        selenium_lib = BuiltIn().get_library_instance(self.seleniumInstanceName)
        # Get the tagName of the element to retrieve in the DOM
        tag_name = scanned_element_json.get("tagName")
        # Get all the DOM elements possible for the element to find
        starting_list = self.filter_elements_by_tag_name_by_driver(tag_name)
        print("Nombre d'élement avec le TagName : " + tag_name + " = " + str(len(starting_list)))
        # Get all the attribute and their value to begin the search
        sorted_tag_list = self.get_element_attributes(scanned_element_json)
        print("Sorted Tag List : " + str(sorted_tag_list))
        # The most accurate list of possible element found by the attributes search
        current_cached_list = starting_list

        for attribute_name, value, _ in sorted_tag_list:
            # The list of possible elements found by the current attribute
            filtered_elements = []

            if attribute_name == "textContent":
                # Search the Element contains the desired text
                if "'" in value:    # avoid mixing single and double quotes in Xpath
                    xpathContains = f'self::node()[contains(text(), "{value}")]'               
                else: 
                    xpathContains = f"self::node()[contains(text(), '{value}')]"
                filtered_elements = [element for element in current_cached_list if element.find_elements(By.XPATH, xpathContains)]
                # Search the Element with strict content text
                if len(filtered_elements) > 1:
                    if "'" in value:    # avoid mixing single and double quotes in Xpath
                        xpathStrict = f'self::node()[text()="{value}"]'              
                    else: 
                        xpathStrict = f"self::node()[text()='{value}']"                    
                    strict_filtered_elements = [element for element in filtered_elements if element.find_elements(By.XPATH, xpathStrict)]
                    if (len(strict_filtered_elements) > 0) and (len(strict_filtered_elements) < len(filtered_elements)):
                        filtered_elements = strict_filtered_elements
                # Search the Element with regEx on content text
                if len(filtered_elements) == 0:
                    # If no element found, try to search using regex
                    if self.is_a_regex(value):
                        pattern = re.compile(value)
                        # Checks each element in current_cached_list to see if it matches the regex
                        for element in current_cached_list:
                            visible_text = element.text
                            if pattern.search(visible_text):
                                # Add the element to the filtered list
                                filtered_elements.append(element)
                # Search the Element with similarity on content text
                if len(filtered_elements) != 1:
                    # get the good list of element between filtered_elements and current_cached_list
                    if len(filtered_elements) > 1:
                        list_we_search_for = filtered_elements
                    else:
                        list_we_search_for = current_cached_list
                    similarity_old = 0
                    # evaluate the similarity between the text element and the value in reference
                    for element in list_we_search_for:
                        visible_text = element.text
                        similarity = similarity_coefficient(visible_text, value)
                        # insert the element in the list if similarity > at the SimilarityCoeffcientMin parameter in settings.yaml
                        if similarity > self.SimilarityCoeffcientMin:
                            # the element with the maximun similarity in the first place of the list
                            if similarity > similarity_old:
                                similarity_old = similarity
                                filtered_elements.insert(0, element)
                            else:
                                filtered_elements.append(element)

            else:    # self:: --> forces the search to be carried out on the element itself
                if "'" in value:    # avoid mixing single and double quotes in Xpath
                    xpath = f'self::*[@{attribute_name}="{value}"]'                
                else: 
                    xpath = f"self::*[@{attribute_name}='{value}']"
                filtered_elements = [element for element in current_cached_list if element.find_elements(By.XPATH, xpath)]     # alternative : if element.get_attribute(attribute_name) == value
                print("Nombre d'élement avec le Xpath : " + xpath + " = " + str(len(filtered_elements)))

            # Determines whether you have found the item you are looking for or whether you need to continue
            if len(filtered_elements) == 1: # Element found
                current_cached_list = filtered_elements    
                break
            elif len(filtered_elements) > 1: # Multiple elements found
                if len(filtered_elements) < len(current_cached_list):
                    current_cached_list = filtered_elements
                else:
                    filtered_elements = current_cached_list

        return current_cached_list


    # Function to make the element blink
    def blink_element(self, element, duration=4, interval=0.3):
        selenium_lib = BuiltIn().get_library_instance(self.seleniumInstanceName)
        
        # Scroll to bring the element into view
        selenium_lib.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", element)
        time.sleep(0.5)  # Pause to ensure the scroll is complete
        
        # Retrieve the original background color of the element
        original_bg_color = selenium_lib.driver.execute_script("return arguments[0].style.backgroundColor;", element)
        
        end_time = time.time() + duration
        while time.time() < end_time:
            # Change the background color to blue
            selenium_lib.driver.execute_script("arguments[0].style.backgroundColor = 'blue'", element)
            time.sleep(interval)
            
            # Revert to the original background color
            selenium_lib.driver.execute_script(f"arguments[0].style.backgroundColor = '{original_bg_color}'", element)
            time.sleep(interval)
        
        # Ensure the original background color is restored after blinking
        selenium_lib.driver.execute_script(f"arguments[0].style.backgroundColor = '{original_bg_color}'", element)



    def find_most_frequent_element_by_siblings(self, json_sibling_properties):
        """
        Finds the web element with the most sibling matches based on JSON properties.

        Arguments:
        - driver: Instance of Selenium's WebDriver.
        - json_sibling_properties: List of dictionaries containing sibling properties.

        Returns:
        - The WebElement that appears most frequently in the merged lists.
        """

        selenium_lib = BuiltIn().get_library_instance(self.seleniumInstanceName)
        # Initialize the merged list for all found elements
        all_elements = []

        # Iterate through each sibling property group in the JSON
        for sibling_props in json_sibling_properties:
            # Build an XPath based on properties to identify siblings
            xpath = f"{sibling_props['tagName']}[contains(., '{sibling_props['textContent']}')]"
            # Find elements with siblings matching this XPath
            matching_elements = selenium_lib.driver.find_elements(By.XPATH, f"//*[following-sibling::{xpath} or preceding-sibling::{xpath}]")
            # Add the found elements to the merged list
            all_elements.extend(matching_elements)

        # Use Counter to count occurrences of each element
        element_counts = Counter(all_elements)

        # Find the element that appears most frequently in the merged list
        most_frequent_element = element_counts.most_common(1)[0][0] if element_counts else None
        # self.blink_element(most_frequent_element)

        return most_frequent_element


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
        if (len(attributes_way_result) > 1):
            print(f"nombre d'élements encore en lice : {len(attributes_way_result)}")
#            print(f"Elements toujours en lice : {attributes_way_result}")
#            print(f"propriétés des frères de l'élément cherché : {scanned_element_json["siblings"]}")
            return self.find_most_frequent_element_by_siblings(scanned_element_json["siblings"])

        return attributes_way_result


    def is_a_regex(self, pattern):
        """
         Verify if a string is a valid regex.
         Args:
             string to verify.
         Returns:
             True if it's a valid regex, false if not.
         """
        try:
            re.compile(pattern)     # Try compiling the pattern
            return True      # If it passes, it's a valid regex
        except re.error:
            return False     # Error = this is not a valid regex


def similarity_coefficient(s1, s2):
    # Calculating the similarity coefficient with SequenceMatcher
    seq_match_coeff = SequenceMatcher(None, s1, s2).ratio()
    print(f"With Sequence Matcher, similarity coefficient is : {seq_match_coeff}")

    # Calculating the similarity coefficient with Levenshtein
    levenshtein_coeff = Levenshtein.ratio(s1, s2)
    print(f"With Levenshtein, similarity coefficient is : {levenshtein_coeff}")

    # Calculating the similarity coefficient with Jaccard
    set1, set2 = set(s1), set(s2)
    jaccard_coeff = len(set1 & set2) / len(set1 | set2)
    print(f"With Jaccard, similarity coefficient is : {jaccard_coeff}")

    # Calculating the similarity coefficient with Cosine
    vec1, vec2 = Counter(s1), Counter(s2)
    dot_product = sum(vec1[ch] * vec2[ch] for ch in vec1)
    magnitude1 = sqrt(sum(count ** 2 for count in vec1.values()))
    magnitude2 = sqrt(sum(count ** 2 for count in vec2.values()))
    cosine_coeff = dot_product / (magnitude1 * magnitude2)
    print(f"With Cosine, similarity coefficient is : {cosine_coeff}")

    coefficients = [seq_match_coeff, levenshtein_coeff, jaccard_coeff, cosine_coeff]

    # Calculating the similarity coefficient with Hamming (if the strings are the same length)
    if len(s1) == len(s2):
        hamming_coeff = 1 - sum(c1 != c2 for c1, c2 in zip(s1, s2)) / len(s1)
        print(f"With Hamming, similarity coefficient is : {hamming_coeff}")
        coefficients.append(hamming_coeff)
    else:
        print("Hamming similarity cannot be calculated: strings must be of equal length.")

    # average_coefficient = sum(coefficients) / len(coefficients)
    max_coefficient = max(coefficients)

    return max_coefficient