*** Settings ***
Library    AutomIAlib.py
Library    FindWebElements.py
Library    SeleniumLibrary
Library    String

*** Keywords ***
AutomIA Locator Strategy
    [Arguments]    ${browser}    ${locator}   ${tag}    ${constraints}
    Import Variables    ./resources/settings.yaml
    ${locator_parts}=    Split String    ${locator}    |
    ${nbProperties}=    Get length    ${locator_parts}
    ${objFile}=    Set Variable    ${locator_parts[0]}
    ${objPath}=    Set Variable    ${EXECDIR}${ObjectRepositoryPath}${objFile}
    # writes the additional properties passed as parameters to the element's json file
    FOR    ${index}    IN RANGE    1    ${nbProperties}
        Update JSON File    ${objPath}    ${locator_parts[${index}]}
    END    
 #   Log To Console     nbCustomProperties : ${nbProperties}
 #   Log To Console     Object Path : ${objPath}
    ${webelement}=     Find Elements By IA With Driver   ${objPath}
    RETURN    ${webelement}
