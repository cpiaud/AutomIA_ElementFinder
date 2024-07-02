*** Settings ***
Library    AutomIAlib.py
Library    FindWebElements.py
Library    SeleniumLibrary

*** Variables ***
${ObjectRepositoryPath}   /demo/objectrepository/

*** Keywords ***
AutomIA Locator Strategy
    [Arguments]    ${browser}    ${locator}    ${tag}    ${constraints}
    ${objPath} =   Set Variable    ${EXECDIR}${ObjectRepositoryPath}${locator}
    ${webelement}=     Find Elements By IA With Driver   ${objPath}
    [Return]    ${webelement}
