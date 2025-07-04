import re
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import json
import gc
import threading
import pyautogui

class Scraper:
    def __init__(self):
        self.email = "deepserp2025@gmail.com"
        self.password = "9ffERrdS5V"
        self.driver = None
        self.wait = None
        self.keep_awake = True
        self.awake_thread = None
        
        # Disable pyautogui failsafe to prevent accidental stops
        pyautogui.FAILSAFE = False
        
        self.countries = [
            "United Kingdom",
            "Ireland", 
            "United States",
            "Canada",
            "United Arab Emirates",
        ]
        self.levels = [
            "Postgraduate",
            "Undergraduate",
            "Foundation",
            "Pre-Sessional",
            "English Language",
            "Pre-Masters",
            "Research",
        ]
        self.subjects = [
            "Accounting and Finance",
            "Aerospace and Manufacturing Engineering",
            "Agriculture, Forestry and Food",
            "American Studies",
            "Anatomy and Physiology",
            "Anthropology",
            "Architecture",
            "Art",
            "Art History",
            "Biosciences",
            "Building and Town and Country Planning",
            "Business and Management",
            "Chemical Engineering",
            "Chemistry",
            "Civil Engineering",
            "Classics and Ancient History",
            "Computer Science",
            "Criminology",
            "Dentistry",
            "Design and Crafts",
            "Development Studies",
            "Drama and Dance",
            "Earth and Marine Science",
            "Economics",
            "Education",
            "Electrical Engineering",
            "English and Creative Writing",
            "English Literature",
            "Fashion and Textiles",
            "Film Production",
            "Food Science",
            "Forensic Science and Archaeology",
            "General Engineering",
            "Geography and Environmental Studies",
            "Health",
            "History",
            "Hospitality, Event Management and Tourism",
            "Hotel Management",
            "International Relations",
            "Journalism, Publishing and Public Relations",
            "Law",
            "Life Sciences",
            "Linguistics",
            "Management",
            "Marketing",
            "Material Engineering",
            "Mathematics",
            "MBA",
            "Mechanical Engineering",
            "Media Studies",
            "Medicine",
            "Music",
            "Nursing and Midwifery",
            "Other",
            "Pharmacy",
            "Philosophy",
            "Physics",
            "Physiotherapy",
            "Politics",
            "Psychology",
            "Religious Studies",
            "Social Policy and Administration",
            "Social Work",
            "Sociology",
            "Sports Science",
            "Supply Chain and Logistics",
            "Veterinary Science",
        ]

    def start_keep_awake(self):
        """Start a background thread to keep the computer awake"""
        def keep_system_awake():
            while self.keep_awake:
                try:
                    # Move mouse slightly to prevent sleep
                    current_pos = pyautogui.position()
                    pyautogui.moveTo(current_pos.x + 1, current_pos.y + 1, duration=0.1)
                    pyautogui.moveTo(current_pos.x, current_pos.y, duration=0.1)
                    
                    # Press a harmless key combination (Shift key)
                    pyautogui.press('shift')
                    
                    print("💤 Keeping system awake...")
                    time.sleep(60)  # Keep awake every minute
                except Exception as e:
                    print(f"⚠️ Keep awake error: {e}")
                    time.sleep(60)
        
        self.awake_thread = threading.Thread(target=keep_system_awake, daemon=True)
        self.awake_thread.start()
        print("🔋 Keep awake thread started")

    def stop_keep_awake(self):
        """Stop the keep awake thread"""
        self.keep_awake = False
        print("🔋 Keep awake thread stopped")

    def refresh_browser_session(self):
        """Refresh the browser session to prevent timeouts"""
        try:
            print("🔄 Refreshing browser session...")
            
            # Get current URL
            current_url = self.driver.current_url
            
            # Refresh the page
            self.driver.refresh()
            
            # Wait for page to load
            time.sleep(3)
            
            # If we're not on the course search page, navigate back
            if "course-search" not in current_url:
                self.visit_course_search()
                self.wait_for_splash_screen_to_disappear()
            
            print("✅ Browser session refreshed")
            
        except Exception as e:
            print(f"⚠️ Error refreshing browser session: {e}")

    def safe_element_interaction(self, action_func, max_retries=3):
        """Safely interact with elements with retries and session refresh"""
        for attempt in range(max_retries):
            try:
                return action_func()
            except Exception as e:
                print(f"⚠️ Element interaction failed (attempt {attempt + 1}/{max_retries}): {e}")
                
                if attempt < max_retries - 1:
                    # Wait a bit
                    time.sleep(2)
                    
                    # Try to refresh session if it's the last retry before giving up
                    if attempt == max_retries - 2:
                        self.refresh_browser_session()
                        time.sleep(3)
                else:
                    raise e

    def visit_login(self):
        self.driver.get("https://si-applications.com/auth/login")
        self.wait.until(
            EC.visibility_of_element_located(
                (By.CSS_SELECTOR, '[formcontrolname="UserName"]')
            )
        )

    def clean_up(self):
        self.stop_keep_awake()
        if self.driver:
            self.driver.quit()

    def login(self):
        self.visit_login()
        email_input = self.driver.find_element(
            By.CSS_SELECTOR, '[formcontrolname="UserName"]'
        )
        password_input = self.driver.find_element(
            By.CSS_SELECTOR, '[formcontrolname="password"]'
        )
        login_button = self.driver.find_element(
            By.XPATH, '//button[normalize-space()="Login"]'
        )
        email_input.clear()
        email_input.send_keys(self.email)
        password_input.clear()
        password_input.send_keys(self.password)
        login_button.click()

    def visit_course_search(self):
        self.driver.get("https://si-applications.com/course-search")

    def wait_for_splash_screen_to_disappear(self):
        self.wait.until(
            EC.invisibility_of_element_located((By.ID, "vex-splash-screen"))
        )

    def select_country(self, country):
        def _select_country():
            self.wait_for_splash_screen_to_disappear()
            ActionChains(self.driver).send_keys(Keys.ESCAPE).perform()
            country_select = self.wait.until(
                EC.element_to_be_clickable((By.ID, "mat-select-0"))
            )
            country_select.click()
            option = self.wait.until(
                EC.element_to_be_clickable(
                    (
                        By.XPATH,
                        f"//mat-option[not(@aria-disabled='true')]//span[contains(text(), '{country}')]",
                    )
                )
            )
            option.click()
        
        return self.safe_element_interaction(_select_country)

    def select_level(self, level):
        def _select_level():
            level_select = self.wait.until(
                EC.element_to_be_clickable(
                    (
                        By.XPATH,
                        "//mat-select[contains(@class, 'mat-select') and @placeholder='Level']",
                    )
                )
            )
            level_select.click()
            option = self.wait.until(
                EC.element_to_be_clickable(
                    (By.XPATH, f"//mat-option//span[normalize-space(text())='{level}']")
                )
            )
            option.click()
            ActionChains(self.driver).send_keys(Keys.ESCAPE).perform()
        
        return self.safe_element_interaction(_select_level)

    def select_subject(self, subject):
        def _select_subject():
            self.wait_for_splash_screen_to_disappear()
            ActionChains(self.driver).send_keys(Keys.ESCAPE).perform()
            subject_select = self.wait.until(
                EC.element_to_be_clickable(
                    (
                        By.XPATH,
                        "//mat-select[.//mat-select-trigger[normalize-space(text())='Subject'] or .//span[contains(@class, 'mat-select-placeholder') and normalize-space(text())='Subject']]",
                    )
                )
            )
            subject_select.click()
            option = self.wait.until(
                EC.element_to_be_clickable(
                    (By.XPATH, f"//mat-option//span[normalize-space(text())='{subject}']")
                )
            )
            option.click()
        
        return self.safe_element_interaction(_select_subject)

    def set_all_location(self):
        def _set_all_location():
            self.wait_for_splash_screen_to_disappear()
            location_select = self.driver.find_element(
                By.XPATH, '//mat-select[@placeholder="Location"]'
            )
            location_select.click()
            checkbox = self.wait.until(
                EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, ".mat-checkbox-inner-container")
                )
            )
            checkbox.click()
        
        return self.safe_element_interaction(_set_all_location)

    def set_all_university(self):
        def _set_all_university():
            self.wait_for_splash_screen_to_disappear()
            ActionChains(self.driver).send_keys(Keys.ESCAPE).perform()
            time.sleep(1)
            for attempt in range(3):
                dropdown = self.wait.until(
                    EC.element_to_be_clickable(
                        (By.XPATH, "//mat-select[@placeholder='University']")
                    )
                )
                dropdown.click()
                try:
                    checkbox = WebDriverWait(self.driver, 2).until(
                        EC.presence_of_element_located((By.ID, "allChekedBox"))
                    )
                    break
                except:
                    print(f"Dropdown didn't open, retry {attempt + 1}/3")
                    if attempt == 2:
                        raise Exception("Failed to open dropdown")

            is_selected = self.driver.execute_script(
                """
                const checkbox = document.getElementById('allChekedBox');
                return checkbox && (checkbox.checked || checkbox.classList.contains('mat-checkbox-checked') ||
                        checkbox.getAttribute('aria-checked') === 'true');
            """
            )

            if not is_selected:
                for attempt in range(3):
                    checkbox = self.wait.until(
                        EC.element_to_be_clickable((By.ID, "allChekedBox"))
                    )
                    checkbox.click()
                    time.sleep(1)
        
        return self.safe_element_interaction(_set_all_university)

    def set_any_intake(self):
        def _set_any_intake():
            ActionChains(self.driver).send_keys(Keys.ESCAPE).perform()
            intake_selection = self.wait.until(
                EC.element_to_be_clickable((By.ID, "mat-select-10"))
            )
            intake_selection.click()
            checkbox = self.wait.until(EC.element_to_be_clickable((By.ID, "mat-option-0")))
            checkbox.click()
            ActionChains(self.driver).send_keys(Keys.ESCAPE).perform()
        
        return self.safe_element_interaction(_set_any_intake)

    def set_any_year(self):
        def _set_any_year():
            year_select = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//mat-select[@placeholder='Year']"))
            )
            year_select.click()
            time.sleep(0.1)
            checkbox = self.wait.until(
                EC.element_to_be_clickable(
                    (
                        By.XPATH,
                        "//mat-option[contains(.//span[@class='mat-option-text'], 'Any')]",
                    )
                )
            )
            checkbox.click()
        
        return self.safe_element_interaction(_set_any_year)

    def apply_filter(self):
        search_button = self.driver.find_elements(
            By.CSS_SELECTOR, "button[mat-flat-button][color='primary']"
        )[1]
        self.driver.execute_script(
            """
            var splash = document.getElementById('vex-splash-screen');
            if (splash) splash.remove();
            arguments[0].click();
        """,
            search_button,
        )

    def check_no_data_found(self):
        """Check if 'No Data Found' message is displayed"""
        try:
            time.sleep(3)
            
            no_data_selectors = [
                'div.dataNotFound.ng-star-inserted',
                'div.dataNotFound',
                '.dataNotFound',
                '//div[contains(@class, "dataNotFound")]',
                '//p[contains(@class, "nodata")]',
                '//span[contains(text(), "No Data Found")]'
            ]
            
            for selector in no_data_selectors:
                try:
                    if selector.startswith('//'):
                        element = self.driver.find_element(By.XPATH, selector)
                    else:
                        element = self.driver.find_element(By.CSS_SELECTOR, selector)
                    
                    if element.is_displayed():
                        print("  ❌ No Data Found message detected")
                        return True
                except:
                    continue
            
            try:
                no_data_element = WebDriverWait(self.driver, 2).until(
                    EC.presence_of_element_located(
                        (By.XPATH, "//span[contains(text(), 'No Data Found Regarding Your Search')]")
                    )
                )
                if no_data_element.is_displayed():
                    print("  ❌ No Data Found message detected by text")
                    return True
            except:
                pass
            
            print("  ✅ Data found - proceeding with scraping")
            return False
            
        except Exception as e:
            print(f"  ⚠️ Error checking for no data message: {e}")
            return False

    def get_course_count_info(self):
        """Get the course count information from the page"""
        try:
            # Wait for the course count element to appear
            course_count_element = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "p.courseCount.text-sm.font-medium.text-customTextColor")
                )
            )
            
            if course_count_element.is_displayed():
                course_count_text = course_count_element.text
                print(f"  📊 {course_count_text}")
                
                # Extract numbers using regex
                import re
                numbers = re.findall(r'\d+', course_count_text)
                
                if len(numbers) >= 2:
                    total_courses = int(numbers[0])
                    total_schools = int(numbers[1])
                    
                    return {
                        "total_courses": total_courses,
                        "total_schools": total_schools,
                        "text": course_count_text,
                        "found": True
                    }
                else:
                    return {"found": False, "text": course_count_text}
            
        except Exception as e:
            print(f"  ⚠️ Could not find course count element: {e}")
            return {"found": False}

    def validate_all_courses_expanded(self, expected_courses, expected_schools):
        """Validate that all courses are properly expanded"""
        try:
            # Get page source and parse
            html = self.driver.page_source
            soup = BeautifulSoup(html, 'html.parser')
            
            # Count actual course links found
            course_links = soup.find_all('a', href=lambda x: x and '/course-details/' in x)
            actual_courses = len(course_links)
            
            # Count university cards
            university_cards = soup.find_all('mat-card', style=lambda x: x and 'border: 2px solid rgb(11, 101, 253)' in x)
            actual_schools = len(university_cards)
            
            print(f"  🔍 Expected: {expected_courses} courses, {expected_schools} schools")
            print(f"  🔍 Found: {actual_courses} courses, {actual_schools} schools")
            
            # Check if we have the expected number of courses (allow some tolerance)
            courses_match = abs(actual_courses - expected_courses) <= 2  # Allow 2 course difference
            schools_match = abs(actual_schools - expected_schools) <= 1   # Allow 1 school difference
            
            if courses_match and schools_match:
                print(f"  ✅ All courses properly expanded and validated")
                return True
            else:
                print(f"  ⚠️ Course count mismatch - may need re-expansion")
                return False
                
        except Exception as e:
            print(f"  ❌ Error validating course expansion: {e}")
            return False

    def expand_info(self):
        if self.check_no_data_found():
            print("  🚫 Skipping expand_info - no data found")
            return False
        
        # Get the expected course count first
        course_info = self.get_course_count_info()
        if not course_info["found"]:
            print("  ⚠️ Could not get course count - proceeding anyway")
            expected_courses = 0
            expected_schools = 0
        else:
            expected_courses = course_info["total_courses"]
            expected_schools = course_info["total_schools"]
        
        # If no courses expected, skip expansion
        if expected_courses == 0:
            print("  📝 No courses to expand")
            return True
        
        try:
            self.wait.until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//span[text()='View Courses']/parent::p")
                )
            )
        except:
            print("  ⚠️ No 'View Courses' buttons found - might be no data or already expanded")
            # Still validate if courses are already expanded
            if expected_courses > 0:
                return self.validate_all_courses_expanded(expected_courses, expected_schools)
            return True
        
        # Expand all courses
        expansion_attempts = 0
        max_expansion_attempts = 3
        
        while expansion_attempts < max_expansion_attempts:
            expansion_attempts += 1
            print(f"  🔄 Expansion attempt {expansion_attempts}/{max_expansion_attempts}")
            
            # Click all "View Courses" buttons
            buttons_clicked = 0
            while True:
                try:
                    self.wait_for_splash_screen_to_disappear()
                    expander = WebDriverWait(self.driver, 4).until(
                        EC.element_to_be_clickable(
                            (By.XPATH, "//span[text()='View Courses']/parent::p")
                        )
                    )
                    expander.click()
                    buttons_clicked += 1
                    time.sleep(0.5)  # Small delay between clicks
                except:
                    break
        
            print(f"    Clicked {buttons_clicked} 'View Courses' buttons")
        
            # Wait a bit for expansion to complete
            time.sleep(2)
        
            # Validate that all courses are now expanded
            if self.validate_all_courses_expanded(expected_courses, expected_schools):
                print(f"  ✅ All courses successfully expanded after {expansion_attempts} attempts")
                return True
            else:
                print(f"  ⚠️ Not all courses expanded, trying again...")
                time.sleep(1)
    
        print(f"  ❌ Failed to expand all courses after {max_expansion_attempts} attempts")
        print(f"  🤷 Proceeding with partial data...")
        return True  # Continue anyway with whatever we have

    def scroll_to_top(self):
        self.wait.until(
            EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='Example icon button with a delete icon']"))
        ).click()

    def scrape_courses_comprehensive(self):
        """Comprehensive scraping with memory optimization"""
        print("Starting comprehensive course scraping...")
        
        # Get page source - NO MORE CLEARING BROWSER DATA
        html = self.driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        
        selectors = [
            'div.mt-2.px-5.viewCourses.ng-star-inserted',
            'div.viewCourses',
            'mat-card[style*="border: 2px solid rgb(11, 101, 253)"]'
        ]
        
        university_containers = []
        for selector in selectors:
            containers = soup.select(selector)
            if containers:
                university_containers = containers
                print(f"Found {len(containers)} containers using selector: {selector}")
                break
        
        if not university_containers:
            university_containers = soup.find_all('mat-card', style=re.compile(r'border.*rgb$$11,\s*101,\s*253$$'))
            print(f"Fallback: Found {len(university_containers)} mat-cards with blue border")
        
        courses = []
        
        for i, container in enumerate(university_containers):
            try:
                university_info = self.extract_university_info(container)
                course_links = container.find_all('a', href=lambda x: x and '/course-details/' in x)
                
                for j, course_link in enumerate(course_links):
                    course_section = course_link.find_parent('div', style=lambda x: x and 'border: 2px solid #EDEDED' in x)
                    if not course_section:
                        course_section = course_link.find_parent('div', class_='ng-star-inserted')
                
                    if course_section:
                        course_data = self.extract_course_info(course_section, university_info)
                        courses.append(course_data)
                    else:
                        course_data = self.extract_course_info(container, university_info)
                        course_data['course_name'] = course_link.get_text(strip=True)
                        course_data['course_url'] = course_link.get('href')
                        courses.append(course_data)
                        
            except Exception as e:
                print(f"Error processing container {i+1}: {e}")
                continue
        
        # Clear soup from memory
        del soup
        del html
        gc.collect()
        
        print(f"Scraping complete! Total courses found: {len(courses)}")
        return courses

    def extract_university_info(self, university_card):
        """Extract university information from the card"""
        university_info = {
            "university": "",
            "location": "",
            "ranking": ""
        }
        
        try:
            uni_selectors = [
                'p.primary.text-base.font-semibold',
                'p[style*="color: #3F4254"]'
            ]
            
            for selector in uni_selectors:
                uni_elem = university_card.select_one(selector)
                if uni_elem:
                    university_info['university'] = uni_elem.get_text(strip=True)
                    break
            
            location_parts = []
            place_icon = university_card.find('mat-icon', string='place')
            if place_icon:
                location_container = place_icon.find_parent('div', class_='mt-2')
                if location_container:
                    location_divs = location_container.find_all('div', recursive=False)
                    for div in location_divs:
                        text = div.get_text(strip=True)
                        if (text and text != '|' and len(text) > 1 and
                            not any(icon in text.lower() for icon in ['place', 'military_tech', 'mat-icon'])):
                            location_parts.append(text)
            
            university_info['location'] = ' | '.join(location_parts)
            
            military_icon = university_card.find('mat-icon', string='military_tech')
            if military_icon:
                ranking_div = military_icon.find_next_sibling('div', class_='text-base')
                if ranking_div:
                    university_info['ranking'] = ranking_div.get_text(strip=True)
                    
        except Exception as e:
            print(f"Error extracting university info: {e}")
        
        return university_info

    def extract_course_info(self, course_section, university_info):
        """Extract individual course information with proper selectors"""
        course_data = {
            "university": university_info['university'],
            "location": university_info['location'],
            "ranking": university_info['ranking'],
            "course_name": "",
            "course_url": "",
            "degree": "",
            "intake": "",
            "tuition_fees": "",
            "duration": "",
            "application_fee": "",
            "scholarships_available": False
        }
        
        try:
            course_link = course_section.find('a', href=lambda x: x and '/course-details/' in x)
            if course_link:
                course_data['course_name'] = course_link.get_text(strip=True)
                course_data['course_url'] = course_link.get('href')

            detail_cards = course_section.find_all('mat-card', class_=lambda x: x and 'h-20' in x)

            for detail_card in detail_cards:
                try:
                    title_elem = detail_card.find('p', class_=lambda x: x and 'text-xs' in x and 'font-medium' in x)
                    value_elem = detail_card.find('mat-card-subtitle', class_=lambda x: x and 'text-sm' in x and 'font-semibold' in x)
                    
                    if not value_elem:
                        value_elem = detail_card.find('p', class_=lambda x: x and 'text-sm' in x and 'font-semibold' in x)

                    if title_elem and value_elem:
                        title = title_elem.get_text(strip=True).lower()
                        value = value_elem.get_text(strip=True)

                        if 'degree' in title:
                            course_data['degree'] = value
                        elif 'intake' in title:
                            course_data['intake'] = value
                        elif 'tuition' in title and 'fee' in title:
                            course_data['tuition_fees'] = value
                        elif 'duration' in title:
                            course_data['duration'] = value
                        elif 'application' in title and 'fee' in title:
                            course_data['application_fee'] = value

                except Exception as e:
                    continue

            scholarship_links = course_section.find_all(['a', 'span'], class_=lambda x: x and 'underline' in x)
            for link in scholarship_links:
                if 'scholarship' in link.get_text().lower():
                    course_data['scholarships_available'] = True
                    break

            if not course_data['scholarships_available']:
                scholarship_text = course_section.get_text().lower()
                if 'scholarship' in scholarship_text:
                    course_data['scholarships_available'] = True

        except Exception as e:
            print(f"Error extracting course info: {e}")

        return course_data

    def save_progress(self, all_courses, fails, no_data_combinations):
        """Save progress to files"""
        with open("courses.json", "w") as f:
            json.dump(all_courses, f, indent=4)
        
        with open("fails.json", "w") as f:
            json.dump(fails, f, indent=4)
        
        with open("no_data_combinations.json", "w") as f:
            json.dump(no_data_combinations, f, indent=4)

    def scrape_courses(self):
        self.visit_course_search()
        self.wait_for_splash_screen_to_disappear()
        
        all_courses = []
        fails = []
        no_data_combinations = []
        
        total_combinations = len(self.countries) * len(self.levels) * len(self.subjects)
        current_combination = 0
        
        for country in self.countries:
            self.select_country(country)
            self.wait_for_splash_screen_to_disappear()
            self.set_all_location()
            self.set_any_intake()
            self.set_any_year()
            
            for level in self.levels:
                print(f"\n🎓 Starting level: {level}")
                self.select_level(level)
                self.set_all_university()
                
                for subject in self.subjects:
                    current_combination += 1
                    progress = (current_combination / total_combinations) * 100
                    
                    print(f"\n🔍 [{progress:.1f}%] Searching: {country} | {level} | {subject}")
                    
                    for attempt in range(3):
                        try:
                            self.select_subject(subject)
                            self.apply_filter()
                            
                            # Wait for results to load
                            time.sleep(3)
                            
                            if self.check_no_data_found():
                                print(f"  📝 No data found for: {country} | {level} | {subject}")
                                no_data_combinations.append({
                                    "country": country,
                                    "level": level,
                                    "subject": subject,
                                    "reason": "No Data Found"
                                })
                                break
                            
                            # Get course count info for validation
                            course_info = self.get_course_count_info()
                            
                            expand_success = self.expand_info()
                            if not expand_success:
                                print(f"  ⚠️ Could not expand courses for: {country} | {level} | {subject}")
                                break
                            
                            courses = self.scrape_courses_comprehensive()
                            all_courses.extend(courses)
                            
                            # Validate scraped count against expected count
                            if course_info["found"]:
                                expected = course_info["total_courses"]
                                actual = len(courses)
                                if abs(actual - expected) <= 2:  # Allow small tolerance
                                    print(f"  ✅ Found {actual}/{expected} courses (validated)")
                                else:
                                    print(f"  ⚠️ Found {actual}/{expected} courses (count mismatch)")
                            else:
                                print(f"  ✅ Found {len(courses)} courses")
                            
                            self.scroll_to_top()
                            time.sleep(2)
                            break
                            
                        except Exception as e:
                            print(f"  ❌ Attempt {attempt + 1} failed: {e}")
                            if attempt == 2:
                                fails.append({
                                    "country": country,
                                    "level": level,
                                    "subject": subject,
                                    "error": str(e)
                                })
                    
                    # Save progress every 10 combinations
                    if current_combination % 10 == 0:
                        self.save_progress(all_courses, fails, no_data_combinations)
                        print(f"💾 Progress saved at {progress:.1f}%")

        # Final save
        self.save_progress(all_courses, fails, no_data_combinations)
        
        print(f"\n📊 Final Results:")
        print(f"  Total courses found: {len(all_courses)}")
        print(f"  Failed combinations: {len(fails)}")
        print(f"  No data combinations: {len(no_data_combinations)}")

    def run(self):
        # Start keep awake functionality
        self.start_keep_awake()
        
        # Back to simple driver creation like before
        self.driver = webdriver.Chrome()
        self.wait = WebDriverWait(self.driver, 100)
        
        try:
            self.login()
            self.wait_for_splash_screen_to_disappear()
            self.scrape_courses()
        finally:
            self.clean_up()

if __name__ == "__main__":
    scraper = Scraper()
    scraper.run()
