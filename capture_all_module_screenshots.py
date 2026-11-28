import os
import time
from playwright.sync_api import sync_playwright

BASE_URL = "https://ai-career-companion-mg65.onrender.com"
OUTPUT_DIR = "module_screenshots"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def capture_screenshots():
    print("Launching Playwright Edge...")
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="msedge", headless=True)
        context = browser.new_context(viewport={"width": 1366, "height": 820})
        page = context.new_page()

        # 1. Landing Page
        print("Capturing Landing Page...")
        try:
            page.goto(f"{BASE_URL}/", timeout=60000)
            page.wait_for_timeout(3000)
            page.screenshot(path=os.path.join(OUTPUT_DIR, "landing_page.png"))
            print("Captured landing_page.png")
        except Exception as e:
            print("Error on landing:", e)

        # 2. Login Page
        print("Capturing Login Page...")
        try:
            page.goto(f"{BASE_URL}/login", timeout=30000)
            page.wait_for_timeout(2000)
            page.screenshot(path=os.path.join(OUTPUT_DIR, "auth_login.png"))
            print("Captured auth_login.png")

            # Click Demo fill button or fill inputs
            demo_btn = page.query_selector(".btn-demo-quickfill")
            if demo_btn:
                print("Clicking demo quickfill button...")
                demo_btn.click()
                page.wait_for_timeout(4000)
            else:
                print("Filling credentials manually...")
                page.fill('input[type="email"]', "arun.student@example.com")
                page.fill('input[type="password"]', "Student123!")
                page.click('button[type="submit"]')
                page.wait_for_timeout(4000)
        except Exception as e:
            print("Error on login:", e)

        # Module Routes
        routes = [
            ("module_1_profile.png", "/profile", "Module 1: Student Profile"),
            ("module_2_resume_parser.png", "/resume-parser", "Module 2: Resume Parser"),
            ("module_3_knowledge_base.png", "/knowledge-base", "Module 3: Knowledge Base"),
            ("module_4_job_matching.png", "/job-matching", "Module 4: Job Matching"),
            ("module_5_skill_gap.png", "/skill-gap", "Module 5: Skill Gap"),
            ("module_6_cover_letter.png", "/cover-letter", "Module 6: Cover Letter Customizer"),
            ("module_7_interview_prep.png", "/interview-prep", "Module 7: Interview Prep"),
            ("module_8_career_assistant.png", "/career-assistant", "Module 8: Career Assistant"),
        ]

        for filename, route, label in routes:
            print(f"Navigating to {label} ({route})...")
            try:
                page.goto(f"{BASE_URL}{route}", timeout=30000)
                page.wait_for_timeout(3500)
                # If on resume parser, click sample demo resume button if present
                if route == "/resume-parser":
                    sample_btn = page.query_selector(".demo-pill") or page.query_selector(".btn-showcase-demo")
                    if sample_btn:
                        print("  Clicking sample demo resume...")
                        sample_btn.click()
                        page.wait_for_timeout(4000)

                target_path = os.path.join(OUTPUT_DIR, filename)
                page.screenshot(path=target_path)
                print(f"  Successfully captured: {filename} ({os.path.getsize(target_path)} bytes)")
            except Exception as e:
                print(f"  Error capturing {label}:", e)

        browser.close()
        print("All screenshots successfully captured!")

if __name__ == "__main__":
    capture_screenshots()
