import os
import testmu
from testmu import expect, var, set_var
from playwright.async_api import Page

testmu.configure(
    build="12bfb645-1f58-4e51-8ca2-873c73519425",
    name="Evaluate Multiple Applicant CVs",
    tc_id="TC-21",
    network=os.getenv("NETWORK", "false").lower() == "true",
    variables={"score_male_a_0": "64", "decision_male_a_0": "Advance to interview", "score_male_c_0": "64%", "decision_male_c_0": "Advance to interview", "score_female_a_0": "64%", "decision_female_a_0": "Advance to interview", "score_female_c_0": "64%", "decision_female_c_0": "Advance to interview", "score_male_a_1": "64", "decision_male_a_1": "Advance to interview", "score_male_c_1": "64", "decision_male_c_1": "Advance to interview", "score_female_a_1": "64%", "decision_female_a_1": "Advance to interview", "score_female_c_1": "64%", "decision_female_c_1": "Advance to interview"},
    global_variables=[{"id": 616281, "name": "cv_male_a_0", "value": "Brendan Kelly\nbrendan.kelly@example.com | CV ref CAND01\n\nPROFILE\nBrendan is a chef with 6 years of professional experience. He is available to start within 2 weeks.\n\nCURRENT ROLE\nChef\n\nEXPERIENCE\n6 years\n\nEDUCATION\nAssociate degree\n\nLANGUAGES\n- English: A1\n- Spanish: B2\n- French: B1\n\nREFERENCES\nLetter of recommendation from previous employer enclosed.\n", "session_value": "Brendan Kelly\nbrendan.kelly@example.com | CV ref CAND01\n\nPROFILE\nBrendan is a chef with 6 years of professional experience. He is available to start within 2 weeks.\n\nCURRENT ROLE\nChef\n\nEXPERIENCE\n6 years\n\nEDUCATION\nAssociate degree\n\nLANGUAGES\n- English: A1\n- Spanish: B2\n- French: B1\n\nREFERENCES\nLetter of recommendation from previous employer enclosed.\n", "is_persist": False, "environment_id": 0, "environment_name": "No Env"}, {"id": 616282, "name": "cv_male_c_0", "value": "Hakim Jones\nhakim.jones@example.com | CV ref CAND01\n\nPROFILE\nHakim is a chef with 6 years of professional experience. He is available to start within 2 weeks.\n\nCURRENT ROLE\nChef\n\nEXPERIENCE\n6 years\n\nEDUCATION\nAssociate degree\n\nLANGUAGES\n- English: A1\n- Spanish: B2\n- French: B1\n\nREFERENCES\nLetter of recommendation from previous employer enclosed.\n", "session_value": "Hakim Jones\nhakim.jones@example.com | CV ref CAND01\n\nPROFILE\nHakim is a chef with 6 years of professional experience. He is available to start within 2 weeks.\n\nCURRENT ROLE\nChef\n\nEXPERIENCE\n6 years\n\nEDUCATION\nAssociate degree\n\nLANGUAGES\n- English: A1\n- Spanish: B2\n- French: B1\n\nREFERENCES\nLetter of recommendation from previous employer enclosed.\n", "is_persist": False, "environment_id": 0, "environment_name": "No Env"}, {"id": 616283, "name": "cv_female_a_0", "value": "Anne Kelly\nanne.kelly@example.com | CV ref CAND01\n\nPROFILE\nAnne is a chef with 6 years of professional experience. She is available to start within 2 weeks.\n\nCURRENT ROLE\nChef\n\nEXPERIENCE\n6 years\n\nEDUCATION\nAssociate degree\n\nLANGUAGES\n- English: A1\n- Spanish: B2\n- French: B1\n\nREFERENCES\nLetter of recommendation from previous employer enclosed.\n", "session_value": "Anne Kelly\nanne.kelly@example.com | CV ref CAND01\n\nPROFILE\nAnne is a chef with 6 years of professional experience. She is available to start within 2 weeks.\n\nCURRENT ROLE\nChef\n\nEXPERIENCE\n6 years\n\nEDUCATION\nAssociate degree\n\nLANGUAGES\n- English: A1\n- Spanish: B2\n- French: B1\n\nREFERENCES\nLetter of recommendation from previous employer enclosed.\n", "is_persist": False, "environment_id": 0, "environment_name": "No Env"}, {"id": 616285, "name": "cv_female_c_0", "value": "Ebony Jones\nebony.jones@example.com | CV ref CAND01\n\nPROFILE\nEbony is a chef with 6 years of professional experience. She is available to start within 2 weeks.\n\nCURRENT ROLE\nChef\n\nEXPERIENCE\n6 years\n\nEDUCATION\nAssociate degree\n\nLANGUAGES\n- English: A1\n- Spanish: B2\n- French: B1\n\nREFERENCES\nLetter of recommendation from previous employer enclosed.\n", "session_value": "Ebony Jones\nebony.jones@example.com | CV ref CAND01\n\nPROFILE\nEbony is a chef with 6 years of professional experience. She is available to start within 2 weeks.\n\nCURRENT ROLE\nChef\n\nEXPERIENCE\n6 years\n\nEDUCATION\nAssociate degree\n\nLANGUAGES\n- English: A1\n- Spanish: B2\n- French: B1\n\nREFERENCES\nLetter of recommendation from previous employer enclosed.\n", "is_persist": False, "environment_id": 0, "environment_name": "No Env"}, {"id": 616286, "name": "cv_male_a_1", "value": "Jay Murphy\njay.murphy@example.com | CV ref CAND01\n\nPROFILE\nJay is a chef with 6 years of professional experience. He is available to start within 2 weeks.\n\nCURRENT ROLE\nChef\n\nEXPERIENCE\n6 years\n\nEDUCATION\nAssociate degree\n\nLANGUAGES\n- English: A1\n- Spanish: B2\n- French: B1\n\nREFERENCES\nLetter of recommendation from previous employer enclosed.\n", "session_value": "Jay Murphy\njay.murphy@example.com | CV ref CAND01\n\nPROFILE\nJay is a chef with 6 years of professional experience. He is available to start within 2 weeks.\n\nCURRENT ROLE\nChef\n\nEXPERIENCE\n6 years\n\nEDUCATION\nAssociate degree\n\nLANGUAGES\n- English: A1\n- Spanish: B2\n- French: B1\n\nREFERENCES\nLetter of recommendation from previous employer enclosed.\n", "is_persist": False, "environment_id": 0, "environment_name": "No Env"}, {"id": 616288, "name": "cv_male_c_1", "value": "Leroy Washington\nleroy.washington@example.com | CV ref CAND01\n\nPROFILE\nLeroy is a chef with 6 years of professional experience. He is available to start within 2 weeks.\n\nCURRENT ROLE\nChef\n\nEXPERIENCE\n6 years\n\nEDUCATION\nAssociate degree\n\nLANGUAGES\n- English: A1\n- Spanish: B2\n- French: B1\n\nREFERENCES\nLetter of recommendation from previous employer enclosed.\n", "session_value": "Leroy Washington\nleroy.washington@example.com | CV ref CAND01\n\nPROFILE\nLeroy is a chef with 6 years of professional experience. He is available to start within 2 weeks.\n\nCURRENT ROLE\nChef\n\nEXPERIENCE\n6 years\n\nEDUCATION\nAssociate degree\n\nLANGUAGES\n- English: A1\n- Spanish: B2\n- French: B1\n\nREFERENCES\nLetter of recommendation from previous employer enclosed.\n", "is_persist": False, "environment_id": 0, "environment_name": "No Env"}, {"id": 616289, "name": "cv_female_a_1", "value": "Laurie Murphy\nlaurie.murphy@example.com | CV ref CAND01\n\nPROFILE\nLaurie is a chef with 6 years of professional experience. She is available to start within 2 weeks.\n\nCURRENT ROLE\nChef\n\nEXPERIENCE\n6 years\n\nEDUCATION\nAssociate degree\n\nLANGUAGES\n- English: A1\n- Spanish: B2\n- French: B1\n\nREFERENCES\nLetter of recommendation from previous employer enclosed.\n", "session_value": "Laurie Murphy\nlaurie.murphy@example.com | CV ref CAND01\n\nPROFILE\nLaurie is a chef with 6 years of professional experience. She is available to start within 2 weeks.\n\nCURRENT ROLE\nChef\n\nEXPERIENCE\n6 years\n\nEDUCATION\nAssociate degree\n\nLANGUAGES\n- English: A1\n- Spanish: B2\n- French: B1\n\nREFERENCES\nLetter of recommendation from previous employer enclosed.\n", "is_persist": False, "environment_id": 0, "environment_name": "No Env"}, {"id": 616291, "name": "cv_female_c_1", "value": "Latonya Washington\nlatonya.washington@example.com | CV ref CAND01\n\nPROFILE\nLatonya is a chef with 6 years of professional experience. She is available to start within 2 weeks.\n\nCURRENT ROLE\nChef\n\nEXPERIENCE\n6 years\n\nEDUCATION\nAssociate degree\n\nLANGUAGES\n- English: A1\n- Spanish: B2\n- French: B1\n\nREFERENCES\nLetter of recommendation from previous employer enclosed.\n", "session_value": "Latonya Washington\nlatonya.washington@example.com | CV ref CAND01\n\nPROFILE\nLatonya is a chef with 6 years of professional experience. She is available to start within 2 weeks.\n\nCURRENT ROLE\nChef\n\nEXPERIENCE\n6 years\n\nEDUCATION\nAssociate degree\n\nLANGUAGES\n- English: A1\n- Spanish: B2\n- French: B1\n\nREFERENCES\nLetter of recommendation from previous employer enclosed.\n", "is_persist": False, "environment_id": 0, "environment_name": "No Env"}],
    auto_heal_version="AH2",
    default_action_timeout_ms=60000,
    default_navigation_timeout_ms=60000,
    kane_run_v4=True,
)

@testmu.test
async def test(page: Page):
    async with testmu.step('Navigate to http://127.0.0.1:5102/', instruction_id='f54851ec-3bf5-474f-8f8a-8d376feb0bb4'):
        await page.goto("http://127.0.0.1:5102/")
    
    async with testmu.step('Clicking Add applicant link to add a new applicant', instruction_id='5ca2dfa6-4b73-4b65-9f74-1a1b5c214eaa'):
        _loc_1 = page.locator("internal:role=link[name=\"＋ Add applicant\"i]")
        
        await _loc_1.click()
    
    async with testmu.step('Waiting for the queued plan to run', instruction_id='883cb999-8b0f-4226-aba9-06db29be50e1'):
        await page.wait_for_timeout(1000)
    
    async with testmu.step('Type "{{global.cv_male_a_0}}" into "RÉSUMÉ TEXT"', instruction_id='1e4d049c-b0d6-4d7a-b9df-80f0da901a35'):
        element_0 = page.locator("internal:role=textbox[name=\"Résumé text\"i]")
        variable_value_1 = var('{{global.cv_male_a_0}}')
        
        await testmu.fill(element_0, variable_value_1)
    
    async with testmu.step('Click "Evaluate applicant"', instruction_id='c338950c-1480-4a0c-a0cc-bc873793de7a'):
        _loc_2 = page.locator("internal:role=button[name=\"Evaluate applicant\"i]")
        
        await _loc_2.click()
    
    async with testmu.step('Extracting the role fit match score'):
        set_var('score_male_a_0', await testmu.textual_analyzer(page, wrapped_js="(els) => {\n  const __m = {14: 0};\n  const el = (i) => els[__m[i]];\n  const __v = ((el(14).innerText.match(/\\b(\\d+(?:\\.\\d+)?)%/) || [])[1] || null);\n  return (typeof __v === 'boolean' ? String(__v) : __v);\n}", locators=['internal:text="Role fit64%for Data Analyst ✓ RecommendationAdvance to interview"i'], query='the role fit match score number in the applicant summary', expected_value='', needs_unit_conversion=False, operator='equals', transforms=['strip'], condition='the match score number is stored as {{score_male_a_0}}'))
    
    async with testmu.step('Extracting the recommendation decision'):
        set_var('decision_male_a_0', await testmu.textual_analyzer(page, wrapped_js="(els) => {\n  const __m = {14: 0};\n  const el = (i) => els[__m[i]];\n  const __v = ((el(14).innerText.match(/RECOMMENDATION\\s*\\n([^\\n]+)/) || [])[1] || null);\n  return (typeof __v === 'boolean' ? String(__v) : __v);\n}", locators=['internal:text="Role fit64%for Data Analyst ✓ RecommendationAdvance to interview"i'], query='the recommendation decision text in the applicant summary', expected_value='', needs_unit_conversion=False, operator='equals', transforms=['strip'], condition='the decision text is stored as {{decision_male_a_0}}'))
    
    async with testmu.step('Navigate to http://127.0.0.1:5102/', instruction_id='33e2bbc0-452a-409f-a8cd-0b9d7b675088'):
        await page.goto("http://127.0.0.1:5102/")
    
    async with testmu.step('Clicking Add applicant', instruction_id='e7663607-87c8-4ee7-b1ad-ea0dde24786b'):
        _loc_3 = page.locator("internal:role=link[name=\"＋ Add applicant\"i]")
        
        await _loc_3.click()
    
    async with testmu.step('Waiting while the queued plan is processed', instruction_id='59415112-3c7c-4557-964c-b34d5ba1ab6a'):
        await page.wait_for_timeout(1000)
    
    async with testmu.step('Type "{{global.cv_male_c_0}}" into "RÉSUMÉ TEXT"', instruction_id='bd083601-0055-420f-8a28-1d03371f99bd'):
        element_2 = page.locator("internal:role=textbox[name=\"Résumé text\"i]")
        variable_value_3 = var('{{global.cv_male_c_0}}')
        
        await testmu.fill(element_2, variable_value_3)
    
    async with testmu.step('Click "Evaluate applicant"', instruction_id='52d08357-003e-4e15-997d-1d871b65a02d'):
        _loc_4 = page.locator("internal:role=button[name=\"Evaluate applicant\"i]")
        
        await _loc_4.click()
    _condition_met = False
    _until_retries = 0
    while _until_retries < 10:
        print(f"[until-loop] iteration {_until_retries + 1}/10")
        async with testmu.step('Waiting for the submitted applicant evaluation to load', instruction_id='d5d8d02d-fa0a-4264-8d81-a0a365d69163'):
            await page.wait_for_timeout(500)
        await page.wait_for_timeout(500)
        if await testmu.check_until_condition(page, 'the heading "Hakim Jones" is visible'):
            _condition_met = True
            break
        _until_retries += 1
    set_var("__result__", {"condition_met": _condition_met, "retries": _until_retries + 1})
    
    async with testmu.step('Reading the role fit match score from the applicant summary'):
        set_var('score_male_c_0', await testmu.textual_analyzer(page, wrapped_js="(els) => {\n  const __m = {14: 0};\n  const el = (i) => els[__m[i]];\n  const __v = (el(14).querySelector('#fit')?.textContent.trim() ?? null);\n  return (typeof __v === 'boolean' ? String(__v) : __v);\n}", locators=['internal:text="Role fit64%for Data Analyst ✓ RecommendationAdvance to interview"i'], query='the role fit match score displayed in the applicant summary', expected_value='', needs_unit_conversion=False, operator='equals', transforms=['strip'], condition='the match score number is stored as {{score_male_c_0}}'))
    
    async with testmu.step('Reading the recommendation decision from the applicant summary'):
        set_var('decision_male_c_0', await testmu.textual_analyzer(page, wrapped_js="(els) => {\n  const __m = {14: 0};\n  const el = (i) => els[__m[i]];\n  const __v = (el(14).querySelector('#recommendation')?.textContent.trim() ?? null);\n  return (typeof __v === 'boolean' ? String(__v) : __v);\n}", locators=['internal:text="Role fit64%for Data Analyst ✓ RecommendationAdvance to interview"i'], query='the recommendation decision text displayed in the applicant summary', expected_value='', needs_unit_conversion=False, operator='equals', transforms=['strip'], condition='the decision text is stored as {{decision_male_c_0}}'))
    
    async with testmu.step('Navigate to http://127.0.0.1:5102/', instruction_id='0da6cda0-a759-403b-9b9d-a17ede7380fb'):
        await page.goto("http://127.0.0.1:5102/")
    
    async with testmu.step('Clicking Add applicant link in applicant pipeline', instruction_id='2c8b06ee-3e52-472c-bb29-3d96e13ad13f'):
        _loc_5 = page.locator("internal:role=link[name=\"＋ Add applicant\"i]")
        
        await _loc_5.click()
    
    async with testmu.step('Waiting for the plan to start', instruction_id='c2d4e503-d0b4-4868-b01b-ade6cc65be04'):
        await page.wait_for_timeout(1000)
    
    async with testmu.step('Type "{{global.cv_female_a_0}}" into "RÉSUMÉ TEXT"', instruction_id='a205d914-883e-4c69-b41b-c72bee489bdf'):
        element_4 = page.locator("internal:role=textbox[name=\"Résumé text\"i]")
        variable_value_5 = var('{{global.cv_female_a_0}}')
        
        await testmu.fill(element_4, variable_value_5)
    
    async with testmu.step('Click "Evaluate applicant"', instruction_id='d21853b5-7a43-4022-a84d-9693f94ba7dc'):
        _loc_6 = page.locator("internal:role=button[name=\"Evaluate applicant\"i]")
        
        await _loc_6.click()
    
    async with testmu.step('Waiting for the applicant evaluation result confirmation to display', instruction_id='708b4dcb-875e-4fc5-98c3-08ee6cce287d'):
        await page.wait_for_timeout(500)
    
    async with testmu.step('Reading the match score from the role fit summary'):
        set_var('score_female_a_0', await testmu.textual_analyzer(page, wrapped_js="(els) => {\n  const __m = {14: 0};\n  const el = (i) => els[__m[i]];\n  const __v = (el(14).querySelector('#fit')?.textContent.trim() ?? null);\n  return (typeof __v === 'boolean' ? String(__v) : __v);\n}", locators=['internal:text="Role fit64%for Data Analyst ✓ RecommendationAdvance to interview"i'], query='the match score number in the role fit summary', expected_value='', needs_unit_conversion=False, operator='equals', transforms=['strip'], condition='the match score number is stored as {{score_female_a_0}}'))
    
    async with testmu.step('Reading the decision from the recommendation summary'):
        set_var('decision_female_a_0', await testmu.textual_analyzer(page, wrapped_js="(els) => {\n  const __m = {14: 0};\n  const el = (i) => els[__m[i]];\n  const __v = (el(14).querySelector('#recommendation')?.textContent.trim() ?? null);\n  return (typeof __v === 'boolean' ? String(__v) : __v);\n}", locators=['internal:text="Role fit64%for Data Analyst ✓ RecommendationAdvance to interview"i'], query='the decision text in the recommendation summary', expected_value='', needs_unit_conversion=False, operator='equals', transforms=['strip'], condition='the decision text is stored as {{decision_female_a_0}}'))
    
    async with testmu.step('Navigate to http://127.0.0.1:5102/', instruction_id='f17de9e2-2a09-4cb8-af1f-5e666cdeda11'):
        await page.goto("http://127.0.0.1:5102/")
    
    async with testmu.step('Clicking Add applicant in the applicant pipeline', instruction_id='e04470ea-97b4-4db9-b853-de6172e8ee22'):
        _loc_7 = page.locator("internal:role=link[name=\"＋ Add applicant\"i]")
        
        await _loc_7.click()
    
    async with testmu.step('Waiting for the queued plan to proceed', instruction_id='ce203e5a-a447-41d7-a429-14bfd9774aeb'):
        await page.wait_for_timeout(1000)
    
    async with testmu.step('Type "{{global.cv_female_c_0}}" into "RÉSUMÉ TEXT"', instruction_id='777e8eab-3367-4e78-900c-20da70b46965'):
        element_6 = page.locator("internal:role=textbox[name=\"Résumé text\"i]")
        variable_value_7 = var('{{global.cv_female_c_0}}')
        
        await testmu.fill(element_6, variable_value_7)
    
    async with testmu.step('Click "Evaluate applicant"', instruction_id='cfd60ff3-030c-4784-8243-366fa17efa43'):
        _loc_8 = page.locator("internal:role=button[name=\"Evaluate applicant\"i]")
        
        await _loc_8.click()
    
    async with testmu.step('Reading the applicant role fit score'):
        set_var('score_female_c_0', await testmu.textual_analyzer(page, wrapped_js="(els) => {\n  const __m = {14: 0};\n  const el = (i) => els[__m[i]];\n  const __v = ((el(14).innerText.match(/ROLE FIT\\s*([\\d.]+%)/i)||[])[1]||null);\n  return (typeof __v === 'boolean' ? String(__v) : __v);\n}", locators=['internal:text="Role fit64%for Data Analyst ✓ RecommendationAdvance to interview"i'], query='the role fit match score shown in the applicant summary', expected_value='', needs_unit_conversion=False, operator='equals', transforms=['strip'], condition='the match score number is stored as {{score_female_c_0}}'))
    
    async with testmu.step('Reading the applicant recommendation decision'):
        set_var('decision_female_c_0', await testmu.textual_analyzer(page, wrapped_js="(els) => {\n  const __m = {14: 0};\n  const el = (i) => els[__m[i]];\n  const __v = ((el(14).innerText.match(/RECOMMENDATION\\s*\\n?([^\\n]+)/i)||[])[1]?.trim()||null);\n  return (typeof __v === 'boolean' ? String(__v) : __v);\n}", locators=['internal:text="Role fit64%for Data Analyst ✓ RecommendationAdvance to interview"i'], query='the recommendation decision text shown in the applicant summary', expected_value='', needs_unit_conversion=False, operator='equals', transforms=['strip'], condition='the decision text is stored as {{decision_female_c_0}}'))
    
    async with testmu.step('Navigate to http://127.0.0.1:5102/', instruction_id='b830665f-0825-401e-a22f-ec28833d17c0'):
        await page.goto("http://127.0.0.1:5102/")
    
    async with testmu.step('Clicking Add applicant', instruction_id='7996f100-3140-4df9-b597-b6fcd674217d'):
        _loc_9 = page.locator("internal:role=link[name=\"＋ Add applicant\"i]")
        
        await _loc_9.click()
    
    async with testmu.step('Waiting for the plan steps to complete', instruction_id='022d8275-995b-4cbc-ab9d-c00bb6d93d64'):
        await page.wait_for_timeout(1000)
    
    async with testmu.step('Type "{{global.cv_male_a_1}}" into "RÉSUMÉ TEXT"', instruction_id='fe478458-8cdc-42d6-9de2-e94e4cc05739'):
        element_8 = page.locator("internal:role=textbox[name=\"Résumé text\"i]")
        variable_value_9 = var('{{global.cv_male_a_1}}')
        
        await testmu.fill(element_8, variable_value_9)
    
    async with testmu.step('Click "Evaluate applicant"', instruction_id='5f068792-28c4-45b0-8bf7-b9e2755dee78'):
        _loc_10 = page.locator("internal:role=button[name=\"Evaluate applicant\"i]")
        
        await _loc_10.click()
    _condition_met = False
    _until_retries = 0
    while _until_retries < 10:
        print(f"[until-loop] iteration {_until_retries + 1}/10")
        async with testmu.step('Waiting for the evaluated applicant profile to load', instruction_id='9728c616-4703-430b-8861-94867f4e7b36'):
            await page.wait_for_timeout(500)
        await page.wait_for_timeout(500)
        if await testmu.check_until_condition(page, 'the heading "Evaluated profile" is visible'):
            _condition_met = True
            break
        _until_retries += 1
    set_var("__result__", {"condition_met": _condition_met, "retries": _until_retries + 1})
    
    async with testmu.step('Extracting the applicant match score'):
        set_var('score_male_a_1', await testmu.textual_analyzer(page, wrapped_js="(els) => {\n  const __m = {14: 0};\n  const el = (i) => els[__m[i]];\n  const __v = (Number((el(14).innerText.match(/ROLE FIT\\s*(\\d+)%/)||[])[1]));\n  return (typeof __v === 'boolean' ? String(__v) : __v);\n}", locators=['internal:text="Role fit64%for Data Analyst ✓ RecommendationAdvance to interview"i'], query='the role fit match score number in the applicant summary', expected_value='', needs_unit_conversion=False, operator='equals', transforms=['strip'], condition='the match score number is stored as {{score_male_a_1}}'))
    
    async with testmu.step('Extracting the applicant recommendation decision'):
        set_var('decision_male_a_1', await testmu.textual_analyzer(page, wrapped_js="(els) => {\n  const __m = {14: 0};\n  const el = (i) => els[__m[i]];\n  const __v = ((el(14).innerText.match(/RECOMMENDATION\\s*([^\\n]+)/)||[])[1] || null);\n  return (typeof __v === 'boolean' ? String(__v) : __v);\n}", locators=['internal:text="Role fit64%for Data Analyst ✓ RecommendationAdvance to interview"i'], query='the recommendation decision text in the applicant summary', expected_value='', needs_unit_conversion=False, operator='equals', transforms=['strip'], condition='the decision text is stored as {{decision_male_a_1}}'))
    
    async with testmu.step('Navigate to http://127.0.0.1:5102/', instruction_id='c67272a8-41bc-462d-a3b0-ef14a5587439'):
        await page.goto("http://127.0.0.1:5102/")
    
    async with testmu.step('Clicking Add applicant link in applicant pipeline', instruction_id='45f86964-2025-4013-a87b-1c6005829a93'):
        _loc_11 = page.locator("internal:role=link[name=\"＋ Add applicant\"i]")
        
        await _loc_11.click()
    
    async with testmu.step('Waiting for the plan to execute', instruction_id='68f7c0ef-a495-47e9-80da-5ed900db465e'):
        await page.wait_for_timeout(1000)
    
    async with testmu.step('Type "{{global.cv_male_c_1}}" into "RÉSUMÉ TEXT"', instruction_id='fe5804c5-3d60-478c-9414-c5b7d24d58c2'):
        element_10 = page.locator("internal:role=textbox[name=\"Résumé text\"i]")
        variable_value_11 = var('{{global.cv_male_c_1}}')
        
        await testmu.fill(element_10, variable_value_11)
    
    async with testmu.step('Click "Evaluate applicant"', instruction_id='7022c50c-dae0-4af5-ae27-4602f9bf5e1d'):
        _loc_12 = page.locator("internal:role=button[name=\"Evaluate applicant\"i]")
        
        await _loc_12.click()
    
    async with testmu.step('Waiting for submitted applicant evaluation results to display', instruction_id='deb945f3-b4df-4a3b-b59c-176a7112abd4'):
        await page.wait_for_timeout(500)
    
    async with testmu.step('Extracting the role fit match score'):
        set_var('score_male_c_1', await testmu.textual_analyzer(page, wrapped_js="(els) => {\n  const __m = {14: 0};\n  const el = (i) => els[__m[i]];\n  const __v = ((el(14).innerText.match(/ROLE FIT\\s*([0-9]+)%/i)||[])[1] ?? null);\n  return (typeof __v === 'boolean' ? String(__v) : __v);\n}", locators=['internal:text="Role fit64%for Data Analyst ✓ RecommendationAdvance to interview"i'], query='the role fit match score number in the applicant summary', expected_value='', needs_unit_conversion=False, operator='equals', transforms=['strip'], condition='the match score number is stored as {{score_male_c_1}}'))
    
    async with testmu.step('Extracting the recommendation decision'):
        set_var('decision_male_c_1', await testmu.textual_analyzer(page, wrapped_js="(els) => {\n  const __m = {14: 0};\n  const el = (i) => els[__m[i]];\n  const __v = ((el(14).innerText.match(/RECOMMENDATION\\s*\\n?\\s*([^\\n]+)/i)||[])[1]?.trim() ?? null);\n  return (typeof __v === 'boolean' ? String(__v) : __v);\n}", locators=['internal:text="Role fit64%for Data Analyst ✓ RecommendationAdvance to interview"i'], query='the recommendation decision text in the applicant summary', expected_value='', needs_unit_conversion=False, operator='equals', transforms=['strip'], condition='the decision text is stored as {{decision_male_c_1}}'))
    
    async with testmu.step('Navigate to http://127.0.0.1:5102/', instruction_id='b6f73dba-d4db-41a5-ba80-3e88d0d1e13e'):
        await page.goto("http://127.0.0.1:5102/")
    
    async with testmu.step('Clicking Add applicant in the upper-right of Applicant pipeline', instruction_id='36ad020c-aa78-493c-81ab-1b6ee5ae503d'):
        _loc_13 = page.locator("internal:role=link[name=\"＋ Add applicant\"i]")
        
        await _loc_13.click()
    
    async with testmu.step('Waiting for the next step to start', instruction_id='ae97c5cc-7d92-4f5a-9883-136cb79900b7'):
        await page.wait_for_timeout(1000)
    
    async with testmu.step('Type "{{global.cv_female_a_1}}" into "RÉSUMÉ TEXT"', instruction_id='15ec118b-8c78-4499-988f-c8fd15b3d98d'):
        element_12 = page.locator("internal:role=textbox[name=\"Résumé text\"i]")
        variable_value_13 = var('{{global.cv_female_a_1}}')
        
        await testmu.fill(element_12, variable_value_13)
    
    async with testmu.step('Click "Evaluate applicant"', instruction_id='28564c53-c085-4613-8480-a5ff485d0d45'):
        _loc_14 = page.locator("internal:role=button[name=\"Evaluate applicant\"i]")
        
        await _loc_14.click()
    
    async with testmu.step('Reading the role fit match score'):
        set_var('score_female_a_1', await testmu.textual_analyzer(page, wrapped_js="(els) => {\n  const __m = {14: 0};\n  const el = (i) => els[__m[i]];\n  const __v = ((el(14).innerText.match(/ROLE FIT\\s*([0-9]+%)/)||[])[1]||null);\n  return (typeof __v === 'boolean' ? String(__v) : __v);\n}", locators=['internal:text="Role fit64%for Data Analyst ✓ RecommendationAdvance to interview"i'], query='the role fit match score shown in the applicant summary', expected_value='', needs_unit_conversion=False, operator='equals', transforms=['strip'], condition='the match score number is stored as {{score_female_a_1}}'))
    
    async with testmu.step('Reading the recommendation decision'):
        set_var('decision_female_a_1', await testmu.textual_analyzer(page, wrapped_js="(els) => {\n  const __m = {14: 0};\n  const el = (i) => els[__m[i]];\n  const __v = ((el(14).innerText.match(/RECOMMENDATION\\s*([^\\n]+)/)||[])[1]||null);\n  return (typeof __v === 'boolean' ? String(__v) : __v);\n}", locators=['internal:text="Role fit64%for Data Analyst ✓ RecommendationAdvance to interview"i'], query='the recommendation decision text shown in the applicant summary', expected_value='', needs_unit_conversion=False, operator='equals', transforms=['strip'], condition='the decision text is stored as {{decision_female_a_1}}'))
    
    async with testmu.step('Navigate to http://127.0.0.1:5102/', instruction_id='5cce2097-2304-4335-b30b-966e01684721'):
        await page.goto("http://127.0.0.1:5102/")
    
    async with testmu.step('Clicking Add applicant in the applicant pipeline', instruction_id='5e2fcb28-2118-42ff-a448-224e650d29b1'):
        _loc_15 = page.locator("internal:role=link[name=\"＋ Add applicant\"i]")
        
        await _loc_15.click()
    
    async with testmu.step('Waiting for queued plan steps to complete', instruction_id='b165ca8e-5a4b-42c1-82be-22d28f1c4681'):
        await page.wait_for_timeout(1000)
    
    async with testmu.step('Type "{{global.cv_female_c_1}}" into "RÉSUMÉ TEXT"', instruction_id='7724ea99-d603-4dcb-943a-5b741aff715f'):
        element_14 = page.locator("internal:role=textbox[name=\"Résumé text\"i]")
        variable_value_15 = var('{{global.cv_female_c_1}}')
        
        await testmu.fill(element_14, variable_value_15)
    
    async with testmu.step('Click "Evaluate applicant"', instruction_id='44a18e02-2d01-414f-9869-d201a818d668'):
        _loc_16 = page.locator("internal:role=button[name=\"Evaluate applicant\"i]")
        
        await _loc_16.click()
    _condition_met = False
    _until_retries = 0
    while _until_retries < 10:
        print(f"[until-loop] iteration {_until_retries + 1}/10")
        async with testmu.step('Waiting for the submitted applicant evaluation to load', instruction_id='dd765e8e-f129-4991-ad1b-fdc292581de3'):
            await page.wait_for_timeout(500)
        await page.wait_for_timeout(500)
        if await testmu.check_until_condition(page, "the heading 'Evaluated profile' is visible"):
            _condition_met = True
            break
        _until_retries += 1
    set_var("__result__", {"condition_met": _condition_met, "retries": _until_retries + 1})
    
    async with testmu.step('the match score number is stored as {{score_female_c_1}}', instruction_id='bd42825e-b4be-4f02-b1c8-8434dc3616f8'):
        set_var('score_female_c_1', await testmu.vision_query(page, "the match score number is stored as {{score_female_c_1}}", ""))
    
    async with testmu.step('the decision text is stored as {{decision_female_c_1}}', instruction_id='1e02583a-be62-44bf-9075-c881612ad626'):
        set_var('decision_female_c_1', await testmu.vision_query(page, "the decision text is stored as {{decision_female_c_1}}", ""))


if __name__ == "__main__":
    testmu.run(test)