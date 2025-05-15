*** Settings ***
Library    AutomIAlib.py
Library    FindWebElements.py
Library    SeleniumLibrary
Library    String
Library    Collections
Variables   ./settings.yaml

*** Keywords ***
AutomIA Locator Strategy
    [Arguments]    ${browser}    ${locator}   ${tag}    ${constraints}
    ${locator_parts}=    Split String    ${locator}    |
    ${nbProperties}=    Get length    ${locator_parts}
    ${objFile}=    Set Variable    ${locator_parts[0]}
    ${objPath}=    Set Variable    ${EXECDIR}${ObjectRepositoryPath}
    ${additionalProperties}=    Create Dictionary
    # transform the additional properties passed as parameters to dictionary
    FOR    ${index}    IN RANGE    1    ${nbProperties}
        ${property}=    Split String    ${locator_parts[${index}]}    :
        ${propertyName}=    Set Variable    ${property[0]}
        ${propertyValue}=    Set Variable    ${property[1]}
        Set To Dictionary    ${additionalProperties}    ${propertyName}    ${propertyValue}
    END    
 #  Log To Console     nbCustomProperties : ${nbProperties}
 #  Log To Console     Object Path : ${objPath}
    ${webelement}=     Find Elements By IA With Driver   ${objPath}    ${objFile}    ${additionalProperties}
    RETURN    ${webelement}
