*** Settings ***
Library  OperatingSystem
Library     ../test/resources/MyLibraryTest.py
Library     MyLibrary.py
Library     SeleniumLibrary     #plugins=C:/Users/MSU23906/SpyWeb_RobotFramework/test/resources/CustomLocators.py
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

*** Test Cases ***
DemoTest
    [Tags]  Authentification
    Open Browser        ${loginpageurl}
    Maximize Browser Window
    login   ${username}   ${password}
    job application form    ${firstnamevalue}   ${lastnamevalue}    ${emailvalue}   ${addressvalue}   ${cityvalue}    ${zipcodevalue}   ${countryvalue}     ${appliedpositionvalue}     ${coverlettervalue}     ${yearsexperiencevalue}     ${startdatevalue}   ${mobilenumbervalue}
    Close Browser
Example that calls a Python keyword
    MyLibrary.join_two_strings     hello      world
    ${result}=   join_two_strings  hello  world
    Should be equal  ${result}  hello world
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
    Open Browser        ${loginpageurl}
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
    read_properties_file        test/resources/selectorWeight.properties
