*** Settings ***
Documentation       Opens the site with the system Firefox (visible window),
...                 gives you time to log in, then saves the storage state
...                 (cookies + localStorage) to resources/env/auth.json.
...
...                 That file is then reused by
...                 tests/interactive_navigation.robot (Load Storage State
...                 keyword) to compare the 2 versions in an authenticated
...                 session.
...
...                 Run:
...                 robot --outputdir output/robot tests/capture_auth.robot

Library             selenium_screenshot_compare.ScreenshotCompareLibrary


*** Variables ***
${SITE}             https://anathos.me/
${FIREFOX}          /usr/bin/firefox
${AUTH_FILE}        ${CURDIR}/../resources/env/auth.json
# Visible window by default so you can log in manually.
${HEADLESS}         ${False}
# Seconds allowed to log in before the capture.
${LOGIN_WAIT}       ${20}


*** Test Cases ***
Capture The Storage State
    [Documentation]    Log in in the opened window during the wait.
    Open Auth Browser    ${SITE}    ${FIREFOX}    headless=${HEADLESS}
    Log    Log in now (${LOGIN_WAIT}s) then wait for the capture.    console=${True}
    Sleep    ${LOGIN_WAIT}s
    Save Storage State    ${AUTH_FILE}
    [Teardown]    Close Auth Browser
