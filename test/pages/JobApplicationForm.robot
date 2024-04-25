*** Settings ***
Library  SeleniumLibrary
Library  OperatingSystem

*** Variables ***
${loginButton}  xpath://a[text()='Connexion']
${userText}  name:email
${passwordText}  name:pass

${applicationForm}  id:fluentform_153
${applyButton}  xpath://a[text()='Apply']
${firstName}    id:ff_153_names_first_name_
${lastName}     id:ff_153_names_last_name_
${email}        id:ff_153_email
${address}        id:ff_153_address_1_address_line_1_
${city}        id:ff_153_address_1_city_
${zipCode}        id:ff_153_address_1_zip_
${country}        id:ff_153_address_1_country_
${appliedPosition}        id:ff_153_input_text
${coverLetter}        id:ff_153_description_3
${yearsExperience}        id:ff_153_numeric-field
${mobileNumberInputElement}     id:ff_153_phone
${success_form}     id:fluentform_153

*** Keywords ***
job application form
    [Arguments]     ${firstnamevalue}    	${lastnamevalue}     	${emailvalue}        	${addressvalue}        	${cityvalue}       	${zipcodevalue}        	${countryvalue}        	${appliedpositionvalue}       	${coverlettervalue}        	${yearsexperiencevalue}     ${startdatevalue}   ${mobilenumbervalue}
    Log to Console  job application form
    Wait Until Element Is Visible  ${applicationForm}
    Input Text	    ${firstName}    ${firstnamevalue}
    Input Text      ${lastName}     ${lastnamevalue}
    Input Text	    ${email}        ${emailvalue}
    Input Text  	${mobileNumberInputElement}      ${mobilenumbervalue}
    Input Text  	${address}      ${addressvalue}
    Input Text      ${city}     ${cityvalue}
    Input Text	    ${zipCode}      ${zipcodevalue}
    Select From List by Value	    ${country}      ${countryvalue}
    Input Text	    ${appliedPosition}      ${appliedpositionvalue}
    Input Text	    ${coverLetter}      ${coverlettervalue}
    Input Text	    ${yearsExperience}      ${yearsexperiencevalue}
    Execute Javascript          document.querySelector("#ff_153_datetime_1").removeAttribute("readonly");
    Execute Javascript          document.querySelector("#ff_153_datetime_1").removeAttribute("onchange");
    Execute Javascript          document.querySelector("#ff_153_datetime_1").setAttribute("value", "${startdatevalue}");
    Click Element  ${applyButton}
    Wait Until Element Is Visible  ${success_form}
    Log to Console  Job application complete

   
