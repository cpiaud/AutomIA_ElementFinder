*** Settings ***
Library  OperatingSystem
Library     ../test/resources/MyLibraryTest.py
Library     MyLibrary.py
Library     RetrieveDOMElements.py
Library     SeleniumLibrary
Library    XML
Resource    ../test/pages/LoginPage.robot
Resource    ../test/pages/JobApplicationForm.robot
*** Variables ***
${username}     test
${password}     test
${loginpageurl}    file:///C:/Users/MSU23906/AutomIA_SpyWeb/demo/Login%20V1.html

${firstnamevalue}     test
${lastnamevalue}     test
${emailvalue}     test@test.com
${addressvalue}     test
${cityvalue}     Nantes
${zipcodevalue}     44000
${countryvalue}     FR
${appliedpositionvalue}     test engineer
${coverlettervalue}     test
${yearsexperiencevalue}     8
${startdatevalue}   13/06/2024
${mobilenumbervalue}    06 77 77 77 77
${testlibrary}      text
${email_locator}    ${EMPTY}
${browser}    ${EMPTY}
${locator}    ${EMPTY}
${tag}    ${EMPTY}
${constraints}   ${EMPTY}

*** Keywords ***
Custom Locator Strategy
    [Arguments]    ${browser}    ${locator}    ${tag}    ${constraints}
    ${element}=    Execute Javascript    return window.document.getElementsByName('${locator}')[0];
    [Return]    ${element}
Custom Locator Strategy External Library
    [Arguments]    ${browser}    ${locator}    ${tag}    ${constraints}
    ${element}=     process_json_file_and_generate_locators   test/objectrepository/${locator}.json
    [Return]    ${element}
Find Element By IA Library
    [Arguments]    ${browser}    ${locator}    ${tag}    ${constraints}
    ${xpath}=     find_elements_by_IA   ${locator}
    ${element}=    ${xpath}
    #${element}=    Execute Javascript    return window.document.getElementByXpath("${xpath}");
    [Return]    ${element}
Custom Locator Strategy for XPath
    [Arguments]    ${browser}    ${locator}    ${tag}    ${constraints}
    ${xpath}=     find_elements_by_IA   ${locator}
    ${element}=    Execute Javascript    return document.evaluate("${xpath}", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
    [Return]    ${element}
*** Test Cases ***
DemoTest
    [Tags]  Authentification
    Open Browser        ${loginpageurl}
    Maximize Browser Window
    login   ${username}   ${password}
    job application form    ${firstnamevalue}   ${lastnamevalue}    ${emailvalue}   ${addressvalue}   ${cityvalue}    ${zipcodevalue}   ${countryvalue}     ${appliedpositionvalue}     ${coverlettervalue}     ${yearsexperiencevalue}     ${startdatevalue}   ${mobilenumbervalue}
    Close Browser
Read JSON File Test
    ${json_data}=   read_json_file    test/objectrepository/login_username.json
    Log    ${json_data}
Read JSON File Test Path
    ${json_data}=   read_json_file_test    test/objectrepository/login_password.json
    Log    ${json_data}
Custom Locator Test
    Open Browser        ${loginpageurl}
    Maximize Browser Window
    Wait Until Element Is Visible  name:email
    Input Text  by_testid   email    ${firstnamevalue}
Custom Locator Library Test
    Add Location Strategy    custom    Custom Locator Strategy
    Open Browser        ${loginpageurl}     chrome
    Maximize Browser Window
    Wait Until Element Is Visible  custom:email
    Input Text  custom:email    ${firstnamevalue}
Custom Locator External Library Test
    Add Location Strategy    findElementByAI    Custom Locator Strategy External Library
    Open Browser        ${loginpageurl}
    Maximize Browser Window
    Log     findElementByAI:login_username
    Wait Until Element Is Visible  findElementByAI:login_username
    Input Text  findElementByAI:login_username    ${firstnamevalue}
Locator Generator Test
    Add Location Strategy    findElementByAI    Custom Locator Strategy External Library
    Open Browser        ${loginpageurl}
    Maximize Browser Window
    Wait Until Element Is Visible  findElementByAI:login_username
Properties File Test
    read_properties_file    test/resources/selectorWeight.properties
    Create Webdriver    Chrome
    Open Browser        ${loginpageurl}     Chrome
    Maximize Browser Window
    Close Browser
Retrieve All DOM Elements Test
    Open Browser    ${loginpageurl}     Chrome
    ${elements_json}=    Get Elements From Url
    Log    ${elements_json}
    ${filter_json}=    Filter Elements By Tag Name    test/objectrepository/login_password.json
    Log    ${filter_json}
    Close Browser
Find Element By IA Test
    Open Browser    ${loginpageurl}     Chrome
    ${find_element_by_IA} =    Find Elements By IA  login_password
    Close Browser
Demo Find Elements By IA Test
    Add Location Strategy    FindElementsByIA    Custom Locator Strategy for XPath
    Open Browser        ${loginpageurl}     chrome
    Maximize Browser Window
    Log to Console  login
    Wait Until Element Is Visible       FindElementsByIA:login_username
    Input Text      FindElementsByIA:login_username  ${username}
    Input Text      FindElementsByIA:login_password  ${password}
    Click Element   FindElementsByIA:login_ConnexionButton
    Close Browser