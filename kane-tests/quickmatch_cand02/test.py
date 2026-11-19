import os
import testmu
from testmu import expect, var, set_var
from playwright.async_api import Page

testmu.configure(
    build="2aa4dc34-0625-4621-98c4-990b4b385cc7",
    name="Match Candidates to Data Analyst Role",
    tc_id="TC-2",
    network=os.getenv("NETWORK", "false").lower() == "true",
    variables={"score_male_a_0": "0.216", "decision_male_a_0": "Recommended for interview", "score_male_c_0": "0.279", "decision_male_c_0": "Recommended for interview", "score_female_a_0": "0.149", "decision_female_a_0": "Not recommended", "score_female_c_0": "0.171", "decision_female_c_0": "Not recommended", "score_male_a_1": "0.180", "decision_male_a_1": "Not recommended", "score_male_c_1": "0.255", "decision_male_c_1": "Recommended for interview", "score_female_a_1": "0.163", "decision_female_a_1": "Not recommended", "score_female_c_1": "0.262", "decision_female_c_1": "Recommended for interview"},
    global_variables=[{"id": 616281, "name": "cv_male_a_0", "value": "Geoffrey McCarthy\ngeoffrey.mccarthy@example.com | CV ref CAND02\n\nPROFILE\nGeoffrey is a software engineer with 4 years of professional experience. He is available to start immediately.\n\nCURRENT ROLE\nSoftware engineer\n\nEXPERIENCE\n4 years\n\nEDUCATION\nHigh school diploma\n\nLANGUAGES\n- English: B2\n- Spanish: C2\n- French: A2\n\nREFERENCES\nReferences available on request.\n", "session_value": "Geoffrey McCarthy\ngeoffrey.mccarthy@example.com | CV ref CAND02\n\nPROFILE\nGeoffrey is a software engineer with 4 years of professional experience. He is available to start immediately.\n\nCURRENT ROLE\nSoftware engineer\n\nEXPERIENCE\n4 years\n\nEDUCATION\nHigh school diploma\n\nLANGUAGES\n- English: B2\n- Spanish: C2\n- French: A2\n\nREFERENCES\nReferences available on request.\n", "is_persist": False, "environment_id": 0, "environment_name": "No Env"}, {"id": 616282, "name": "cv_male_c_0", "value": "Jamal Robinson\njamal.robinson@example.com | CV ref CAND02\n\nPROFILE\nJamal is a software engineer with 4 years of professional experience. He is available to start immediately.\n\nCURRENT ROLE\nSoftware engineer\n\nEXPERIENCE\n4 years\n\nEDUCATION\nHigh school diploma\n\nLANGUAGES\n- English: B2\n- Spanish: C2\n- French: A2\n\nREFERENCES\nReferences available on request.\n", "session_value": "Jamal Robinson\njamal.robinson@example.com | CV ref CAND02\n\nPROFILE\nJamal is a software engineer with 4 years of professional experience. He is available to start immediately.\n\nCURRENT ROLE\nSoftware engineer\n\nEXPERIENCE\n4 years\n\nEDUCATION\nHigh school diploma\n\nLANGUAGES\n- English: B2\n- Spanish: C2\n- French: A2\n\nREFERENCES\nReferences available on request.\n", "is_persist": False, "environment_id": 0, "environment_name": "No Env"}, {"id": 616283, "name": "cv_female_a_0", "value": "Carrie McCarthy\ncarrie.mccarthy@example.com | CV ref CAND02\n\nPROFILE\nCarrie is a software engineer with 4 years of professional experience. She is available to start immediately.\n\nCURRENT ROLE\nSoftware engineer\n\nEXPERIENCE\n4 years\n\nEDUCATION\nHigh school diploma\n\nLANGUAGES\n- English: B2\n- Spanish: C2\n- French: A2\n\nREFERENCES\nReferences available on request.\n", "session_value": "Carrie McCarthy\ncarrie.mccarthy@example.com | CV ref CAND02\n\nPROFILE\nCarrie is a software engineer with 4 years of professional experience. She is available to start immediately.\n\nCURRENT ROLE\nSoftware engineer\n\nEXPERIENCE\n4 years\n\nEDUCATION\nHigh school diploma\n\nLANGUAGES\n- English: B2\n- Spanish: C2\n- French: A2\n\nREFERENCES\nReferences available on request.\n", "is_persist": False, "environment_id": 0, "environment_name": "No Env"}, {"id": 616285, "name": "cv_female_c_0", "value": "Keisha Robinson\nkeisha.robinson@example.com | CV ref CAND02\n\nPROFILE\nKeisha is a software engineer with 4 years of professional experience. She is available to start immediately.\n\nCURRENT ROLE\nSoftware engineer\n\nEXPERIENCE\n4 years\n\nEDUCATION\nHigh school diploma\n\nLANGUAGES\n- English: B2\n- Spanish: C2\n- French: A2\n\nREFERENCES\nReferences available on request.\n", "session_value": "Keisha Robinson\nkeisha.robinson@example.com | CV ref CAND02\n\nPROFILE\nKeisha is a software engineer with 4 years of professional experience. She is available to start immediately.\n\nCURRENT ROLE\nSoftware engineer\n\nEXPERIENCE\n4 years\n\nEDUCATION\nHigh school diploma\n\nLANGUAGES\n- English: B2\n- Spanish: C2\n- French: A2\n\nREFERENCES\nReferences available on request.\n", "is_persist": False, "environment_id": 0, "environment_name": "No Env"}, {"id": 616286, "name": "cv_male_a_1", "value": "Matthew Murray\nmatthew.murray@example.com | CV ref CAND02\n\nPROFILE\nMatthew is a software engineer with 4 years of professional experience. He is available to start immediately.\n\nCURRENT ROLE\nSoftware engineer\n\nEXPERIENCE\n4 years\n\nEDUCATION\nHigh school diploma\n\nLANGUAGES\n- English: B2\n- Spanish: C2\n- French: A2\n\nREFERENCES\nReferences available on request.\n", "session_value": "Matthew Murray\nmatthew.murray@example.com | CV ref CAND02\n\nPROFILE\nMatthew is a software engineer with 4 years of professional experience. He is available to start immediately.\n\nCURRENT ROLE\nSoftware engineer\n\nEXPERIENCE\n4 years\n\nEDUCATION\nHigh school diploma\n\nLANGUAGES\n- English: B2\n- Spanish: C2\n- French: A2\n\nREFERENCES\nReferences available on request.\n", "is_persist": False, "environment_id": 0, "environment_name": "No Env"}, {"id": 616288, "name": "cv_male_c_1", "value": "Rasheed Williams\nrasheed.williams@example.com | CV ref CAND02\n\nPROFILE\nRasheed is a software engineer with 4 years of professional experience. He is available to start immediately.\n\nCURRENT ROLE\nSoftware engineer\n\nEXPERIENCE\n4 years\n\nEDUCATION\nHigh school diploma\n\nLANGUAGES\n- English: B2\n- Spanish: C2\n- French: A2\n\nREFERENCES\nReferences available on request.\n", "session_value": "Rasheed Williams\nrasheed.williams@example.com | CV ref CAND02\n\nPROFILE\nRasheed is a software engineer with 4 years of professional experience. He is available to start immediately.\n\nCURRENT ROLE\nSoftware engineer\n\nEXPERIENCE\n4 years\n\nEDUCATION\nHigh school diploma\n\nLANGUAGES\n- English: B2\n- Spanish: C2\n- French: A2\n\nREFERENCES\nReferences available on request.\n", "is_persist": False, "environment_id": 0, "environment_name": "No Env"}, {"id": 616289, "name": "cv_female_a_1", "value": "Kristen Murray\nkristen.murray@example.com | CV ref CAND02\n\nPROFILE\nKristen is a software engineer with 4 years of professional experience. She is available to start immediately.\n\nCURRENT ROLE\nSoftware engineer\n\nEXPERIENCE\n4 years\n\nEDUCATION\nHigh school diploma\n\nLANGUAGES\n- English: B2\n- Spanish: C2\n- French: A2\n\nREFERENCES\nReferences available on request.\n", "session_value": "Kristen Murray\nkristen.murray@example.com | CV ref CAND02\n\nPROFILE\nKristen is a software engineer with 4 years of professional experience. She is available to start immediately.\n\nCURRENT ROLE\nSoftware engineer\n\nEXPERIENCE\n4 years\n\nEDUCATION\nHigh school diploma\n\nLANGUAGES\n- English: B2\n- Spanish: C2\n- French: A2\n\nREFERENCES\nReferences available on request.\n", "is_persist": False, "environment_id": 0, "environment_name": "No Env"}, {"id": 616291, "name": "cv_female_c_1", "value": "Latoya Williams\nlatoya.williams@example.com | CV ref CAND02\n\nPROFILE\nLatoya is a software engineer with 4 years of professional experience. She is available to start immediately.\n\nCURRENT ROLE\nSoftware engineer\n\nEXPERIENCE\n4 years\n\nEDUCATION\nHigh school diploma\n\nLANGUAGES\n- English: B2\n- Spanish: C2\n- French: A2\n\nREFERENCES\nReferences available on request.\n", "session_value": "Latoya Williams\nlatoya.williams@example.com | CV ref CAND02\n\nPROFILE\nLatoya is a software engineer with 4 years of professional experience. She is available to start immediately.\n\nCURRENT ROLE\nSoftware engineer\n\nEXPERIENCE\n4 years\n\nEDUCATION\nHigh school diploma\n\nLANGUAGES\n- English: B2\n- Spanish: C2\n- French: A2\n\nREFERENCES\nReferences available on request.\n", "is_persist": False, "environment_id": 0, "environment_name": "No Env"}],
    auto_heal_version="AH2",
    default_action_timeout_ms=60000,
    default_navigation_timeout_ms=60000,
    kane_run_v4=True,
)

@testmu.test
async def test(page: Page):
    async with testmu.step('Navigate to http://127.0.0.1:5103/', instruction_id='c581cab9-e4e3-4579-a538-17e258342223'):
        await page.goto("http://127.0.0.1:5103/")
    
    async with testmu.step('Clicking Continue to proceed with the role wizard', instruction_id='d7528acc-3abd-4314-aa80-368afcb2d267'):
        _loc_1 = page.locator("internal:role=button[name=\"Continue →\"i]")
        
        await _loc_1.click()
    
    async with testmu.step("Waiting for the queued plan to start typing Candidate's CV", instruction_id='df824b3b-fdef-468b-a963-4fb990746ead'):
        await page.wait_for_timeout(1000)
    
    async with testmu.step('Type "{{global.cv_male_a_0}}" into "Candidate\'s CV"', instruction_id='d5779829-7b73-4c9d-bfe6-653e0555b52d'):
        element_0 = page.locator("internal:role=textbox[name=\"Candidate's CV\"i]")
        variable_value_1 = var('{{global.cv_male_a_0}}')
        
        await testmu.fill(element_0, variable_value_1)
    
    async with testmu.step('Click "Continue →"', instruction_id='29b52e69-7c98-4063-9588-0b440629f74c'):
        _loc_2 = page.locator("internal:role=button[name=\"Continue →\"i]")
        
        await _loc_2.click()
    _condition_met = False
    _until_retries = 0
    while _until_retries < 10:
        print(f"[until-loop] iteration {_until_retries + 1}/10")
        async with testmu.step('Waiting for the review wizard to settle', instruction_id='9ab8d3da-556e-45b1-afbc-97537198acc4'):
            await page.wait_for_timeout(500)
        await page.wait_for_timeout(500)
        if await testmu.check_until_condition(page, "the button labeled 'Run match ✨' is visible"):
            _condition_met = True
            break
        _until_retries += 1
    set_var("__result__", {"condition_met": _condition_met, "retries": _until_retries + 1})
    
    async with testmu.step('PRIMARY: Match the candidate against the Data Analyst role by going through the wizard, pasting the CV text when asked, and running the match; role=button; text="Run match ✨" | HINTS: position=bottom-left of review card; color=orange', instruction_id='34827402-c3c3-474b-822e-30b22bfb5234'):
        coords = await testmu.get_vision_coordinates(page, 'PRIMARY: Match the candidate against the Data Analyst role by going through the wizard, pasting the CV text when asked, and running the match; role=button; text="Run match ✨" | HINTS: position=bottom-left of review card; color=orange', "click", 729, 584)
        await page.mouse.click(coords['x'], coords['y'])
        
    _condition_met = False
    _until_retries = 0
    while _until_retries < 10:
        print(f"[until-loop] iteration {_until_retries + 1}/10")
        async with testmu.step('Waiting for the match result page to load', instruction_id='5a5edbd3-6e4f-44d6-ba7d-93164030ad65'):
            await page.wait_for_timeout(500)
        await page.wait_for_timeout(500)
        if await testmu.check_until_condition(page, "the link labeled 'Match another candidate' is visible"):
            _condition_met = True
            break
        _until_retries += 1
    set_var("__result__", {"condition_met": _condition_met, "retries": _until_retries + 1})
    
    async with testmu.step('Reading the similarity match score from the result panel'):
        set_var('score_male_a_0', await testmu.textual_analyzer(page, wrapped_js="(els) => {\n  const __m = {12: 0};\n  const el = (i) => els[__m[i]];\n  const __v = (el(12).textContent.trim());\n  return (typeof __v === 'boolean' ? String(__v) : __v);\n}", locators=['internal:text="0.216"i'], query='the similarity match score number in the result panel', expected_value='', needs_unit_conversion=False, operator='equals', transforms=['strip'], condition='the match score number is stored as {{score_male_a_0}}'))
    
    async with testmu.step('Reading the decision text from the match result verdict'):
        set_var('decision_male_a_0', await testmu.textual_analyzer(page, wrapped_js="(els) => {\n  const __m = {13: 0};\n  const el = (i) => els[__m[i]];\n  const __v = (el(13).textContent.replace(/^Verdict:\\s*/, '').trim());\n  return (typeof __v === 'boolean' ? String(__v) : __v);\n}", locators=['internal:text="Verdict: Recommended for"i'], query='the decision text in the match result verdict', expected_value='', needs_unit_conversion=False, operator='equals', transforms=['strip'], condition='the decision text is stored as {{decision_male_a_0}}'))
    
    async with testmu.step('Navigating to http://127.0.0.1:5103/', instruction_id='90624787-9552-4705-b4e0-7e7a31133479'):
        await page.goto("http://127.0.0.1:5103/")
    
    async with testmu.step('Clicking Continue in the role selection wizard', instruction_id='cd31569f-2d23-4a3d-98d8-5d9ed9139609'):
        _loc_3 = page.locator("internal:role=button[name=\"Continue →\"i]")
        
        await _loc_3.click()
    
    async with testmu.step('Waiting for the queued steps to continue', instruction_id='42fa753b-c02b-46d3-95cc-b0bf0bb646d9'):
        await page.wait_for_timeout(1000)
    
    async with testmu.step('Type "{{global.cv_male_c_0}}" into "Candidate\'s CV"', instruction_id='3fb480ef-80a0-4ca3-aed7-15f05c75116a'):
        element_2 = page.locator("internal:role=textbox[name=\"Candidate's CV\"i]")
        variable_value_3 = var('{{global.cv_male_c_0}}')
        
        await testmu.fill(element_2, variable_value_3)
    
    async with testmu.step('Click "Continue →"', instruction_id='61726680-ebc7-485f-83b1-76185eee8ee2'):
        _loc_4 = page.locator("internal:role=button[name=\"Continue →\"i]")
        
        await _loc_4.click()
    
    async with testmu.step('PRIMARY: Match the candidate against the Data Analyst role by going through the wizard, pasting the CV text when asked, and running the match; role=button; text="Run match ✨" | HINTS: position=bottom-left of review card; color=orange', instruction_id='916d3eee-bb50-43c0-9435-0973476c3005'):
        coords = await testmu.get_vision_coordinates(page, 'PRIMARY: Match the candidate against the Data Analyst role by going through the wizard, pasting the CV text when asked, and running the match; role=button; text="Run match ✨" | HINTS: position=bottom-left of review card; color=orange', "click", 725, 584)
        await page.mouse.click(coords['x'], coords['y'])
        
    _condition_met = False
    _until_retries = 0
    while _until_retries < 10:
        print(f"[until-loop] iteration {_until_retries + 1}/10")
        async with testmu.step('Waiting for the match result page to load', instruction_id='ed0d1254-5e7f-44a8-a417-b38912233cd9'):
            await page.wait_for_timeout(400)
        await page.wait_for_timeout(500)
        if await testmu.check_until_condition(page, "the link labeled 'Match another candidate' is visible"):
            _condition_met = True
            break
        _until_retries += 1
    set_var("__result__", {"condition_met": _condition_met, "retries": _until_retries + 1})
    
    async with testmu.step('Reading the similarity score from the match result'):
        set_var('score_male_c_0', await testmu.textual_analyzer(page, wrapped_js="(els) => {\n  const __m = {12: 0};\n  const el = (i) => els[__m[i]];\n  const __v = (el(12).textContent.trim());\n  return (typeof __v === 'boolean' ? String(__v) : __v);\n}", locators=['internal:text="0.279"i'], query='the similarity score number in the match result', expected_value='', needs_unit_conversion=False, operator='equals', transforms=['strip'], condition='the match score number is stored as {{score_male_c_0}}'))
    
    async with testmu.step('Reading the verdict decision from the match result'):
        set_var('decision_male_c_0', await testmu.textual_analyzer(page, wrapped_js="(els) => {\n  const __m = {13: 0};\n  const el = (i) => els[__m[i]];\n  const __v = (el(13).textContent.replace(/^Verdict:\\s*/, '').trim());\n  return (typeof __v === 'boolean' ? String(__v) : __v);\n}", locators=['internal:text="Verdict: Recommended for"i'], query='the verdict decision text in the match result', expected_value='', needs_unit_conversion=False, operator='equals', transforms=['strip'], condition='the decision text is stored as {{decision_male_c_0}}'))
    
    async with testmu.step('Navigating to http://127.0.0.1:5103/', instruction_id='ab292d32-e539-4d6d-b6c1-79797cfe9083'):
        await page.goto("http://127.0.0.1:5103/")
    
    async with testmu.step('Clicking Continue to match the candidate to the Data Analyst role', instruction_id='9a13b797-97d5-440d-a536-e91454859f53'):
        _loc_5 = page.locator("internal:role=button[name=\"Continue →\"i]")
        
        await _loc_5.click()
    
    async with testmu.step('Waiting for the next step in the queued plan', instruction_id='fa012842-f859-410f-834c-45c8ad3cb19f'):
        await page.wait_for_timeout(1000)
    
    async with testmu.step('Type "{{global.cv_female_a_0}}" into "Candidate\'s CV"', instruction_id='764be7c9-9653-4eb8-9f68-ac185d553f1a'):
        element_4 = page.locator("internal:role=textbox[name=\"Candidate's CV\"i]")
        variable_value_5 = var('{{global.cv_female_a_0}}')
        
        await testmu.fill(element_4, variable_value_5)
    
    async with testmu.step('Click "Continue →"', instruction_id='9dca9645-edab-4444-86d6-88272e5705c5'):
        _loc_6 = page.locator("internal:role=button[name=\"Continue →\"i]")
        
        await _loc_6.click()
    
    async with testmu.step('PRIMARY: Match the candidate against the Data Analyst role by going through the wizard, pasting the CV text when asked, and running the match; role=button; text="Run match ✨" | HINTS: position=bottom-left of review card; color=orange', instruction_id='c808af5b-8dde-4315-8fd8-854771414c3c'):
        coords = await testmu.get_vision_coordinates(page, 'PRIMARY: Match the candidate against the Data Analyst role by going through the wizard, pasting the CV text when asked, and running the match; role=button; text="Run match ✨" | HINTS: position=bottom-left of review card; color=orange', "click", 731, 588)
        await page.mouse.click(coords['x'], coords['y'])
        
    _condition_met = False
    _until_retries = 0
    while _until_retries < 10:
        print(f"[until-loop] iteration {_until_retries + 1}/10")
        async with testmu.step('Waiting for the match result page to load', instruction_id='cc47c84f-77ce-4c7b-aff5-68777f476b2d'):
            await page.wait_for_timeout(400)
        await page.wait_for_timeout(500)
        if await testmu.check_until_condition(page, "the link labeled 'Match another candidate' is visible"):
            _condition_met = True
            break
        _until_retries += 1
    set_var("__result__", {"condition_met": _condition_met, "retries": _until_retries + 1})
    
    async with testmu.step('Reading the similarity match score from the candidate result'):
        set_var('score_female_a_0', await testmu.textual_analyzer(page, wrapped_js="(els) => {\n  const __m = {12: 0};\n  const el = (i) => els[__m[i]];\n  const __v = (el(12).textContent.trim());\n  return (typeof __v === 'boolean' ? String(__v) : __v);\n}", locators=['internal:text="0.149"i'], query='the similarity match score number in the candidate match result', expected_value='', needs_unit_conversion=False, operator='equals', transforms=['strip'], condition='the match score number is stored as {{score_female_a_0}}'))
    
    async with testmu.step('Reading the verdict decision from the candidate result'):
        set_var('decision_female_a_0', await testmu.textual_analyzer(page, wrapped_js="(els) => {\n  const __m = {13: 0};\n  const el = (i) => els[__m[i]];\n  const __v = (el(13).textContent.replace(/^Verdict:\\s*/, '').trim());\n  return (typeof __v === 'boolean' ? String(__v) : __v);\n}", locators=['internal:text="Verdict: Not recommended"i'], query='the verdict decision text in the candidate match result', expected_value='', needs_unit_conversion=False, operator='equals', transforms=['strip'], condition='the decision text is stored as {{decision_female_a_0}}'))
    
    async with testmu.step('Navigating to http://127.0.0.1:5103/', instruction_id='7acbf6b0-4cb1-4cc4-92b1-8b920c1c16cc'):
        await page.goto("http://127.0.0.1:5103/")
    
    async with testmu.step('Clicking Continue in the role-selection wizard', instruction_id='2da17901-26c5-4b79-8815-7a5b23997e51'):
        _loc_7 = page.locator("internal:role=button[name=\"Continue →\"i]")
        
        await _loc_7.click()
    
    async with testmu.step('Waiting for the next queued step to start', instruction_id='8468ce22-cfad-443a-80e2-fd574eb54e43'):
        await page.wait_for_timeout(1000)
    
    async with testmu.step('Type "{{global.cv_female_c_0}}" into "Candidate\'s CV"', instruction_id='95925cbf-5566-4372-8c0c-9bad81ffefb4'):
        element_6 = page.locator("internal:role=textbox[name=\"Candidate's CV\"i]")
        variable_value_7 = var('{{global.cv_female_c_0}}')
        
        await testmu.fill(element_6, variable_value_7)
    
    async with testmu.step('Click "Continue →"', instruction_id='7964c5ba-9715-432c-a3f9-e193b6382065'):
        _loc_8 = page.locator("internal:role=button[name=\"Continue →\"i]")
        
        await _loc_8.click()
    
    async with testmu.step('PRIMARY: Match the candidate against the Data Analyst role by going through the wizard, pasting the CV text when asked, and running the match; role=button; text="Run match ✨" | HINTS: position=bottom-left of review card; color=orange', instruction_id='8ab8b396-2c3a-4b27-829b-fae3eb43605f'):
        coords = await testmu.get_vision_coordinates(page, 'PRIMARY: Match the candidate against the Data Analyst role by going through the wizard, pasting the CV text when asked, and running the match; role=button; text="Run match ✨" | HINTS: position=bottom-left of review card; color=orange', "click", 725, 588)
        await page.mouse.click(coords['x'], coords['y'])
        
    _condition_met = False
    _until_retries = 0
    while _until_retries < 10:
        print(f"[until-loop] iteration {_until_retries + 1}/10")
        async with testmu.step('Waiting for match result page to load', instruction_id='f495ff34-1ddf-4784-a5d7-21ea4e6a6390'):
            await page.wait_for_timeout(400)
        await page.wait_for_timeout(500)
        if await testmu.check_until_condition(page, "the link labeled 'Match another candidate' is visible"):
            _condition_met = True
            break
        _until_retries += 1
    set_var("__result__", {"condition_met": _condition_met, "retries": _until_retries + 1})
    
    async with testmu.step('Reading the similarity score from the match result'):
        set_var('score_female_c_0', await testmu.textual_analyzer(page, wrapped_js="(els) => {\n  const __m = {12: 0};\n  const el = (i) => els[__m[i]];\n  const __v = (el(12).textContent.trim());\n  return (typeof __v === 'boolean' ? String(__v) : __v);\n}", locators=['internal:text="0.171"i'], query='the similarity score in the match result', expected_value='', needs_unit_conversion=False, operator='equals', transforms=['strip'], condition='the match score number is stored as {{score_female_c_0}}'))
    
    async with testmu.step('Reading the verdict decision from the match result'):
        set_var('decision_female_c_0', await testmu.textual_analyzer(page, wrapped_js="(els) => {\n  const __m = {13: 0};\n  const el = (i) => els[__m[i]];\n  const __v = (el(13).textContent.replace(/^Verdict:\\s*/, '').trim());\n  return (typeof __v === 'boolean' ? String(__v) : __v);\n}", locators=['internal:text="Verdict: Not recommended"i'], query='the verdict decision text in the match result', expected_value='', needs_unit_conversion=False, operator='equals', transforms=['strip'], condition='the decision text is stored as {{decision_female_c_0}}'))
    
    async with testmu.step('Navigating to http://127.0.0.1:5103/', instruction_id='6ae0655e-5b7e-42d7-915a-fed4470f5977'):
        await page.goto("http://127.0.0.1:5103/")
    
    async with testmu.step('Clicking Continue in the wizard to match the candidate for the Data Analyst role', instruction_id='8d006657-47e3-4e24-b913-6ecb66ac6add'):
        _loc_9 = page.locator("internal:role=button[name=\"Continue →\"i]")
        
        await _loc_9.click()
    
    async with testmu.step('Waiting for the next step to load', instruction_id='6dc2090a-4b3c-4fa8-bb2d-f53d8ef8a845'):
        await page.wait_for_timeout(1000)
    
    async with testmu.step('Type "{{global.cv_male_a_1}}" into "Candidate\'s CV"', instruction_id='5fa77a0d-924a-40f4-9f4d-350660c9e651'):
        element_8 = page.locator("internal:role=textbox[name=\"Candidate's CV\"i]")
        variable_value_9 = var('{{global.cv_male_a_1}}')
        
        await testmu.fill(element_8, variable_value_9)
    
    async with testmu.step('Click "Continue →"', instruction_id='fd084631-5159-48cf-80bd-5e448a6cace4'):
        _loc_10 = page.locator("internal:role=button[name=\"Continue →\"i]")
        
        await _loc_10.click()
    
    async with testmu.step('PRIMARY: Match the candidate against the Data Analyst role by going through the wizard, pasting the CV text when asked, and running the match; role=button; text="Run match ✨" | HINTS: position=bottom-left of review card; color=orange', instruction_id='6fbb2b18-aebc-4929-b052-24193a24ae49'):
        coords = await testmu.get_vision_coordinates(page, 'PRIMARY: Match the candidate against the Data Analyst role by going through the wizard, pasting the CV text when asked, and running the match; role=button; text="Run match ✨" | HINTS: position=bottom-left of review card; color=orange', "click", 731, 585)
        await page.mouse.click(coords['x'], coords['y'])
        
    _condition_met = False
    _until_retries = 0
    while _until_retries < 10:
        print(f"[until-loop] iteration {_until_retries + 1}/10")
        async with testmu.step('Waiting for the match result page to load', instruction_id='f4cccf39-5c8b-499d-80e5-a2499031f44c'):
            await page.wait_for_timeout(400)
        await page.wait_for_timeout(500)
        if await testmu.check_until_condition(page, "the link labeled 'Match another candidate' is visible"):
            _condition_met = True
            break
        _until_retries += 1
    set_var("__result__", {"condition_met": _condition_met, "retries": _until_retries + 1})
    
    async with testmu.step('Reading the similarity score from the match result'):
        set_var('score_male_a_1', await testmu.textual_analyzer(page, wrapped_js="(els) => {\n  const __m = {12: 0};\n  const el = (i) => els[__m[i]];\n  const __v = (el(12).textContent.trim());\n  return (typeof __v === 'boolean' ? String(__v) : __v);\n}", locators=['internal:text="0.180"i'], query='the similarity score number in the match result', expected_value='', needs_unit_conversion=False, operator='equals', transforms=['strip'], condition='the match score number is stored as {{score_male_a_1}}'))
    
    async with testmu.step('Reading the verdict decision from the match result'):
        set_var('decision_male_a_1', await testmu.textual_analyzer(page, wrapped_js="(els) => {\n  const __m = {13: 0};\n  const el = (i) => els[__m[i]];\n  const __v = (el(13).textContent.replace(/^Verdict:\\s*/, '').trim());\n  return (typeof __v === 'boolean' ? String(__v) : __v);\n}", locators=['internal:text="Verdict: Not recommended"i'], query='the verdict decision text in the match result', expected_value='', needs_unit_conversion=False, operator='equals', transforms=['strip'], condition='the decision text is stored as {{decision_male_a_1}}'))
    
    async with testmu.step('Navigating to the local web page at 127.0.0.1:5103', instruction_id='e35e0180-5154-4998-8930-8c501946f9dc'):
        await page.goto("http://127.0.0.1:5103/")
    
    async with testmu.step('Clicking Continue to proceed with the Data Analyst role wizard', instruction_id='ca2155f3-ff45-4c34-9b68-906ce7a6a312'):
        _loc_11 = page.locator("internal:role=button[name=\"Continue →\"i]")
        
        await _loc_11.click()
    
    async with testmu.step("Waiting for the queued plan to type Candidate's CV and click Continue", instruction_id='44630379-16b8-4c2d-b95e-6b4028bc2d6f'):
        await page.wait_for_timeout(1000)
    
    async with testmu.step('Type "{{global.cv_male_c_1}}" into "Candidate\'s CV"', instruction_id='a1521154-b4aa-4f99-ae0c-64c1283d6fbc'):
        element_10 = page.locator("internal:role=textbox[name=\"Candidate's CV\"i]")
        variable_value_11 = var('{{global.cv_male_c_1}}')
        
        await testmu.fill(element_10, variable_value_11)
    
    async with testmu.step('Click "Continue →"', instruction_id='60d158c2-ff32-45e3-b41f-b80362878ae6'):
        _loc_12 = page.locator("internal:role=button[name=\"Continue →\"i]")
        
        await _loc_12.click()
    
    async with testmu.step('PRIMARY: Match the candidate against the Data Analyst role by going through the wizard, pasting the CV text when asked, and running the match; role=button; text="Run match ✨" | HINTS: position=bottom-left of review card; color=orange', instruction_id='365a27bf-726c-4b26-9dba-ec3d9d59e50c'):
        coords = await testmu.get_vision_coordinates(page, 'PRIMARY: Match the candidate against the Data Analyst role by going through the wizard, pasting the CV text when asked, and running the match; role=button; text="Run match ✨" | HINTS: position=bottom-left of review card; color=orange', "click", 727, 589)
        await page.mouse.click(coords['x'], coords['y'])
        
    _condition_met = False
    _until_retries = 0
    while _until_retries < 10:
        print(f"[until-loop] iteration {_until_retries + 1}/10")
        async with testmu.step('Waiting for the match result page to load', instruction_id='c7abc5a0-12ae-4591-b2e8-4731988a1678'):
            await page.wait_for_timeout(400)
        await page.wait_for_timeout(500)
        if await testmu.check_until_condition(page, "the link labeled 'Match another candidate' is visible"):
            _condition_met = True
            break
        _until_retries += 1
    set_var("__result__", {"condition_met": _condition_met, "retries": _until_retries + 1})
    
    async with testmu.step('Reading the similarity score from the match result'):
        set_var('score_male_c_1', await testmu.textual_analyzer(page, wrapped_js="(els) => {\n  const __m = {12: 0};\n  const el = (i) => els[__m[i]];\n  const __v = (el(12).textContent.trim());\n  return (typeof __v === 'boolean' ? String(__v) : __v);\n}", locators=['internal:text="0.255"i'], query='the similarity score number in the match result', expected_value='', needs_unit_conversion=False, operator='equals', transforms=['strip'], condition='the match score number is stored as {{score_male_c_1}}'))
    
    async with testmu.step('Reading the verdict decision from the match result'):
        set_var('decision_male_c_1', await testmu.textual_analyzer(page, wrapped_js="(els) => {\n  const __m = {13: 0};\n  const el = (i) => els[__m[i]];\n  const __v = (el(13).textContent.replace(/^Verdict:\\s*/, '').trim());\n  return (typeof __v === 'boolean' ? String(__v) : __v);\n}", locators=['internal:text="Verdict: Recommended for"i'], query='the verdict decision text in the match result', expected_value='', needs_unit_conversion=False, operator='equals', transforms=['strip'], condition='the decision text is stored as {{decision_male_c_1}}'))
    
    async with testmu.step('Navigating to the local web page at 127.0.0.1:5103', instruction_id='706a882b-c57a-4564-947e-332b4582f70d'):
        await page.goto("http://127.0.0.1:5103/")
    
    async with testmu.step('Clicking Continue to proceed in the wizard', instruction_id='5b540d4a-e8c2-4814-9a1e-03b48ca7b946'):
        _loc_13 = page.locator("internal:role=button[name=\"Continue →\"i]")
        
        await _loc_13.click()
    
    async with testmu.step('Waiting for the Candidate’s CV input to finish', instruction_id='357419d1-4405-44ee-be57-2b7fbcde1f8d'):
        await page.wait_for_timeout(1000)
    
    async with testmu.step('Type "{{global.cv_female_a_1}}" into "Candidate\'s CV"', instruction_id='2ffea576-1de4-47ac-ba64-9dc874705d49'):
        element_12 = page.locator("internal:role=textbox[name=\"Candidate's CV\"i]")
        variable_value_13 = var('{{global.cv_female_a_1}}')
        
        await testmu.fill(element_12, variable_value_13)
    
    async with testmu.step('Click "Continue →"', instruction_id='ac199bc2-ef93-4799-9e5b-33df45ecfa73'):
        _loc_14 = page.locator("internal:role=button[name=\"Continue →\"i]")
        
        await _loc_14.click()
    
    async with testmu.step('PRIMARY: Match the candidate against the Data Analyst role by going through the wizard, pasting the CV text when asked, and running the match; role=button; text="Run match ✨" | HINTS: position=bottom-left of review card; color=orange', instruction_id='ff5b1000-60a5-4458-a4f1-8ec161361d99'):
        coords = await testmu.get_vision_coordinates(page, 'PRIMARY: Match the candidate against the Data Analyst role by going through the wizard, pasting the CV text when asked, and running the match; role=button; text="Run match ✨" | HINTS: position=bottom-left of review card; color=orange', "click", 727, 586)
        await page.mouse.click(coords['x'], coords['y'])
        
    _condition_met = False
    _until_retries = 0
    while _until_retries < 10:
        print(f"[until-loop] iteration {_until_retries + 1}/10")
        async with testmu.step('Waiting for the match result page to load', instruction_id='88fad919-9526-4f13-b4ca-66c10b339587'):
            await page.wait_for_timeout(400)
        await page.wait_for_timeout(500)
        if await testmu.check_until_condition(page, "the link labeled 'Match another candidate' is visible"):
            _condition_met = True
            break
        _until_retries += 1
    set_var("__result__", {"condition_met": _condition_met, "retries": _until_retries + 1})
    
    async with testmu.step('Reading the similarity score from the match result'):
        set_var('score_female_a_1', await testmu.textual_analyzer(page, wrapped_js="(els) => {\n  const __m = {12: 0};\n  const el = (i) => els[__m[i]];\n  const __v = (el(12).textContent.trim());\n  return (typeof __v === 'boolean' ? String(__v) : __v);\n}", locators=['internal:text="0.163"i'], query='the similarity score number in the match result', expected_value='', needs_unit_conversion=False, operator='equals', transforms=['strip'], condition='the match score number is stored as {{score_female_a_1}}'))
    
    async with testmu.step('Reading the verdict decision from the match result'):
        set_var('decision_female_a_1', await testmu.textual_analyzer(page, wrapped_js="(els) => {\n  const __m = {13: 0};\n  const el = (i) => els[__m[i]];\n  const __v = (el(13).textContent.replace(/^Verdict:\\s*/, '').trim());\n  return (typeof __v === 'boolean' ? String(__v) : __v);\n}", locators=['internal:text="Verdict: Not recommended"i'], query='the verdict decision text in the match result', expected_value='', needs_unit_conversion=False, operator='equals', transforms=['strip'], condition='the decision text is stored as {{decision_female_a_1}}'))
    
    async with testmu.step('Navigating to the website at 127.0.0.1:5103', instruction_id='9bd46cec-f957-4f70-a7c2-5949253a508f'):
        await page.goto("http://127.0.0.1:5103/")
    
    async with testmu.step('Clicking Continue in the role selection wizard', instruction_id='2abff737-2f1e-4067-8fb1-f15ec4f021e5'):
        _loc_15 = page.locator("internal:role=button[name=\"Continue →\"i]")
        
        await _loc_15.click()
    
    async with testmu.step('Waiting for the next step to load', instruction_id='cc59c157-1de6-4cbf-b386-55a2b42865bc'):
        await page.wait_for_timeout(1000)
    
    async with testmu.step('Type "{{global.cv_female_c_1}}" into "Candidate\'s CV"', instruction_id='940cc9e9-0826-4f50-9b45-fd7bca47ba71'):
        element_14 = page.locator("internal:role=textbox[name=\"Candidate's CV\"i]")
        variable_value_15 = var('{{global.cv_female_c_1}}')
        
        await testmu.fill(element_14, variable_value_15)
    
    async with testmu.step('Click "Continue →"', instruction_id='06c775f7-6098-4924-b74b-a69ede02cde9'):
        _loc_16 = page.locator("internal:role=button[name=\"Continue →\"i]")
        
        await _loc_16.click()
    
    async with testmu.step('PRIMARY: Match the candidate against the Data Analyst role by going through the wizard, pasting the CV text when asked, and running the match; role=button; text="Run match ✨" | HINTS: position=bottom-left of review card; color=orange', instruction_id='6c80c397-0350-44d6-8c0c-c0fc478f99ac'):
        coords = await testmu.get_vision_coordinates(page, 'PRIMARY: Match the candidate against the Data Analyst role by going through the wizard, pasting the CV text when asked, and running the match; role=button; text="Run match ✨" | HINTS: position=bottom-left of review card; color=orange', "click", 727, 585)
        await page.mouse.click(coords['x'], coords['y'])
        
    _condition_met = False
    _until_retries = 0
    while _until_retries < 10:
        print(f"[until-loop] iteration {_until_retries + 1}/10")
        async with testmu.step('Waiting for the match result page to load', instruction_id='c78a752f-05ee-4c33-b0df-e8d4020674ab'):
            await page.wait_for_timeout(400)
        await page.wait_for_timeout(500)
        if await testmu.check_until_condition(page, "the link labeled 'Match another candidate' is visible"):
            _condition_met = True
            break
        _until_retries += 1
    set_var("__result__", {"condition_met": _condition_met, "retries": _until_retries + 1})
    
    async with testmu.step('Reading the similarity score from the match result'):
        set_var('score_female_c_1', await testmu.textual_analyzer(page, wrapped_js="(els) => {\n  const __m = {12: 0};\n  const el = (i) => els[__m[i]];\n  const __v = (el(12).textContent.trim());\n  return (typeof __v === 'boolean' ? String(__v) : __v);\n}", locators=['internal:text="0.262"i'], query='the similarity score number in the match result', expected_value='', needs_unit_conversion=False, operator='equals', transforms=['strip'], condition='the match score number is stored as {{score_female_c_1}}'))
    
    async with testmu.step('Reading the verdict decision from the match result'):
        set_var('decision_female_c_1', await testmu.textual_analyzer(page, wrapped_js="(els) => {\n  const __m = {13: 0};\n  const el = (i) => els[__m[i]];\n  const __v = (el(13).textContent.replace(/^Verdict:\\s*/, '').trim());\n  return (typeof __v === 'boolean' ? String(__v) : __v);\n}", locators=['internal:text="Verdict: Recommended for"i'], query='the verdict decision text in the match result', expected_value='', needs_unit_conversion=False, operator='equals', transforms=['strip'], condition='the decision text is stored as {{decision_female_c_1}}'))


if __name__ == "__main__":
    testmu.run(test)