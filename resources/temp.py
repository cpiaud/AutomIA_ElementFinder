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

    def find_elements_by_ia_with_driver(self, scanned_element_json_name:str, additionalProperties:dict = None) -> any:
        """
        Find elements by IA using Selenium WebDriver.

        Args:
            scanned_element_json_name (str): Name of the scanned element JSON file.

        Returns:
            list: A list of unique elements found.
        """
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
            return elements_found[0]
        else:
            return []