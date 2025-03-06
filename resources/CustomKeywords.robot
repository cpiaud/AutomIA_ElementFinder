*** Settings ***
Library    AutomIAlib.py
Library    FindWebElements.py
Library    SeleniumLibrary
Library    String

*** Keywords ***
AutomIA Locator Strategy
    [Arguments]    ${browser}    ${locator}    ${tag}    ${constraints}
    Import Variables    ./resources/settings.yaml
    ${locator_parts}=    Split String    ${locator}    |
    ${nbProperties}=    Get length    ${locator_parts}
    ${objFile}=    Set Variable    ${locator_parts[0]}
    ${objPath}=    Set Variable    ${EXECDIR}${ObjectRepositoryPath}${objFile}
    Run Keyword If    ${nbProperties} > 1    Update JSON File    ${objPath}     ${locator_parts[1]}
    Run Keyword If    ${nbProperties} > 2    Update JSON File    ${objPath}     ${locator_parts[2]}
    Run Keyword If    ${nbProperties} > 3    Update JSON File    ${objPath}     ${locator_parts[3]}
    Run Keyword If    ${nbProperties} > 4    Update JSON File    ${objPath}     ${locator_parts[4]}
    Run Keyword If    ${nbProperties} > 5    Update JSON File    ${objPath}     ${locator_parts[5]}
 #   Log To Console     nbCustomProperties : ${nbProperties}
 #   Log To Console     Object Path : ${objPath}
    ${webelement}=     Find Elements By IA With Driver   ${objPath}
    RETURN    ${webelement}
