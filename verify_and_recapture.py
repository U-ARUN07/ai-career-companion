import os
import time
from playwright.sync_api import sync_playwright

BASE_URL = "https://ai-career-companion-mg65.onrender.com"
OUTPUT_DIR = "module_screenshots"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def run():
    print("Launching Playwright Edge...")
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="msedge", headless=True)
        context = browser.new_context(viewport={"width": 1366, "height": 840})
        page = context.new_page()

        # Step 1: Login
        print("Navigating to login page...")
        page.goto(f"{BASE_URL}/login", timeout=60000)
        page.wait_for_timeout(3000)

        # Click demo quickfill button
        demo_btn = page.query_selector(".btn-demo-quickfill")
        if demo_btn:
            print("Clicking demo quickfill button...")
            demo_btn.click()
            page.wait_for_timeout(5000)
        else:
            print("Filling form directly...")
            page.fill('input[type="email"]', "arun.student@example.com")
            page.fill('input[type="password"]', "Student123!")
            page.click('button[type="submit"]')
            page.wait_for_timeout(5000)

        print("Current URL after login:", page.url)

        # Module 1: Student Profile
        print("Capturing Module 1: Student Profile (/profile)...")
        page.goto(f"{BASE_URL}/profile", timeout=30000)
        page.wait_for_timeout(4000)
        page.screenshot(path=os.path.join(OUTPUT_DIR, "module_1_profile.png"))
        print(f"  URL: {page.url} | Title: {page.title()}")

        # Module 2: Resume Parser (Load Sample Resume)
        print("Capturing Module 2: Resume Parser (/resume-parser)...")
        page.goto(f"{BASE_URL}/resume-parser", timeout=30000)
        page.wait_for_timeout(4000)
        sample_btn = page.query_selector(".demo-pill") or page.query_selector(".btn-showcase-demo")
        if sample_btn:
            print("  Clicking 'Load Sample Resume' button...")
            sample_btn.click()
            page.wait_for_timeout(5000)
        page.screenshot(path=os.path.join(OUTPUT_DIR, "module_2_resume_parser.png"))
        print(f"  URL: {page.url} | Title: {page.title()}")

        # Module 3: Knowledge Base
        print("Capturing Module 3: Knowledge Base (/knowledge-base)...")
        page.goto(f"{BASE_URL}/knowledge-base", timeout=30000)
        page.wait_for_timeout(4000)
        page.screenshot(path=os.path.join(OUTPUT_DIR, "module_3_knowledge_base.png"))
        print(f"  URL: {page.url} | Title: {page.title()}")

        # Module 4: Job Matching
        print("Capturing Module 4: Job Matching (/job-matching)...")
        page.goto(f"{BASE_URL}/job-matching", timeout=30000)
        page.wait_for_timeout(4000)
        # Select first internship or calculate if button available
        score_btn = page.query_selector(".btn-score, .btn-match, button:has-text('Score'), button:has-text('Match')")
        if score_btn:
            try:
                score_btn.click()
                page.wait_for_timeout(3000)
            except:
                pass
        page.screenshot(path=os.path.join(OUTPUT_DIR, "module_4_job_matching.png"))
        print(f"  URL: {page.url} | Title: {page.title()}")

        # Module 5: Skill Gap
        print("Capturing Module 5: Skill Gap (/skill-gap)...")
        page.goto(f"{BASE_URL}/skill-gap", timeout=30000)
        page.wait_for_timeout(4000)
        analyze_btn = page.query_selector(".btn-analyze, button:has-text('Analyze'), button:has-text('Skill Gap')")
        if analyze_btn:
            try:
                analyze_btn.click()
                page.wait_for_timeout(3000)
            except:
                pass
        page.screenshot(path=os.path.join(OUTPUT_DIR, "module_5_skill_gap.png"))
        print(f"  URL: {page.url} | Title: {page.title()}")

        # Module 6: Resume & Cover Letter Customizer (/customizer)
        print("Capturing Module 6: Customizer (/customizer)...")
        page.goto(f"{BASE_URL}/customizer", timeout=30000)
        page.wait_for_timeout(4000)
        page.screenshot(path=os.path.join(OUTPUT_DIR, "module_6_cover_letter.png"))
        print(f"  URL: {page.url} | Title: {page.title()}")

        # Module 7: Interview Prep
        print("Capturing Module 7: Interview Prep (/interview-prep)...")
        page.goto(f"{BASE_URL}/interview-prep", timeout=30000)
        page.wait_for_timeout(4000)
        gen_btn = page.query_selector("button:has-text('Generate Questions'), .btn-generate")
        if gen_btn:
            try:
                gen_btn.click()
                page.wait_for_timeout(3000)
            except:
                pass
        page.screenshot(path=os.path.join(OUTPUT_DIR, "module_7_interview_prep.png"))
        print(f"  URL: {page.url} | Title: {page.title()}")

        # Module 8: Career Assistant
        print("Capturing Module 8: Career Assistant (/career-assistant)...")
        page.goto(f"{BASE_URL}/career-assistant", timeout=30000)
        page.wait_for_timeout(4000)
        page.screenshot(path=os.path.join(OUTPUT_DIR, "module_8_career_assistant.png"))
        print(f"  URL: {page.url} | Title: {page.title()}")

        browser.close()
        print("All module screenshots refreshed successfully!")

if __name__ == "__main__":
    run()
