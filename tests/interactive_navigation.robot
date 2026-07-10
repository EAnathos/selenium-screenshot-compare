*** Settings ***
Documentation       Click-driven navigation scenario, comparing at each step the
...                 rendering between two Firefox versions (driven in parallel).
...
...                 Opens the site in both versions, clicks on buttons/links via
...                 Selenium-style keywords, and at each step checks the rendering
...                 does not diverge above the threshold. A result.json is written
...                 per step to ${CAPTURES_DIR}/<step>/.
...
...                 Run:
...                 robot --outputdir output/robot tests/interactive_navigation.robot

# The package must be installed (pip install -e ".[robot]").
Library             selenium_screenshot_compare.ScreenshotCompareLibrary

Suite Teardown      Close Versions


*** Variables ***
${SITE}             https://anathos.me/
${FIREFOX_A}        /usr/bin/firefox
${FIREFOX_B}        ${CURDIR}/../firefoxes/firefox-128esr/firefox
${CAPTURES_DIR}     ${CURDIR}/../output/interactive
# Storage state (cookies + localStorage) produced by tests/capture_auth.robot.
${AUTH_FILE}        ${CURDIR}/../resources/env/auth.json
# % difference above which a step fails.
${FAIL_OVER}        ${5.0}


*** Test Cases ***
Navigate By Clicks And Compare At Each Step
    [Documentation]    3 steps: home -> click Photography -> back + click language button.
    Open Versions    ${SITE}    ${FIREFOX_A}    ${FIREFOX_B}
    Load Storage State    ${AUTH_FILE}

    Verify Step    home

    Click Element    css=a[href="/photographie"]
    Verify Step    after-click-photography

    Go Back
    Click Element    css=a[href="/en"]
    Verify Step    after-click-language-button


*** Keywords ***
Verify Step
    [Documentation]    Capture the current state of both versions and fail past ${FAIL_OVER} %.
    [Arguments]    ${name}
    ${pct}=    Capture And Compare    ${name}    ${CAPTURES_DIR}
    Log    ${name} -> ${pct} %    console=${True}
    Should Be True    ${pct} <= ${FAIL_OVER}
    ...    msg=Step '${name}': ${pct} % difference (threshold ${FAIL_OVER} %)
