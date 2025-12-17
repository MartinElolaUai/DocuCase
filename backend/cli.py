"""
CLI tool for DocuDash operations.
"""
import click
import json
import os
import time
from pathlib import Path
from typing import Optional, List, Dict
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import Application


def ensure_output_dir():
    """Create output directory if it doesn't exist."""
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    return output_dir


def normalize_name(name: str) -> str:
    """Normalize application names for comparison (lowercase, no spaces)."""
    return "".join(name.lower().split()) if name else ""


def parse_bool(value: str) -> bool:
    """Parse string boolean value to bool."""
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.lower() in ('true', '1', 'yes', 'on')
    return bool(value)


def init_selenium_driver(headed: bool = True, timeout: int = 60) -> webdriver.Chrome:
    """Initialize Selenium WebDriver with Chrome."""
    chrome_options = Options()
    
    if not headed:
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
    
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    import os
    import shutil
    import glob
    
    try:
        print("  📥 Downloading/checking ChromeDriver...")
        # Get the directory where ChromeDriver should be
        driver_dir = ChromeDriverManager().install()
        
        # WebDriver Manager sometimes returns a file path instead of directory
        # We need to find the actual chromedriver.exe
        if os.path.isfile(driver_dir):
            driver_dir = os.path.dirname(driver_dir)
        
        # Search for chromedriver.exe in the directory and subdirectories
        possible_paths = [
            os.path.join(driver_dir, "chromedriver.exe"),
            os.path.join(driver_dir, "chromedriver"),
        ]
        
        # Also search in subdirectories
        for root, dirs, files in os.walk(driver_dir):
            for file in files:
                if file == "chromedriver.exe" or (file == "chromedriver" and os.name != 'nt'):
                    possible_paths.append(os.path.join(root, file))
        
        driver_path = None
        for path in possible_paths:
            if os.path.exists(path) and os.path.isfile(path):
                # Verify it's actually an executable (not a text file)
                if path.endswith('.exe') or (os.path.getsize(path) > 1000000):  # Executable should be > 1MB
                    driver_path = path
                    break
        
        if not driver_path:
            raise FileNotFoundError(
                f"Could not find chromedriver.exe in {driver_dir}. "
                "Try clearing cache: python -c \"import shutil, os; shutil.rmtree(os.path.expanduser('~/.wdm'), ignore_errors=True)\""
            )
        
        print(f"  ✅ ChromeDriver found at: {driver_path}")
        
        service = Service(driver_path)
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.implicitly_wait(timeout)
        driver.set_page_load_timeout(timeout)
        
        print("  ✅ Browser initialized successfully")
        return driver
    except OSError as e:
        if "[WinError 193]" in str(e):
            print(f"  ❌ ChromeDriver compatibility error: {e}")
            print("  🔄 Attempting to clear cache and re-download...")
            cache_dir = os.path.expanduser("~/.wdm")
            if os.path.exists(cache_dir):
                shutil.rmtree(cache_dir, ignore_errors=True)
                print("  ✅ Cache cleared")
            
            try:
                print("  📥 Re-downloading ChromeDriver...")
                driver_dir = ChromeDriverManager().install()
                if os.path.isfile(driver_dir):
                    driver_dir = os.path.dirname(driver_dir)
                
                # Find chromedriver.exe
                for root, dirs, files in os.walk(driver_dir):
                    for file in files:
                        if file == "chromedriver.exe":
                            driver_path = os.path.join(root, file)
                            break
                    if driver_path:
                        break
                
                if not driver_path:
                    raise FileNotFoundError("Could not find chromedriver.exe after re-download")
                
                print(f"  ✅ ChromeDriver re-downloaded at: {driver_path}")
                
                service = Service(driver_path)
                driver = webdriver.Chrome(service=service, options=chrome_options)
                driver.implicitly_wait(timeout)
                driver.set_page_load_timeout(timeout)
                
                print("  ✅ Browser initialized successfully after retry")
                return driver
            except Exception as retry_error:
                print(f"  ❌ Retry also failed: {retry_error}")
                raise
        else:
            raise
    except Exception as e:
        print(f"  ❌ Error initializing ChromeDriver: {e}")
        print("\n  💡 Troubleshooting tips:")
        print("     1. Make sure Chrome browser is installed")
        print("     2. Try clearing WebDriver Manager cache:")
        print("        python -c \"import shutil, os; shutil.rmtree(os.path.expanduser('~/.wdm'), ignore_errors=True)\"")
        print("     3. Or manually download ChromeDriver from:")
        print("        https://chromedriver.chromium.org/")
        raise


def manual_google_login(driver: webdriver.Chrome) -> None:
    """Handle manual Google login with user interaction."""
    print("\n" + "="*60)
    print("🔐 MANUAL LOGIN REQUIRED")
    print("="*60)
    print("\nThe browser will open. Please:")
    print("1. Log in with your Google account")
    print("2. Complete any authentication steps")
    print("3. Return here and press Enter to continue")
    print("\n" + "="*60 + "\n")
    
    input("Press Enter after you've logged in via Google...")
    print("✅ Login confirmed. Continuing with scraping...\n")


def scrape_app_id(driver: webdriver.Chrome, app_name: str, delay: float = 0.5) -> Optional[str]:
    """
    Scrape app_id from the disponibilidad page for a given app name.
    
    Args:
        driver: Selenium WebDriver instance
        app_name: Name of the application to search for
        delay: Delay between requests in seconds
    
    Returns:
        app_id if found, None otherwise
    """
    try:
        url = "https://pruebasdisponibilidad.cloud.osde.ar/"
        print(f"  📍 Navigating to: {url}")
        driver.get(url)
        
        # Wait for page to load
        time.sleep(2)
        
        # Find all h2 elements with the specific class
        try:
            h2_elements = driver.find_elements(By.CSS_SELECTOR, "h2.text-xl.font-semibold.mb-4.text-white")
        except NoSuchElementException:
            print(f"  ⚠️  No h2 elements found with expected class")
            return None
        
        print(f"  🔍 Found {len(h2_elements)} h2 elements, searching for: '{app_name}'")
        
        # Search for the app name in h2 elements
        for h2 in h2_elements:
            try:
                text = h2.text.strip()
                if text == app_name:
                    print(f"  ✅ Found matching app: {text}")
                    
                    # Find the parent anchor tag
                    parent = h2.find_element(By.XPATH, "./ancestor::a")
                    href = parent.get_attribute("href") or ""
                    
                    app_id = extract_app_id_from_href(href)
                    
                    if app_id:
                        print(f"  ✅ Extracted app_id: {app_id} from href: {href}")
                        time.sleep(delay)
                        return app_id
                    
                    print(f"  ⚠️  Could not extract app_id from href: {href}")
                    return None
            except Exception as e:
                print(f"  ⚠️  Error processing h2 element: {e}")
                continue
        
        print(f"  ❌ App name '{app_name}' not found on page")
        time.sleep(delay)
        return None
        
    except TimeoutException:
        print(f"  ❌ Timeout loading page for app: {app_name}")
        return None
    except Exception as e:
        print(f"  ❌ Error scraping app '{app_name}': {e}")
        return None


def extract_app_id_from_href(href: str) -> Optional[str]:
    """Extract numeric app_id from a href URL using several patterns."""
    if not href:
        return None
    
    import re
    app_id = None
    
    # Pattern 1: /app/520 or /app/520/
    match = re.search(r"/app/(\d+)", href)
    if match:
        app_id = match.group(1)
    
    # Pattern 2: ?app_id=520 or &app_id=520
    if not app_id:
        match = re.search(r"[?&]app_id=(\d+)", href)
        if match:
            app_id = match.group(1)
    
    # Pattern 3: ?id=520 or &id=520
    if not app_id:
        match = re.search(r"[?&]id=(\d+)", href)
        if match:
            app_id = match.group(1)
    
    # Pattern 4: Any numeric segment in the path
    if not app_id:
        match = re.search(r"/(\d+)(?:/|$|\?)", href)
        if match:
            app_id = match.group(1)
    
    return app_id


def get_applications_without_bapp_id(db: Session) -> List[Application]:
    """Get all applications that don't have a bapp_id set."""
    return db.query(Application).filter(
        Application.bapp_id.is_(None)
    ).all()


def scrape_all_apps(driver: webdriver.Chrome, delay: float = 0.5) -> List[Dict[str, Optional[str]]]:
    """
    Discover all applications on the disponibilidad page.
    
    Returns a list of dicts with:
        {
            "name": app_name,
            "bapp_id": app_id,
            "href": href,
            "group_name": group_name,
            "gitlab_url": gitlab_url,
        }
    """
    url = "https://pruebasdisponibilidad.cloud.osde.ar/"
    print(f"\n🌐 Discovering all apps at: {url}")
    driver.get(url)
    time.sleep(2)
    
    try:
        h2_elements = driver.find_elements(By.CSS_SELECTOR, "h2.text-xl.font-semibold.mb-4.text-white")
    except NoSuchElementException:
        print("  ⚠️  No h2 elements found with expected class")
        return []
    
    print(f"  🔍 Found {len(h2_elements)} h2 elements on page")
    
    apps: List[Dict[str, Optional[str]]] = []
    
    for h2 in h2_elements:
        try:
            name = (h2.text or "").strip()
            if not name:
                continue
            
            parent = h2.find_element(By.XPATH, "./ancestor::a")
            href = parent.get_attribute("href") or ""
            app_id = extract_app_id_from_href(href)

            # Try to get the group/agrupador label inside the same card
            group_name: Optional[str] = None
            try:
                group_span = parent.find_element(
                    By.CSS_SELECTOR,
                    "span.text-gray-300",
                )
                group_name = (group_span.text or "").strip() or None
            except NoSuchElementException:
                group_name = None
            
            # Try to find GitLab link within the same card/parent element
            gitlab_url: Optional[str] = None
            try:
                # Look for an <a> tag with href containing "git.osde.ar/projects"
                gitlab_link = parent.find_element(
                    By.XPATH,
                    ".//a[contains(@href, 'git.osde.ar/projects')]"
                )
                gitlab_url = gitlab_link.get_attribute("href") or None
                if gitlab_url:
                    print(f"  ✅ Found GitLab URL for {name}: {gitlab_url}")
            except NoSuchElementException:
                # Try searching in the parent card container if the link is not directly in the anchor
                try:
                    card_container = parent.find_element(By.XPATH, "./ancestor::div[contains(@class, 'card') or contains(@class, 'rounded')]")
                    gitlab_link = card_container.find_element(
                        By.XPATH,
                        ".//a[contains(@href, 'git.osde.ar/projects')]"
                    )
                    gitlab_url = gitlab_link.get_attribute("href") or None
                    if gitlab_url:
                        print(f"  ✅ Found GitLab URL for {name} (in card): {gitlab_url}")
                except NoSuchElementException:
                    gitlab_url = None
            
            apps.append(
                {
                    "name": name,
                    "bapp_id": app_id,
                    "href": href,
                    "group_name": group_name,
                    "gitlab_url": gitlab_url,
                }
            )
        except Exception as e:
            print(f"  ⚠️  Error processing element while discovering apps: {e}")
            continue
    
    # Small delay before next actions
    time.sleep(delay)
    
    # Log summary
    with_id = sum(1 for a in apps if a["bapp_id"])
    with_gitlab = sum(1 for a in apps if a.get("gitlab_url"))
    print(f"  ✅ Discovered {len(apps)} apps (with id: {with_id}, without id: {len(apps) - with_id}, with GitLab: {with_gitlab})")
    
    return apps


def save_mapping_results(results: List[Dict], output_dir: Path):
    """Save mapping results to JSON file."""
    output_file = output_dir / "mapping_apps.json"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Results saved to: {output_file}")


@click.group()
def cli():
    """DocuDash CLI tool."""
    pass


@cli.command("scrape-apps-names")
@click.option("--headed", default="true", help="Run browser in headed mode (true/false, default: true)")
@click.option("--timeout", type=int, default=60, help="Browser timeout in seconds (default: 60)")
@click.option("--delay", type=float, default=0.5, help="Delay between requests in seconds (default: 0.5)")
def scrape_apps_names(headed: str, timeout: int, delay: float):
    """
    Scrape app names from disponibilidad system and map to applications in database.
    
    This command:
    1. Opens a browser with manual Google login
    2. Scrapes app IDs from pruebasdisponibilidad.cloud.osde.ar
    3. Maps them to applications in the database
    4. Saves results to output/mapping_apps.json
    """
    
    # Parse headed boolean
    use_headed = parse_bool(headed)
    
    print("🚀 Starting app name scraping...")
    print(f"   Headed mode: {use_headed}")
    print(f"   Timeout: {timeout}s")
    print(f"   Delay: {delay}s\n")
    
    # Ensure output directory exists
    output_dir = ensure_output_dir()
    
    # Initialize database session
    db = SessionLocal()
    
    try:
        # Get applications without bapp_id
        apps = get_applications_without_bapp_id(db)
        
        if not apps:
            print("✅ No applications found without bapp_id. All apps are already mapped!")
            return
        
        print(f"📋 Found {len(apps)} applications without bapp_id\n")
        
        # Initialize Selenium
        print("🌐 Initializing browser...")
        driver = init_selenium_driver(headed=use_headed, timeout=timeout)
        
        try:
            # Manual Google login
            manual_google_login(driver)
            
            # First, discover ALL apps from the disponibilidad site
            discovered_apps = scrape_all_apps(driver, delay=delay)
            
            # Save full catalog for reference
            catalog_file = output_dir / "catalog_apps.json"
            with open(catalog_file, "w", encoding="utf-8") as f:
                json.dump(discovered_apps, f, indent=2, ensure_ascii=False)
            print(f"\n📁 Full catalog saved to: {catalog_file}")
            
            # Build index by normalized name for quick lookup
            index_by_name = {
                normalize_name(a["name"]): a for a in discovered_apps if a.get("name")
            }
            
            # Results list for DB mapping
            results = []
            
            # Scrape/match each application from DB using discovered catalog
            for idx, app in enumerate(apps, 1):
                print(f"\n[{idx}/{len(apps)}] Processing: {app.name}")
                print(f"   Asset ID: {app.asset_id or 'N/A'}")
                
                norm_name = normalize_name(app.name)
                matched = index_by_name.get(norm_name)
                
                app_id = matched.get("bapp_id") if matched else None
                
                if matched:
                    print(f"   🔗 Matched with discovered app name: '{matched['name']}'")
                else:
                    print("   ❌ No matching app found in discovered catalog (by normalized name)")
                
                result = {
                    "app_name": app.name,
                    "discovered_app_name": matched["name"] if matched else None,
                    "asset_id": int(app.asset_id) if app.asset_id and app.asset_id.isdigit() else None,
                    "bapp_id": int(app_id) if app_id and app_id.isdigit() else None,
                }
                
                results.append(result)
                
                # Update database if app_id was found
                if app_id:
                    app.bapp_id = app_id
                    db.commit()
                    print(f"   ✅ Updated database: bapp_id = {app_id}")
                else:
                    print(f"   ⚠️  Could not find bapp_id, leaving as null")
            
            # Save mapping results to JSON
            save_mapping_results(results, output_dir)
            
            print(f"\n🎉 Scraping completed!")
            print(f"   Total processed: {len(apps)}")
            print(f"   Successfully mapped: {sum(1 for r in results if r['bapp_id'] is not None)}")
            print(f"   Failed: {sum(1 for r in results if r['bapp_id'] is None)}")
            
        finally:
            print("\n🔒 Closing browser...")
            driver.quit()
            
    except Exception as e:
        print(f"\n❌ Error during scraping: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    cli()

