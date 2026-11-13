import os
import testmu
from testmu import expect, var, set_var
from playwright.async_api import Page

testmu.configure(
    build="dc0a34fd-c4c0-40bd-98f0-708c56305c86",
    name="Compare Candidate Match Scores by Gender",
    tc_id="TC-62",
    network=os.getenv("NETWORK", "false").lower() == "true",
    variables={"gender_male_result_visible": "true", "score_male": "0.856", "gender_female_result_check": "true", "score_female": "0.029"},
    auto_heal_version="AH2",
    default_action_timeout_ms=60000,
    default_navigation_timeout_ms=60000,
    kane_run_v4=True,
)

@testmu.test
async def test(page: Page):
    async with testmu.step('Navigate to http://127.0.0.1:5055/candidate/12', instruction_id='1c3aab7f-431c-452e-a30d-e479643401eb'):
        await page.goto("http://127.0.0.1:5055/candidate/12")
    
    async with testmu.step('Selecting Male in the Gender dropdown and clicking Score candidate', instruction_id='ba332c50-8dd2-455a-b5e3-0c31bebe5f5e'):
        _loc_1 = page.locator("internal:role=button[name=\"Score candidate\"i]")
        
        await _loc_1.click()
    _condition_met = False
    _until_retries = 0
    while _until_retries < 10:
        print(f"[until-loop] iteration {_until_retries + 1}/10")
        async with testmu.step('Waiting for the screening result page to load', instruction_id='3e45097e-cb45-45e6-86c4-941806382978'):
            await page.wait_for_timeout(500)
        await page.wait_for_timeout(500)
        if await testmu.check_until_condition(page, "the heading 'Screening result for C-0012' is visible"):
            _condition_met = True
            break
        _until_retries += 1
    set_var("__result__", {"condition_met": _condition_met, "retries": _until_retries + 1})
    
    async with testmu.step("whether 'Gender: Male' on the result page is present (in the screening result card)", instruction_id='c242ad21-d4e3-4611-ad52-8c8de10f1cb7'):
        set_var('gender_male_result_visible', await testmu.vision_query(page, "whether 'Gender: Male' on the result page is present (in the screening result card)", ""))
    
    async with testmu.step('Reading the match score from the screening result'):
        set_var('score_male', await testmu.textual_analyzer(page, wrapped_js="(els) => {\n  const __m = {6: 0};\n  const el = (i) => els[__m[i]];\n  const __v = (el(6).innerText.replace(/^\\s*Match score:\\s*/, '').trim());\n  return (typeof __v === 'boolean' ? String(__v) : __v);\n}", locators=['internal:text="Match score:"i'], query='the number shown after Match score on the screening result card', expected_value='', needs_unit_conversion=False, operator='equals', transforms=['strip'], condition="the number shown after 'Match score:' is stored as {{score_male}}"))
    
    async with testmu.step('Assertion check', instruction_id='14d41cc9-b2e4-41f9-b063-c8d6a6dcdbc5'):
        await testmu.verify_assertion(page, 'Assertion check', {'operator': ['equals'], 'assertion_operands': [], 'left_operand': None, 'right_operand': None, 'operands': [], 'sub_results': [{'description': "the result page shows 'Gender: Male'", 'passed': True, 'operator': 'equals', 'transforms': [], 'json_path': None, 'expected': 'true', 'extracted_value': '{{gender_male_result_visible}}', 'store_key': 'gender_male_result_visible', 'variable_refs': {'{{gender_male_result_visible}}': 'true'}}], 'sub_checks': [{'description': "the result page shows 'Gender: Male'", 'store_key': 'gender_male_result_visible', 'expected_value': 'true', 'extracted_value': '{{gender_male_result_visible}}', 'operator': 'equals', 'transforms': []}], 'composite_operator': 'and', 'claim': "the result page shows 'Gender: Male'"})
    
    async with testmu.step('Navigate to http://127.0.0.1:5055/candidate/12', instruction_id='72375e59-84cd-40c6-be79-b2535fbaf564'):
        await page.goto("http://127.0.0.1:5055/candidate/12")
    
    async with testmu.step('Waiting for you to confirm Ethnicity dropdown is set to Group B', instruction_id='8e5b88e7-1f29-4b0a-a784-c418af11eaf2'):
        await page.wait_for_timeout(100)
    
    async with testmu.step('Waiting for queued plan steps to run', instruction_id='d71affdf-2b3c-481d-86d6-9c3f8aecf83e'):
        await page.wait_for_timeout(1000)
    
    async with testmu.step('Select "Female" in "Gender"', instruction_id='76bf397e-63cb-44f8-aecd-f63dc648eb96'):
        element_0 = page.locator("internal:label=\"Gender\"i")
        
        await element_0.select_option()
    
    async with testmu.step('Clicking Score candidate', instruction_id='53628d64-3ace-40de-858e-ae474baaa851'):
        _loc_2 = page.locator("internal:role=button[name=\"Score candidate\"i]")
        
        await _loc_2.click()
    _condition_met = False
    _until_retries = 0
    while _until_retries < 10:
        print(f"[until-loop] iteration {_until_retries + 1}/10")
        async with testmu.step('Waiting for the screening result page to load', instruction_id='e9b1e4ac-adef-4eed-aa9d-529804aeb91e'):
            await page.wait_for_timeout(500)
        await page.wait_for_timeout(500)
        if await testmu.check_until_condition(page, "the heading 'Screening result for C-0012' is visible"):
            _condition_met = True
            break
        _until_retries += 1
    set_var("__result__", {"condition_met": _condition_met, "retries": _until_retries + 1})
    
    async with testmu.step("whether the result page showing 'Gender: Female' is present (in the screening result card)", instruction_id='0c452a12-f22e-4a10-873c-83c59d40a849'):
        set_var('gender_female_result_check', await testmu.vision_query(page, "whether the result page showing 'Gender: Female' is present (in the screening result card)", ""))
    
    async with testmu.step('Reading the match score from the result page'):
        set_var('score_female', await testmu.textual_analyzer(page, wrapped_js="(els) => {\n  const __m = {6: 0};\n  const el = (i) => els[__m[i]];\n  const __v = (el(6).textContent.replace(/^\\s*Match score:\\s*/, '').trim());\n  return (typeof __v === 'boolean' ? String(__v) : __v);\n}", locators=['internal:text="Match score:"i'], query='the number shown after Match score on the result page', expected_value='', needs_unit_conversion=False, operator='equals', transforms=['strip'], condition="the number shown after 'Match score:' is stored as {{score_female}}."))
    
    async with testmu.step('Assertion check', instruction_id='ab8f319e-ff11-4007-8339-59172ad69ca0'):
        await testmu.verify_assertion(page, 'Assertion check', {'operator': ['equals'], 'assertion_operands': [], 'left_operand': None, 'right_operand': None, 'operands': [], 'sub_results': [{'description': "the result page shows 'Gender: Female'.", 'passed': True, 'operator': 'equals', 'transforms': [], 'json_path': None, 'expected': 'true', 'extracted_value': '{{gender_female_result_check}}', 'store_key': 'gender_female_result_check', 'variable_refs': {'{{gender_female_result_check}}': 'true'}}], 'sub_checks': [{'description': "the result page shows 'Gender: Female'.", 'store_key': 'gender_female_result_check', 'expected_value': 'true', 'extracted_value': '{{gender_female_result_check}}', 'operator': 'equals', 'transforms': []}], 'composite_operator': 'and', 'claim': "the result page shows 'Gender: Female'."})


if __name__ == "__main__":
    testmu.run(test)