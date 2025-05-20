from collections import Counter
import time
import yaml
import re
import Levenshtein
from difflib import SequenceMatcher
from math import sqrt
from robot.libraries.BuiltIn import BuiltIn
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import NoSuchElementException
from AutomIAlib import AutomIAlib
from pathlib import Path
from typing import Any, List, Dict, Tuple, Optional, Union

class FindWebElements:
    
    # Path to the attributes weight definition file
    attributes_weight_file_path: Path = Path(__file__).parent / "attributesWeight.properties"
    seleniumInstanceName: str = "SeleniumLibrary"

    def __init__(self) -> None:
        self.AutomIAlib = AutomIAlib()
        with open(Path(__file__).parent / "settings.yaml", 'r') as f:
            config: Dict[str, Any] = yaml.safe_load(f)
        self.seleniumInstanceName = config["SeleniumLibraryInstanceName"]
        self.SimilarityCoeffcientMin: float = float(config.get("SimilarityCoeffcientMin", 0.0))
        self.continueOnMultipleElement: bool = self.get_boolean_setting(config, "continueOnMultipleElement")
        self.textContentValue: str = ""
        self.elementIndex: int = -1

    def get_boolean_setting(self, config: Dict[str, Any], key: str, default: bool = False) -> bool:
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


    def safe_int_conversion(self, value: Any, default: int = 0) -> int:
        """Convert string to integer safely. Returns `default` if conversion fails."""
        try:
            return int(str(value))
        except (ValueError, TypeError):
            return default
    

    def filter_elements_by_tag_name_by_driver(self, tag_name: str) -> List[WebElement]:
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


    def get_element_attributes(self, scanned_element_json: Dict[str, Any]) -> List[Tuple[str, Any, int]]:
        """
        Get all the attributes and their weight of the scanned_element_json.
        if one of the found attribute has no weight define in the attributes_weight file, is default weight will be 10

        Args:
            scanned_element_json (Dict[str, Any]): scanned element JSON data.
        
        Returns:
            List[Tuple[str, Any, int]]: A list of tuples containing this attribute key is value and is weight.
        """
        # Read the attribute weight properties file
        file_attributes = self.AutomIAlib.read_properties_file(str(self.attributes_weight_file_path))
        # Extract values based on the sorted attribute list
        attributes: List[Tuple[str, Any, int]] = []

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
                if attr == str(key):
                    in_attributes_weight_file = True
                    print("Attibut traité : " + attr)
                    attributes.append((attr, scanned_element_json[attr], self.safe_int_conversion(weight, 10)))
                    break
            if not in_attributes_weight_file:
                attributes.append((attr, scanned_element_json[attr], 10))

        return sorted(attributes, key=lambda elm: int(elm[2]), reverse=True) # sort the attributes by decreasing weight order


    def get_by_attributes(self, scanned_element_json: Dict[str, Any]) -> List[WebElement]:
        """
        Get all corresponding elements with the attributes of the scanned element.

        Args:
            scanned_element_json (json): scanned element JSON data.

        Returns:
            List[WebElement]: A list of filtered elements.
        """
        # Initialize a SeleniumLibrary instance
        selenium_lib = BuiltIn().get_library_instance(self.seleniumInstanceName)
        # Get the tagName of the element to retrieve in the DOM
        tag_name = scanned_element_json.get("tagName")
        # Ensure tag_name is a non-empty string before proceeding
        if not isinstance(tag_name, str) or not tag_name.strip():
            print("Warning: 'tagName' is missing or not a valid string in the scanned element JSON. Cannot filter by tag name.")
            return [] # Return empty list if tag name is missing or invalid
        # Get all the DOM elements possible for the element to find
        starting_list = self.filter_elements_by_tag_name_by_driver(tag_name)
        print("Nombre d'élement avec le TagName : " + tag_name + " = " + str(len(starting_list)))
        # Get all the attribute and their value to begin the search
        sorted_tag_list = self.get_element_attributes(scanned_element_json)
        print("Sorted Tag List : " + str(sorted_tag_list))
        # The most accurate list of possible element found by the attributes search
        current_cached_list = starting_list[:]

        for attribute_name, value, _weight in sorted_tag_list:
            # The list of possible elements found by the current attribute
            filtered_elements = []

            if (attribute_name == "textContent") and (len(value) > 0):
                self.textContentValue = value
                filtered_elements = [element for element in current_cached_list if element.find_elements(By.XPATH, "self::node()[contains(text(), {})]".format(self.escape_xpath_text(value)))]
                # Search the Element with strict content text
                if len(filtered_elements) > 1:
                    strict_filtered_elements = [element for element in filtered_elements if element.find_elements(By.XPATH, "self::node()[text()={}]".format(self.escape_xpath_text(value)))]
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
                filtered_elements = [element for element in current_cached_list if element.find_elements(By.XPATH, "self::*[@{}={}]".format(attribute_name, self.escape_xpath_text(value)))]     # alternative : if element.get_attribute(attribute_name) == value
                print("Nombre d'élement avec l'attribut : " + attribute_name + " = " + str(len(filtered_elements)))

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
    def blink_element(self, element: WebElement, duration: float = 4.0, interval: float = 0.3) -> None:
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


    def find_most_frequent_elements_by_siblings(self, elements_list: List[WebElement], json_sibling_properties: List[Dict[str, Any]], textContentValue: str) -> List[WebElement]:
        """
        Finds the web element with the most sibling matches based on JSON properties, 
        but only among the provided elements.

        Args:
            elements_list (list[WebElement]): List of WebElements to filter from.
            json_sibling_properties (List[Dict[str, Any]]): List of dictionaries containing sibling properties.
            textContentValue (str): the text content value

        Returns:
            list[WebElement]: The list of WebElements that are the most frequent in sibling list.
        """
        selenium_lib = BuiltIn().get_library_instance(self.seleniumInstanceName)
        # Initialize the merged list for all found elements
        all_elements = []
        # Iterate through each sibling property group in the JSON
        for sibling_props in json_sibling_properties:
            # Build an XPath based on properties to identify siblings
            sibling_tag = str(sibling_props.get('tagName', '*'))
            sibling_text = str(sibling_props.get('textContent', ''))

            # if sibling_text is empty verify if element with the tag and self.textContent existe on the DOM and replace sibling_text by self.textContentValue
            if not sibling_text.strip() and textContentValue.strip():
                matching_elements = selenium_lib.driver.find_elements(By.XPATH, f".//*[following-sibling::{sibling_tag}[contains(., {self.escape_xpath_text(textContentValue)})] or preceding-sibling::{sibling_tag}[contains(., {self.escape_xpath_text(textContentValue)})]]")
                if len(matching_elements) > 0:
                    sibling_text = textContentValue

            # Iterate over the elements_list to find which have corresponding siblings.
            for element in elements_list:
                # construct xpath for the parent to search the sibling inside the parent
                parent_xpath = "./.."
                parent_element = element.find_element(By.XPATH,parent_xpath)
                # Execute the xpath for the sibling search into the parent element
                sibling_elements = parent_element.find_elements(By.XPATH, f".//*[following-sibling::{sibling_tag}[contains(., {self.escape_xpath_text(sibling_text)})] or preceding-sibling::{sibling_tag}[contains(., {self.escape_xpath_text(sibling_text)})]]")
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


    def find_most_frequent_elements_by_siblings_fastway(self, json_sibling_properties: List[Dict[str, Any]]) -> List[WebElement]:
        """
        Finds the web element with the most sibling matches based on JSON properties.
        Fastway against find_most_frequent_elements_by_siblings but maybe less accurate.

        Arguments:
        - driver: Instance of Selenium's WebDriver. (Note: driver is not a direct param, it's accessed via selenium_lib)
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
            sibling_tag = str(sibling_props.get('tagName', '*'))
            sibling_text = str(sibling_props.get('textContent', ''))
            # Find elements with siblings matching this XPath
            matching_elements = selenium_lib.driver.find_elements(By.XPATH, f".//*[following-sibling::{sibling_tag}[contains(., {self.escape_xpath_text(sibling_text)})] or preceding-sibling::{sibling_tag}[contains(., {self.escape_xpath_text(sibling_text)})]]")
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
                print(f"Warning: Multiple elements have the same highest frequency in sibling research : {most_frequent_elements}. Multiple elements are return.")

        return most_frequent_elements


    def find_most_frequent_elements_by_parents(self, elements_list: List[WebElement], json_parents_properties: List[Dict[str, Any]], textContentValue: str) -> List[WebElement]:
        """
        Finds the web element with the most parents matches based on JSON properties, 
        but only among the provided elements.

        Args:
            elements_list (list[WebElement]): List of WebElements to filter from.
            json_parents_properties (List[Dict[str, Any]]): List of dictionaries containing parents properties.
            textContentValue (str): the text content value of the element to find or their parents

        Returns:
            list[WebElement]: The list of WebElements that are the most frequent in sibling list.
        """
        # Initialize the merged list for all found elements
        element_with_parents = []
        lowest_level_elements = []

        # Iterate through each sibling property group in the JSON
        for parents_props in json_parents_properties:
            # Build an XPath based on properties to identify siblings
            # parents_tag = str(parents_props.get('tagName', '*'))
            parents_text_prop = parents_props.get('textContent', '').strip()
            text_content_value = textContentValue.strip()
            if not parents_text_prop and text_content_value:
                parents_text = textContentValue
            else:
                parents_text = parents_text_prop
            if not parents_text:
                continue

            # Parcourir chaque élément cible et chercher l'ancêtre contenant le texte
            for element in elements_list:
                try:
                    # Trouver l'ancêtre le plus proche contenant le texte recherché
                    ancestor_with_text = element.find_element(By.XPATH, ".//ancestor::*[contains(text(), {})]".format(self.escape_xpath_text(parents_text)))
                    # Calcul du niveau du parent
                    level = 0
                    current_element = element
                    while current_element != ancestor_with_text:
                        current_element = current_element.find_element(By.XPATH, "./parent::*")
                        level += 1      
                    # Ajouter l'élément et son niveau à la liste des résultats
                    element_with_parents.append((element, level))
                except NoSuchElementException:
                    pass  # Aucun ancêtre contenant le texte trouvé pour cet élément

        # Extraction des éléments avec le niveau le plus bas
        if element_with_parents:
            # Trouver le niveau minimal dans les résultats
            min_level = min(level for _, level in element_with_parents)
            # Extraire les éléments correspondant au niveau le plus bas
            # lowest_level_elements = [element for element, level in element_with_parents if level == min_level]
            lowest_level_elements = list(dict.fromkeys(element for element, level in element_with_parents if level == min_level))
            # Affichage des résultats
            print(f"✅ Niveau le plus bas trouvé : {min_level}")
            print(f"➡️ Warning: Multiple elements have the lowest parent level in parent research : {lowest_level_elements}. Multiple elements are return.")
        else:
            print("❌ Aucun élément n'a de parent contenant le texte recherché.")

        return lowest_level_elements
    

    def find_elements_by_ia_with_driver(self, objectPath: str, scanned_element_json_name: str, additionalProperties: Optional[Dict[str, Any]] = None) -> Union[WebElement, List[WebElement]]:
        """
        Find elements by IA using Selenium WebDriver.

        Args:
            objectPath (str): Path to the object repository.
            scanned_element_json_name (str): Name of the scanned element JSON file (without .json extension).
            additionalProperties (Optional[Dict[str, Any]]): Additional properties to merge into the scanned JSON.

        Returns:
            Union[WebElement, List[WebElement]]: A single WebElement if uniquely found or specified by index, 
                                                  or a list of WebElements (possibly empty if not found or ambiguous).
        """
        # reinit global variables
        config: Dict[str, Any] = yaml.safe_load(open(Path(__file__).parent / "settings.yaml"))
        self.continueOnMultipleElement = self.get_boolean_setting(config, "continueOnMultipleElement")
        self.textContentValue = ""
        self.elementIndex = -1

        # Get the data of the element json file
        scanned_element_json = self.AutomIAlib.read_json_file(objectPath, f'{scanned_element_json_name}.json')

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
                if (len(siblings_way_result) > 0) and (len(siblings_way_result) < len(elements_found)):
                    elements_found = siblings_way_result[:]

        # if more than 1 element is in the list try search by parents
        if (len(elements_found) > 1):
            print(f"nombre d'élements encore en lice après recherche par siblings : {len(elements_found)}")
            if "parents" in scanned_element_json and scanned_element_json["parents"]:    # Check if "parents" exists and is not empty
                parents_way_result = self.find_most_frequent_elements_by_parents(elements_found, scanned_element_json["parents"], self.textContentValue)
                if (len(parents_way_result) > 0) and (len(parents_way_result) < len(elements_found)):
                    elements_found = parents_way_result[:]

        # Return one or none element
        if len(elements_found) == 0:
            return []
        if len(elements_found) == 1:
            return elements_found[0]
        if (len(elements_found) > 1) and self.continueOnMultipleElement:
            if (self.elementIndex < len(elements_found)) and (self.elementIndex >= 0):
                return elements_found[self.elementIndex]
            else:
                if self.elementIndex > 0:
                    print(f"l'index de l'élement demandé : {self.elementIndex} est supérieur au nombre d'élements trouvés : {len(elements_found)}")
                return elements_found[0]
        else:
            return []


    def is_a_regex(self, pattern: str) -> bool:
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


    def similarity_coefficient(self, s1: str, s2: str) -> float:
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
    

    def escape_xpath_text(self, text: str) -> str:
        if "'" not in text:
            return f"'{text}'"
        elif '"' not in text:
            return f'"{text}"'
        else:
            # Si les deux types de quotes sont présents, on utilise concat
            parts = text.split("'")
            return "concat(" + ", \"'\", ".join(f"'{part}'" for part in parts) + ")"