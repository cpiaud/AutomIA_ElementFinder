*** Settings ***
Library    AutomIAlib.py
Library    FindWebElements.py
Library    SeleniumLibrary

*** Variables ***


*** Keywords ***
AutomIA Locator Strategy
    [Arguments]    ${browser}    ${locator}    ${tag}    ${constraints}
    ${objPath} =   Set Variable    ${EXECDIR}/demo/objectrepository/${locator}
    ${webelement}=     Find Elements By IA With Driver   ${objPath}
    [Return]    ${webelement}
