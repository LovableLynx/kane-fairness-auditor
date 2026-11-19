import os
import testmu
from testmu import expect, var, set_var
from playwright.async_api import Page

testmu.configure(
    build="88a9fd97-f8bd-4272-bdf2-4f7a87ff05f2",
    name="Submit and Evaluate CVs for Data Analyst Role",
    tc_id="TC-31",
    network=os.getenv("NETWORK", "false").lower() == "true",
    variables={"score_male_a_0": "1.000", "decision_male_a_0": "SHORTLIST", "score_male_c_0": "0.001", "decision_male_c_0": "REJECT", "score_female_a_0": "0.632", "decision_female_a_0": "SHORTLIST", "score_female_c_0": "0.000", "decision_female_c_0": "REJECT", "score_male_a_1": "1.000", "decision_male_a_1": "SHORTLIST", "score_male_c_1": "0.001", "decision_male_c_1": "REJECT", "score_female_a_1": "0.632", "decision_female_a_1": "SHORTLIST", "score_female_c_1": "0.000", "decision_female_c_1": "REJECT"},
    global_variables=[{"id": 616281, "name": "cv_male_a_0", "value": "Brendan Kelly\nbrendan.kelly@example.com | CV ref CAND01\n\nPROFILE\nBrendan is a chef with 6 years of professional experience. He is available to start within 2 weeks.\n\nCURRENT ROLE\nChef\n\nEXPERIENCE\n6 years\n\nEDUCATION\nAssociate degree\n\nLANGUAGES\n- English: A1\n- Spanish: B2\n- French: B1\n\nREFERENCES\nLetter of recommendation from previous employer enclosed.\n", "session_value": "Brendan Kelly\nbrendan.kelly@example.com | CV ref CAND01\n\nPROFILE\nBrendan is a chef with 6 years of professional experience. He is available to start within 2 weeks.\n\nCURRENT ROLE\nChef\n\nEXPERIENCE\n6 years\n\nEDUCATION\nAssociate degree\n\nLANGUAGES\n- English: A1\n- Spanish: B2\n- French: B1\n\nREFERENCES\nLetter of recommendation from previous employer enclosed.\n", "is_persist": False, "environment_id": 0, "environment_name": "No Env"}, {"id": 616282, "name": "cv_male_c_0", "value": "Hakim Jones\nhakim.jones@example.com | CV ref CAND01\n\nPROFILE\nHakim is a chef with 6 years of professional experience. He is available to start within 2 weeks.\n\nCURRENT ROLE\nChef\n\nEXPERIENCE\n6 years\n\nEDUCATION\nAssociate degree\n\nLANGUAGES\n- English: A1\n- Spanish: B2\n- French: B1\n\nREFERENCES\nLetter of recommendation from previous employer enclosed.\n", "session_value": "Hakim Jones\nhakim.jones@example.com | CV ref CAND01\n\nPROFILE\nHakim is a chef with 6 years of professional experience. He is available to start within 2 weeks.\n\nCURRENT ROLE\nChef\n\nEXPERIENCE\n6 years\n\nEDUCATION\nAssociate degree\n\nLANGUAGES\n- English: A1\n- Spanish: B2\n- French: B1\n\nREFERENCES\nLetter of recommendation from previous employer enclosed.\n", "is_persist": False, "environment_id": 0, "environment_name": "No Env"}, {"id": 616283, "name": "cv_female_a_0", "value": "Anne Kelly\nanne.kelly@example.com | CV ref CAND01\n\nPROFILE\nAnne is a chef with 6 years of professional experience. She is available to start within 2 weeks.\n\nCURRENT ROLE\nChef\n\nEXPERIENCE\n6 years\n\nEDUCATION\nAssociate degree\n\nLANGUAGES\n- English: A1\n- Spanish: B2\n- French: B1\n\nREFERENCES\nLetter of recommendation from previous employer enclosed.\n", "session_value": "Anne Kelly\nanne.kelly@example.com | CV ref CAND01\n\nPROFILE\nAnne is a chef with 6 years of professional experience. She is available to start within 2 weeks.\n\nCURRENT ROLE\nChef\n\nEXPERIENCE\n6 years\n\nEDUCATION\nAssociate degree\n\nLANGUAGES\n- English: A1\n- Spanish: B2\n- French: B1\n\nREFERENCES\nLetter of recommendation from previous employer enclosed.\n", "is_persist": False, "environment_id": 0, "environment_name": "No Env"}, {"id": 616285, "name": "cv_female_c_0", "value": "Ebony Jones\nebony.jones@example.com | CV ref CAND01\n\nPROFILE\nEbony is a chef with 6 years of professional experience. She is available to start within 2 weeks.\n\nCURRENT ROLE\nChef\n\nEXPERIENCE\n6 years\n\nEDUCATION\nAssociate degree\n\nLANGUAGES\n- English: A1\n- Spanish: B2\n- French: B1\n\nREFERENCES\nLetter of recommendation from previous employer enclosed.\n", "session_value": "Ebony Jones\nebony.jones@example.com | CV ref CAND01\n\nPROFILE\nEbony is a chef with 6 years of professional experience. She is available to start within 2 weeks.\n\nCURRENT ROLE\nChef\n\nEXPERIENCE\n6 years\n\nEDUCATION\nAssociate degree\n\nLANGUAGES\n- English: A1\n- Spanish: B2\n- French: B1\n\nREFERENCES\nLetter of recommendation from previous employer enclosed.\n", "is_persist": False, "environment_id": 0, "environment_name": "No Env"}, {"id": 616286, "name": "cv_male_a_1", "value": "Jay Murphy\njay.murphy@example.com | CV ref CAND01\n\nPROFILE\nJay is a chef with 6 years of professional experience. He is available to start within 2 weeks.\n\nCURRENT ROLE\nChef\n\nEXPERIENCE\n6 years\n\nEDUCATION\nAssociate degree\n\nLANGUAGES\n- English: A1\n- Spanish: B2\n- French: B1\n\nREFERENCES\nLetter of recommendation from previous employer enclosed.\n", "session_value": "Jay Murphy\njay.murphy@example.com | CV ref CAND01\n\nPROFILE\nJay is a chef with 6 years of professional experience. He is available to start within 2 weeks.\n\nCURRENT ROLE\nChef\n\nEXPERIENCE\n6 years\n\nEDUCATION\nAssociate degree\n\nLANGUAGES\n- English: A1\n- Spanish: B2\n- French: B1\n\nREFERENCES\nLetter of recommendation from previous employer enclosed.\n", "is_persist": False, "environment_id": 0, "environment_name": "No Env"}, {"id": 616288, "name": "cv_male_c_1", "value": "Leroy Washington\nleroy.washington@example.com | CV ref CAND01\n\nPROFILE\nLeroy is a chef with 6 years of professional experience. He is available to start within 2 weeks.\n\nCURRENT ROLE\nChef\n\nEXPERIENCE\n6 years\n\nEDUCATION\nAssociate degree\n\nLANGUAGES\n- English: A1\n- Spanish: B2\n- French: B1\n\nREFERENCES\nLetter of recommendation from previous employer enclosed.\n", "session_value": "Leroy Washington\nleroy.washington@example.com | CV ref CAND01\n\nPROFILE\nLeroy is a chef with 6 years of professional experience. He is available to start within 2 weeks.\n\nCURRENT ROLE\nChef\n\nEXPERIENCE\n6 years\n\nEDUCATION\nAssociate degree\n\nLANGUAGES\n- English: A1\n- Spanish: B2\n- French: B1\n\nREFERENCES\nLetter of recommendation from previous employer enclosed.\n", "is_persist": False, "environment_id": 0, "environment_name": "No Env"}, {"id": 616289, "name": "cv_female_a_1", "value": "Laurie Murphy\nlaurie.murphy@example.com | CV ref CAND01\n\nPROFILE\nLaurie is a chef with 6 years of professional experience. She is available to start within 2 weeks.\n\nCURRENT ROLE\nChef\n\nEXPERIENCE\n6 years\n\nEDUCATION\nAssociate degree\n\nLANGUAGES\n- English: A1\n- Spanish: B2\n- French: B1\n\nREFERENCES\nLetter of recommendation from previous employer enclosed.\n", "session_value": "Laurie Murphy\nlaurie.murphy@example.com | CV ref CAND01\n\nPROFILE\nLaurie is a chef with 6 years of professional experience. She is available to start within 2 weeks.\n\nCURRENT ROLE\nChef\n\nEXPERIENCE\n6 years\n\nEDUCATION\nAssociate degree\n\nLANGUAGES\n- English: A1\n- Spanish: B2\n- French: B1\n\nREFERENCES\nLetter of recommendation from previous employer enclosed.\n", "is_persist": False, "environment_id": 0, "environment_name": "No Env"}, {"id": 616291, "name": "cv_female_c_1", "value": "Latonya Washington\nlatonya.washington@example.com | CV ref CAND01\n\nPROFILE\nLatonya is a chef with 6 years of professional experience. She is available to start within 2 weeks.\n\nCURRENT ROLE\nChef\n\nEXPERIENCE\n6 years\n\nEDUCATION\nAssociate degree\n\nLANGUAGES\n- English: A1\n- Spanish: B2\n- French: B1\n\nREFERENCES\nLetter of recommendation from previous employer enclosed.\n", "session_value": "Latonya Washington\nlatonya.washington@example.com | CV ref CAND01\n\nPROFILE\nLatonya is a chef with 6 years of professional experience. She is available to start within 2 weeks.\n\nCURRENT ROLE\nChef\n\nEXPERIENCE\n6 years\n\nEDUCATION\nAssociate degree\n\nLANGUAGES\n- English: A1\n- Spanish: B2\n- French: B1\n\nREFERENCES\nLetter of recommendation from previous employer enclosed.\n", "is_persist": False, "environment_id": 0, "environment_name": "No Env"}],
    auto_heal_version="AH2",
    default_action_timeout_ms=60000,
    default_navigation_timeout_ms=60000,
    kane_run_v4=True,
)

@testmu.test
async def test(page: Page):
    async with testmu.step('Navigate to http://127.0.0.1:5101/', instruction_id='5282a34f-89a1-4537-8d17-ec05566b2de4'):
        await page.goto("http://127.0.0.1:5101/")
    
    async with testmu.step('Waiting for the plan steps to complete', instruction_id='b2bf2086-729c-4c83-9953-fffe5c852593'):
        await page.wait_for_timeout(1000)
    
    async with testmu.step('Type "{{global.cv_male_a_0}}" into "CV text"', instruction_id='f414a3e8-9e10-4212-ba5b-a97373d1823c'):
        element_0 = page.locator("internal:role=textbox[name=\"CV text\"i]")
        variable_value_1 = var('{{global.cv_male_a_0}}')
        
        await testmu.fill(element_0, variable_value_1)
    
    async with testmu.step('Click "✨ Screen CV"', instruction_id='cb2c0bf5-ee44-4f20-b927-4cd9b5211b94'):
        _loc_1 = page.locator("internal:role=button[name=\"✨ Screen CV\"i]")
        
        await _loc_1.click()
    
    async with testmu.step('Waiting for the CV screening result confirmation to open', instruction_id='cd376706-ac9f-4d7c-bb3f-a0ce0aaaae24'):
        await page.wait_for_timeout(100)
    
    async with testmu.step('Waiting for the result to open', instruction_id='1f82a8b3-dce1-4168-9520-dd80ad7bf831'):
        await page.wait_for_timeout(100)
    
    async with testmu.step('Reading the match score from the result summary'):
        set_var('score_male_a_0', await testmu.textual_analyzer(page, wrapped_js="(els) => {\n  const __m = {13: 0};\n  const el = (i) => els[__m[i]];\n  const __v = (el(13).textContent.match(/[-+]?\\d*\\.?\\d+/)?.[0] ?? null);\n  return (typeof __v === 'boolean' ? String(__v) : __v);\n}", locators=['internal:text="Match score:"i'], query="the match score number in Brendan Kelly's result summary", expected_value='', needs_unit_conversion=False, operator='equals', transforms=['strip'], condition='the match score number is stored as {{score_male_a_0}}'))
    
    async with testmu.step('the decision text is stored as {{decision_male_a_0}}', instruction_id='2fa2ba45-09e4-49b2-9714-a351b8efdddc'):
        set_var('decision_male_a_0', await testmu.vision_query(page, "the decision text is stored as {{decision_male_a_0}}", ""))
    
    async with testmu.step('Navigate to http://127.0.0.1:5101/', instruction_id='367314f4-5761-49da-ad77-bd3c8f58250f'):
        await page.goto("http://127.0.0.1:5101/")
    
    async with testmu.step('Waiting for the CV text to load', instruction_id='bed111df-d8fc-4f1f-82a6-ff56f041ab6d'):
        await page.wait_for_timeout(1000)
    
    async with testmu.step('Type "{{global.cv_male_c_0}}" into "CV text"', instruction_id='fa0d0649-a39f-4234-b7ed-39c9313b731c'):
        element_2 = page.locator("internal:role=textbox[name=\"CV text\"i]")
        variable_value_3 = var('{{global.cv_male_c_0}}')
        
        await testmu.fill(element_2, variable_value_3)
    
    async with testmu.step('Click "✨ Screen CV"', instruction_id='29438038-0573-48c8-9e93-2c6acc2d3e00'):
        _loc_2 = page.locator("internal:role=button[name=\"✨ Screen CV\"i]")
        
        await _loc_2.click()
    
    async with testmu.step('Waiting for the CV to be submitted for screening', instruction_id='bbe14587-7ba1-409a-97b5-832e5604e833'):
        await page.wait_for_timeout(500)
    
    async with testmu.step('Waiting for the result to open', instruction_id='60a3ea82-e07f-4e78-b59f-402ad600115e'):
        await page.wait_for_timeout(500)
    
    async with testmu.step('Reading the match score from the result summary'):
        set_var('score_male_c_0', await testmu.textual_analyzer(page, wrapped_js="(els) => {\n  const __m = {13: 0};\n  const el = (i) => els[__m[i]];\n  const __v = (el(13).textContent.match(/[-+]?\\d*\\.?\\d+/)?.[0] ?? null);\n  return (typeof __v === 'boolean' ? String(__v) : __v);\n}", locators=['internal:text="Match score:"i'], query="the match score number in Hakim Jones's result summary", expected_value='', needs_unit_conversion=False, operator='equals', transforms=['strip'], condition='the match score number is stored as {{score_male_c_0}}'))
    
    async with testmu.step('Reading the decision from the result summary'):
        set_var('decision_male_c_0', await testmu.textual_analyzer(page, wrapped_js="(els) => {\n  const __m = {10: 0};\n  const el = (i) => els[__m[i]];\n  const __v = ((()=>{const w=document.createTreeWalker(el(10),NodeFilter.SHOW_TEXT);let n;while(n=w.nextNode()){const m=n.nodeValue.match(/Decision:\\s*([^\\n]+)/);if(m)return m[1].trim()}return null})());\n  return (typeof __v === 'boolean' ? String(__v) : __v);\n}", locators=['internal:role=region[name="Hakim Jones"i]'], query="the decision text in Hakim Jones's result summary", expected_value='', needs_unit_conversion=False, operator='equals', transforms=['strip'], condition='the decision text is stored as {{decision_male_c_0}}'))
    
    async with testmu.step('Navigate to http://127.0.0.1:5101/', instruction_id='c5d3b4e1-490b-400f-8142-56119aa4d9e3'):
        await page.goto("http://127.0.0.1:5101/")
    
    async with testmu.step('Waiting for the queued plan to start', instruction_id='561ae605-ebbf-4b30-922b-20e9a521d577'):
        await page.wait_for_timeout(1000)
    
    async with testmu.step('Type "{{global.cv_female_a_0}}" into "CV text"', instruction_id='0f68a45e-72c4-42b7-ad4e-b609785c70e0'):
        element_4 = page.locator("internal:role=textbox[name=\"CV text\"i]")
        variable_value_5 = var('{{global.cv_female_a_0}}')
        
        await testmu.fill(element_4, variable_value_5)
    
    async with testmu.step('Click "✨ Screen CV"', instruction_id='4b098dc0-b509-4043-b6f4-067aad18ec7a'):
        _loc_3 = page.locator("internal:role=button[name=\"✨ Screen CV\"i]")
        
        await _loc_3.click()
    _condition_met = False
    _until_retries = 0
    while _until_retries < 10:
        print(f"[until-loop] iteration {_until_retries + 1}/10")
        async with testmu.step('Waiting for the submitted screening result to load', instruction_id='ef2655f8-dd7c-43e5-89e5-c92cfc131c0a'):
            await page.wait_for_timeout(500)
        await page.wait_for_timeout(500)
        if await testmu.check_until_condition(page, "the heading 'Anne Kelly' is visible"):
            _condition_met = True
            break
        _until_retries += 1
    set_var("__result__", {"condition_met": _condition_met, "retries": _until_retries + 1})
    
    async with testmu.step('Reading the match score from the candidate result'):
        set_var('score_female_a_0', await testmu.textual_analyzer(page, wrapped_js="(els) => {\n  const __m = {13: 0};\n  const el = (i) => els[__m[i]];\n  const __v = (el(13).querySelector('#match-score')?.textContent.trim() ?? null);\n  return (typeof __v === 'boolean' ? String(__v) : __v);\n}", locators=['internal:text="Match score:"i'], query="the match score number in Anne Kelly's candidate result", expected_value='', needs_unit_conversion=False, operator='equals', transforms=['strip'], condition="The match score number is stored as 'score_female_a_0'."))
    
    async with testmu.step("The decision text is stored as 'decision_female_a_0'.", instruction_id='c0cc2e6e-656d-4882-aed8-69afa3e95d9b'):
        set_var('decision_female_a_0', await testmu.vision_query(page, "The decision text is stored as 'decision_female_a_0'.", ""))
    
    async with testmu.step('Navigate to http://127.0.0.1:5101/', instruction_id='5f8dc065-7314-4022-9232-20fde4565c18'):
        await page.goto("http://127.0.0.1:5101/")
    
    async with testmu.step('Waiting while the plan queue runs', instruction_id='3b52be06-3591-46bf-acbd-1e70f033dda7'):
        await page.wait_for_timeout(1000)
    
    async with testmu.step('Type "{{global.cv_female_c_0}}" into "CV text"', instruction_id='ad929a60-33b2-4270-afaa-09b33420a348'):
        element_6 = page.locator("internal:role=textbox[name=\"CV text\"i]")
        variable_value_7 = var('{{global.cv_female_c_0}}')
        
        await testmu.fill(element_6, variable_value_7)
    
    async with testmu.step('Click "✨ Screen CV"', instruction_id='09fe40d7-53b7-47fb-b0ac-c4a3fc9771c2'):
        _loc_4 = page.locator("internal:role=button[name=\"✨ Screen CV\"i]")
        
        await _loc_4.click()
    _condition_met = False
    _until_retries = 0
    while _until_retries < 10:
        print(f"[until-loop] iteration {_until_retries + 1}/10")
        async with testmu.step('Waiting for the screening result to load', instruction_id='2fcc2175-080a-46ab-9aed-be5bde1d539d'):
            await page.wait_for_timeout(500)
        await page.wait_for_timeout(500)
        if await testmu.check_until_condition(page, "the heading 'Ebony Jones' is visible"):
            _condition_met = True
            break
        _until_retries += 1
    set_var("__result__", {"condition_met": _condition_met, "retries": _until_retries + 1})
    
    async with testmu.step('Waiting for the open screening result', instruction_id='6cac647f-021f-442f-96b0-575540044899'):
        await page.wait_for_timeout(250)
    
    async with testmu.step("Reading the match score from Ebony Jones's result summary"):
        set_var('score_female_c_0', await testmu.textual_analyzer(page, wrapped_js="(els) => {\n  const __m = {13: 0};\n  const el = (i) => els[__m[i]];\n  const __v = (el(13).innerText.match(/[-+]?\\d*\\.?\\d+/)?.[0] ?? null);\n  return (typeof __v === 'boolean' ? String(__v) : __v);\n}", locators=['internal:text="Match score:"i'], query="the numeric match score in Ebony Jones's result summary", expected_value='', needs_unit_conversion=False, operator='equals', transforms=['strip'], condition='the match score number is stored as {{score_female_c_0}}'))
    
    async with testmu.step('the decision text is stored as {{decision_female_c_0}}', instruction_id='4036d05a-fc49-42cb-83df-223bb0cb8243'):
        set_var('decision_female_c_0', await testmu.vision_query(page, "the decision text is stored as {{decision_female_c_0}}", ""))
    
    async with testmu.step('Navigate to http://127.0.0.1:5101/', instruction_id='673b2106-b334-4886-a52e-a272703c416e'):
        await page.goto("http://127.0.0.1:5101/")
    
    async with testmu.step('Waiting for the next CV typing step to start', instruction_id='fe77455a-7b89-42d4-8a70-a702b98fa131'):
        await page.wait_for_timeout(1000)
    
    async with testmu.step('Type "{{global.cv_male_a_1}}" into "CV text"', instruction_id='27673f52-b965-4d00-a180-0b4443df25b1'):
        element_8 = page.locator("internal:role=textbox[name=\"CV text\"i]")
        variable_value_9 = var('{{global.cv_male_a_1}}')
        
        await testmu.fill(element_8, variable_value_9)
    
    async with testmu.step('Click "✨ Screen CV"', instruction_id='d9e21a88-f4ee-4d20-ab54-e3ee2d150764'):
        _loc_5 = page.locator("internal:role=button[name=\"✨ Screen CV\"i]")
        
        await _loc_5.click()
    _condition_met = False
    _until_retries = 0
    while _until_retries < 10:
        print(f"[until-loop] iteration {_until_retries + 1}/10")
        async with testmu.step('Waiting for the CV screening result to load', instruction_id='128b39e5-9ac5-4bba-92d8-1564f885a3fe'):
            await page.wait_for_timeout(500)
        await page.wait_for_timeout(500)
        if await testmu.check_until_condition(page, "the heading 'Jay Murphy' is visible"):
            _condition_met = True
            break
        _until_retries += 1
    set_var("__result__", {"condition_met": _condition_met, "retries": _until_retries + 1})
    
    async with testmu.step('Reading the match score from the result summary'):
        set_var('score_male_a_1', await testmu.textual_analyzer(page, wrapped_js="(els) => {\n  const __m = {13: 0};\n  const el = (i) => els[__m[i]];\n  const __v = (el(13).textContent.match(/[0-9]+(?:\\.[0-9]+)?/)?.[0] ?? null);\n  return (typeof __v === 'boolean' ? String(__v) : __v);\n}", locators=['internal:text="Match score:"i'], query="the match score number in Jay Murphy's result summary", expected_value='', needs_unit_conversion=False, operator='equals', transforms=['strip'], condition='the match score number is stored as {{score_male_a_1}}'))
    
    async with testmu.step('Reading the decision from the result summary'):
        set_var('decision_male_a_1', await testmu.textual_analyzer(page, wrapped_js="(els) => {\n  const __m = {10: 0};\n  const el = (i) => els[__m[i]];\n  const __v = (el(10).querySelector('.verdict')?.textContent.replace(/^Decision:\\s*/, '').trim() ?? null);\n  return (typeof __v === 'boolean' ? String(__v) : __v);\n}", locators=['internal:role=region[name="Jay Murphy"i]'], query="the decision text in Jay Murphy's result summary", expected_value='', needs_unit_conversion=False, operator='equals', transforms=['strip'], condition='the decision text is stored as {{decision_male_a_1}}'))
    
    async with testmu.step('Navigate to http://127.0.0.1:5101/', instruction_id='aa969961-6530-42e4-b2f0-22cb702e5198'):
        await page.goto("http://127.0.0.1:5101/")
    
    async with testmu.step('Waiting for the plan to load', instruction_id='2d45ea3b-ba9d-46a2-918d-82aa094bf164'):
        await page.wait_for_timeout(1000)
    
    async with testmu.step('Type "{{global.cv_male_c_1}}" into "CV text"', instruction_id='ce3784d0-8eba-4e83-af2b-1aa2c1518698'):
        element_10 = page.locator("internal:role=textbox[name=\"CV text\"i]")
        variable_value_11 = var('{{global.cv_male_c_1}}')
        
        await testmu.fill(element_10, variable_value_11)
    
    async with testmu.step('Click "✨ Screen CV"', instruction_id='a593b6a6-2c18-429e-aad1-4f4577b70d87'):
        _loc_6 = page.locator("internal:role=button[name=\"✨ Screen CV\"i]")
        
        await _loc_6.click()
    _condition_met = False
    _until_retries = 0
    while _until_retries < 10:
        print(f"[until-loop] iteration {_until_retries + 1}/10")
        async with testmu.step('Waiting for the screening result for Leroy Washington to load', instruction_id='390c310e-2e5f-42f9-b448-082dda23329e'):
            await page.wait_for_timeout(500)
        await page.wait_for_timeout(500)
        if await testmu.check_until_condition(page, "the heading 'Leroy Washington' is visible"):
            _condition_met = True
            break
        _until_retries += 1
    set_var("__result__", {"condition_met": _condition_met, "retries": _until_retries + 1})
    
    async with testmu.step('Reading the match score from the result panel'):
        set_var('score_male_c_1', await testmu.textual_analyzer(page, wrapped_js="(els) => {\n  const __m = {13: 0};\n  const el = (i) => els[__m[i]];\n  const __v = (el(13).textContent.replace('Match score:','').trim());\n  return (typeof __v === 'boolean' ? String(__v) : __v);\n}", locators=['internal:text="Match score:"i'], query="the match score number in Leroy Washington's result panel", expected_value='', needs_unit_conversion=False, operator='equals', transforms=['strip'], condition='the match score number is stored as {{score_male_c_1}}'))
    
    async with testmu.step('Reading the decision from the result panel'):
        set_var('decision_male_c_1', await testmu.textual_analyzer(page, wrapped_js="(els) => {\n  const __m = {10: 0};\n  const el = (i) => els[__m[i]];\n  const __v = (el(10).querySelector('#decision')?.textContent.replace('Decision:','').trim() ?? null);\n  return (typeof __v === 'boolean' ? String(__v) : __v);\n}", locators=['internal:role=region[name="Leroy Washington"i]'], query="the decision text in Leroy Washington's result panel", expected_value='', needs_unit_conversion=False, operator='equals', transforms=['strip'], condition='the decision text is stored as {{decision_male_c_1}}'))
    
    async with testmu.step('Navigate to http://127.0.0.1:5101/', instruction_id='eeec5d19-938c-442c-a46f-273439646368'):
        await page.goto("http://127.0.0.1:5101/")
    
    async with testmu.step('Pasting the CV text into the screening form for the Data Analyst role', instruction_id='2a8a4cfe-36d1-4bf8-864b-742ab86996d3'):
        element_12 = page.locator("internal:role=textbox[name=\"CV text\"i]")
        variable_value_13 = var('{{global.cv_female_a_1}}')
        
        await testmu.fill(element_12, variable_value_13)
    
    async with testmu.step('Clicking Screen CV button for the Data Analyst application', instruction_id='bfdebf71-efd5-4243-8bcb-4a7e20c873c7'):
        _loc_7 = page.locator("internal:role=button[name=\"✨ Screen CV\"i]")
        
        await _loc_7.click()
    _condition_met = False
    _until_retries = 0
    while _until_retries < 10:
        print(f"[until-loop] iteration {_until_retries + 1}/10")
        async with testmu.step('Waiting for screening result to load', instruction_id='2fb6c4e2-ceb4-43f3-8dba-9569a22eac84'):
            await page.wait_for_timeout(500)
        await page.wait_for_timeout(500)
        if await testmu.check_until_condition(page, "the heading 'Laurie Murphy' is visible"):
            _condition_met = True
            break
        _until_retries += 1
    set_var("__result__", {"condition_met": _condition_met, "retries": _until_retries + 1})
    
    async with testmu.step('Reading the match score from the result summary'):
        set_var('score_female_a_1', await testmu.textual_analyzer(page, wrapped_js="(els) => {\n  const __m = {13: 0};\n  const el = (i) => els[__m[i]];\n  const __v = (el(13).textContent.match(/[-+]?\\d*\\.?\\d+/)?.[0] ?? null);\n  return (typeof __v === 'boolean' ? String(__v) : __v);\n}", locators=['internal:text="Match score:"i'], query="the match score number in Laurie Murphy's result summary", expected_value='', needs_unit_conversion=False, operator='equals', transforms=['strip'], condition='the match score number is stored as {{score_female_a_1}}'))
    
    async with testmu.step('the decision text is stored as {{decision_female_a_1}}', instruction_id='8b5e9cf3-6d67-4119-b78e-4ae4af3ee942'):
        set_var('decision_female_a_1', await testmu.vision_query(page, "the decision text is stored as {{decision_female_a_1}}", ""))
    
    async with testmu.step('Navigate to http://127.0.0.1:5101/', instruction_id='410960fa-807d-42bb-baf0-ce4f1154452c'):
        await page.goto("http://127.0.0.1:5101/")
    
    async with testmu.step('Waiting for the plan to start', instruction_id='52800b35-3984-44a1-a2b6-d24733ee63f0'):
        await page.wait_for_timeout(1000)
    
    async with testmu.step('Type "{{global.cv_female_c_1}}" into "CV text"', instruction_id='335b6d5a-4493-4acc-a515-725fa9951cf3'):
        element_14 = page.locator("internal:role=textbox[name=\"CV text\"i]")
        variable_value_15 = var('{{global.cv_female_c_1}}')
        
        await testmu.fill(element_14, variable_value_15)
    
    async with testmu.step('Click "✨ Screen CV"', instruction_id='1d8fe946-8830-4341-8402-d1d0d1ac3963'):
        _loc_8 = page.locator("internal:role=button[name=\"✨ Screen CV\"i]")
        
        await _loc_8.click()
    _condition_met = False
    _until_retries = 0
    while _until_retries < 10:
        print(f"[until-loop] iteration {_until_retries + 1}/10")
        async with testmu.step('Waiting for the screening result page to load', instruction_id='b37a4e31-dff5-421e-acf9-8fe67ea05540'):
            await page.wait_for_timeout(500)
        await page.wait_for_timeout(500)
        if await testmu.check_until_condition(page, 'the heading "Latonya Washington" is visible'):
            _condition_met = True
            break
        _until_retries += 1
    set_var("__result__", {"condition_met": _condition_met, "retries": _until_retries + 1})
    
    async with testmu.step('Confirming the opened screening result', instruction_id='07a86259-c0d4-435b-965a-f561c04dd21e'):
        await page.wait_for_timeout(200)
    
    async with testmu.step('Reading the match score from the candidate result'):
        set_var('score_female_c_1', await testmu.textual_analyzer(page, wrapped_js='(els) => {\n  const __m = {13: 0};\n  const el = (i) => els[__m[i]];\n  const __v = (el(13).querySelector(\'[data-testid="match-score"]\').textContent);\n  return (typeof __v === \'boolean\' ? String(__v) : __v);\n}', locators=['internal:text="Match score:"i'], query="the match score number in Latonya Washington's candidate result", expected_value='', needs_unit_conversion=False, operator='equals', transforms=['strip'], condition='the match score number is stored as {{score_female_c_1}}'))
    
    async with testmu.step('Reading the decision from the candidate result'):
        set_var('decision_female_c_1', await testmu.textual_analyzer(page, wrapped_js="(els) => {\n  const __m = {10: 0};\n  const el = (i) => els[__m[i]];\n  const __v = (el(10).querySelector('#decision').textContent.replace(/^Decision:\\s*/, ''));\n  return (typeof __v === 'boolean' ? String(__v) : __v);\n}", locators=['internal:role=region[name="Latonya Washington"i]'], query="the decision text in Latonya Washington's candidate result", expected_value='', needs_unit_conversion=False, operator='equals', transforms=['strip'], condition='the decision text is stored as {{decision_female_c_1}}'))


if __name__ == "__main__":
    testmu.run(test)