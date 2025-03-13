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
        self.continueOnMultipleElement = self.get_boolean_setting(config, "continueOnMultipleElement")
        self.textContentValue = ""
        self.elementIndex = -1

    def get_boolean_setting(self, config, key, default=False):
        """
        Retrieves a boolean setting from the configuration, handling invalid values.

        Args:
            config (dict): The loaded YAML configuration dictionary.
            key (str): The key of the setting to retrieve.
            default (bool): The default value to use if the key is missing or invalid.

        Returns:
            bool: The boolean value of the setting, or the default if invalid.
        """
        value = config.get(key)
        if isinstance(value, bool):
            return value  # Already a boolean, return directly
        elif isinstance(value, str):
            if value.lower() == "true":
                return True
            elif value.lower() == "false":
                return False
            else:
                print(f"Warning: Invalid boolean value '{value}' found for setting '{key}' in settings.yaml. Using default: {default}")
                return default
        elif value is None:
            print(f"Warning: Missing setting '{key}' in settings.yaml. Using default: {default}")
            return default
        else:
            print(f"Warning: Invalid type '{type(value)}' for setting '{key}' in settings.yaml. Using default: {default}")
            return default


    def safe_int_conversion(self, value, default=0):
        """Convert string to integer safely. Returns `default` if conversion fails."""
        try:
            return int(value)
        except (ValueError, TypeError):
            return default
    

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
            if attr == 'elementNumber': # special case, elementNumber is used to select an element when many were found
                elementNumber = self.safe_int_conversion(scanned_element_json[attr])
                # the presence of the elementNumber parameter allows you to continue if there are several elements in the search list
                self.continueOnMultipleElement = True
                if elementNumber == 0 :
                    self.elementIndex = 0
                else:
                    self.elementIndex = elementNumber - 1
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
        current_cached_list = starting_list[:]

        for attribute_name, value, _ in sorted_tag_list:
            # The list of possible elements found by the current attribute
            filtered_elements = []

            if (attribute_name == "textContent") and (len(value) > 0):
                self.textContentValue = value
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
                        filtered_elements = strict_filtered_elements[:]
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
                    list_of_element_with_similarity = []
                    if len(filtered_elements) > 1:
                        list_we_search_for = filtered_elements[:]
                    else:
                        list_we_search_for = current_cached_list[:]
                    similarity_old = 0
                    # evaluate the similarity between the text element and the value in reference
                    for element in list_we_search_for:
                        visible_text = element.text
                        similarity = self.similarity_coefficient(visible_text, value)
                        # insert the element in the list if similarity > at the SimilarityCoeffcientMin parameter in settings.yaml
                        if similarity > self.SimilarityCoeffcientMin:
                            # the element with the maximun similarity in the first place of the list : TODO: Gérer une liste provisoire avec le coefficient de similarité pour faire un tri décroissant avant de restocker la liste d'élément trouvé
                            if similarity > similarity_old:
                                similarity_old = similarity
                                list_of_element_with_similarity.insert(0, element)
                            else:
                                list_of_element_with_similarity.append(element)
                    if (len(list_of_element_with_similarity) > 0) and (len(list_of_element_with_similarity) <= len(list_we_search_for)):
                        filtered_elements = list_of_element_with_similarity[:]
                        

            else:    # self:: --> forces the search to be carried out on the element itself
                if "'" in value:    # avoid mixing single and double quotes in Xpath
                    xpath = f'self::*[@{attribute_name}="{value}"]'                
                else: 
                    xpath = f"self::*[@{attribute_name}='{value}']"
                filtered_elements = [element for element in current_cached_list if element.find_elements(By.XPATH, xpath)]     # alternative : if element.get_attribute(attribute_name) == value
                print("Nombre d'élement avec le Xpath : " + xpath + " = " + str(len(filtered_elements)))

            # Determines whether you have found the item you are looking for or whether you need to continue
            if len(filtered_elements) == 1: # Element found
                current_cached_list = filtered_elements[:]    
                break
            elif len(filtered_elements) > 1: # Multiple elements found
                if len(filtered_elements) < len(current_cached_list):
                    current_cached_list = filtered_elements[:]
                else:
                    filtered_elements = current_cached_list[:]

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


    def find_most_frequent_elements_by_siblings(self, elements_list: list[WebElement], json_sibling_properties, textContentValue):
        """
        Finds the web element with the most sibling matches based on JSON properties, 
        but only among the provided elements.

        Args:
            elements_list (list[WebElement]): List of WebElements to filter from.
            json_sibling_properties: List of dictionaries containing sibling properties.
            textContentValue: the text content value

        Returns:
            list[WebElement]: The list of WebElements that are the most frequent in sibling list.
        """
        selenium_lib = BuiltIn().get_library_instance(self.seleniumInstanceName)
        # Initialize the merged list for all found elements
        all_elements = []
        # Iterate through each sibling property group in the JSON
        for sibling_props in json_sibling_properties:
            # Build an XPath based on properties to identify siblings
            sibling_tag = sibling_props['tagName']
            sibling_text = sibling_props['textContent']

            # if sibling_text is empty verify if element with the tag and self.textContent existe on the DOM and replace sibling_text by self.textContentValue
            if not sibling_text.strip() and self.textContentValue.strip():
                xpath = self.get_sibling_xpath(sibling_tag, self.textContentValue)
                matching_elements = selenium_lib.driver.find_elements(By.XPATH, f"//*[following-sibling::{xpath} or preceding-sibling::{xpath}]")
                if len(matching_elements) > 0:
                    sibling_text = self.textContentValue

            # Iterate over the elements_list to find which have corresponding siblings.
            for element in elements_list:
                # construct xpath for the parent to search the sibling inside the parent
                parent_xpath = "./.."
                parent_element = element.find_element(By.XPATH,parent_xpath)
                # Execute the xpath for the sibling search into the parent element
                xpath = self.get_sibling_xpath(sibling_tag, sibling_text)
                sibling_elements = parent_element.find_elements(By.XPATH, f".//*[following-sibling::{xpath} or preceding-sibling::{xpath}]")
                # Filter sibling_elements to keep only those present in elements_list
                valid_sibling_elements = [sib for sib in sibling_elements if sib in elements_list]
                all_elements.extend(valid_sibling_elements)

        # Use Counter to count occurrences of each element
        element_counts = Counter(all_elements)

        # Find the element that appears most frequently in the merged list
        most_frequent_elements = []
        if element_counts:
            most_common = element_counts.most_common()
            if not most_common:
                return [] # return empty list if no element found
            max_frequency = most_common[0][1]  # Get the highest frequency
            most_frequent_elements = [element for element, count in most_common if count == max_frequency]
            if len(most_frequent_elements) > 1:
                print(f"Warning: Multiple elements have the same highest frequency: {most_frequent_elements}. Multiple elements are return.")

        return most_frequent_elements


    def find_most_frequent_elements_by_siblings_fastway(self, json_sibling_properties):
        """
        Finds the web element with the most sibling matches based on JSON properties.
        Fastway against find_most_frequent_elements_by_siblings but maybe less accurate.

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
            xpath = self.get_sibling_xpath(sibling_props['tagName'], sibling_props['textContent'])
            # Find elements with siblings matching this XPath
            matching_elements = selenium_lib.driver.find_elements(By.XPATH, f"//*[following-sibling::{xpath} or preceding-sibling::{xpath}]")
            # Add the found elements to the merged list
            all_elements.extend(matching_elements)

        # Use Counter to count occurrences of each element
        element_counts = Counter(all_elements)

        # Find the element that appears most frequently in the merged list
        most_frequent_elements = []
        if element_counts:
            most_common = element_counts.most_common()
            if not most_common:
                return [] # return empty list if no element found
            max_frequency = most_common[0][1]  # Get the highest frequency
            most_frequent_elements = [element for element, count in most_common if count == max_frequency]
            if len(most_frequent_elements) > 1:
                print(f"Warning: Multiple elements have the same highest frequency: {most_frequent_elements}. Multiple elements are return.")

        return most_frequent_elements


    def find_elements_by_ia_with_driver(self, scanned_element_json_name:str, additionalProperties:dict = None) -> any:
        """
        Find elements by IA using Selenium WebDriver.

        Args:
            scanned_element_json_name (str): Name of the scanned element JSON file.

        Returns:
            list: A list of unique elements found.
        """
        # reinit global variables
        config = yaml.safe_load(open(Path(__file__).parent / "settings.yaml"))
        self.continueOnMultipleElement = self.get_boolean_setting(config, "continueOnMultipleElement")
        self.textContentValue = ""
        self.elementIndex = -1

        # Get the data of the element json file
        scanned_element_json = self.AutomIAlib.read_json_file(f'{scanned_element_json_name}.json')

        # Add additional properties to the scanned element JSON
        if additionalProperties:
            scanned_element_json.update(additionalProperties)

        # classic search only on the attribute of the element in the object repository json file
        elements_found = self.get_by_attributes(scanned_element_json)
        print(f"nombre d'élements encore en lice après recherche par attributs : {len(elements_found)}")
        
        # if more than 1 element is in the list try search by siblings
        if (len(elements_found) > 1):
            if "siblings" in scanned_element_json and scanned_element_json["siblings"]:    # Check if "siblings" exists and is not empty
                if (len(elements_found) > 80):
                    siblings_way_result = self.find_most_frequent_elements_by_siblings_fastway(scanned_element_json["siblings"])                    
                else:
                    siblings_way_result = self.find_most_frequent_elements_by_siblings(elements_found, scanned_element_json["siblings"], self.textContentValue)
                if (len(siblings_way_result) > 0):
                    elements_found = siblings_way_result[:]

        # if more than 1 element is in the list try search by parents
#        if (len(elements_found) > 1):
#            print(f"nombre d'élements encore en lice après recherche par attributs : {len(elements_found)}")
#            if "siblings" in scanned_element_json and scanned_element_json["siblings"]:    # Check if "siblings" exists and is not empty
#                siblings_way_result = self.find_most_frequent_elements_by_siblings(scanned_element_json["siblings"])
#                if (len(siblings_way_result) > 0):
#                    elements_found = siblings_way_result[:]

        # Return one or none element
        if len(elements_found) == 0:
            return []
        if len(elements_found) == 1:
            return elements_found[0]
        if (len(elements_found) > 1) and self.continueOnMultipleElement:
            if self.elementIndex < len(elements_found):
                return elements_found[self.elementIndex]
            else:
                print(f"l'index de l'élement demandé : {self.elementIndex} est supérieur au nombre d'élements trouvés : {len(elements_found)}")
                return elements_found[0]
        else:
            return []


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


    def similarity_coefficient(self, s1, s2):
        """
         Calculat max similarity beteween two string.
         Args:
             strings to verify.
         Returns:
             the maximum coefficent of similarity between the two strings in entry.
         """
        # Verify if string are not empty
        if not s1.strip() or not s2.strip():
            return 0
    
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
    

    def get_sibling_xpath(self, sibling_tag, textContentValue):
        """
         Construc sibling xpath to find element with this sibling.
         Args:
             text content value of the sibling.
         Returns:
             xpath to find element with this sibling.
         """
        if "'" in textContentValue:
            sibling_xpath_contains = f"contains(., \"{textContentValue}\")"
        else:
            sibling_xpath_contains = f"contains(., '{textContentValue}')"

        # Construct the xpath to find the sibling in the DOM
        xpath = f"{sibling_tag}[{sibling_xpath_contains}]"

        return xpath

