from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import json
import time

def crawl_danawa_mats():
    """
    다나와에서 매트 제품을 순서대로 크롤링
    """
    # Chrome 옵션 설정
    chrome_options = Options()
    chrome_options.add_argument('--headless')  # 헤드리스 모드 (브라우저 창 안 띄움)
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
    
    # 다나와 매트 검색 URL (예시)
    url = "https://search.danawa.com/dsearch.php?query=매트&tab=goods"
    
    driver = None
    try:
        # ChromeDriver 경로 설정 (Docker 컨테이너 내부 경로)
        service = Service('/usr/local/bin/chromedriver')
        # WebDriver 생성
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.get(url)
        
        # 페이지 로딩 대기
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".main_prodlist_list")))
        
        # 스크롤하여 더 많은 제품 로드 (필요시)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        
        # 제품 목록 컨테이너 찾기
        product_list = driver.find_element(By.CSS_SELECTOR, ".main_prodlist_list .product_list")
        products = product_list.find_elements(By.CSS_SELECTOR, "li.prod_item.prod_layer")
        
        results = []
        
        # 각 제품 정보 추출
        for idx, product in enumerate(products, 1):
            try:
                # 제품 ID 추출
                product_id = product.get_attribute("id")
                if product_id:
                    product_id = product_id.replace("productItem", "")
                
                # 제품명 추출
                try:
                    prod_info = product.find_element(By.CSS_SELECTOR, ".prod_info")
                    prod_name_elem = prod_info.find_element(By.CSS_SELECTOR, ".prod_name a, .prod_name")
                    product_name = prod_name_elem.text.strip()
                except:
                    product_name = ""
                
                # 제품 링크 추출
                try:
                    prod_link_elem = product.find_element(By.CSS_SELECTOR, ".thumb_link, .prod_name a")
                    product_link = prod_link_elem.get_attribute("href")
                except:
                    product_link = ""
                
                # 제품 이미지 추출
                try:
                    img_elem = product.find_element(By.CSS_SELECTOR, ".thumb_image img, .thumb_link img")
                    product_image = img_elem.get_attribute("src")
                    if not product_image or product_image.startswith("//"):
                        product_image = "https:" + product_image if product_image.startswith("//") else product_image
                except:
                    product_image = ""
                
                # 가격 정보 추출
                try:
                    price_list = product.find_element(By.CSS_SELECTOR, ".prod_pricelist")
                    price_elem = price_list.find_element(By.CSS_SELECTOR, ".price_sect strong, .price")
                    price = price_elem.text.strip()
                except:
                    price = ""
                
                # 카테고리 정보 추출
                try:
                    category_input = product.find_element(By.CSS_SELECTOR, "input[type='hidden'][id*='categoryInfo']")
                    category = category_input.get_attribute("value")
                except:
                    category = ""
                
                # 결과에 추가
                if product_name:  # 제품명이 있는 경우만 추가
                    results.append({
                        "순서": idx,
                        "제품ID": product_id,
                        "제품명": product_name,
                        "링크": product_link,
                        "이미지": product_image,
                        "가격": price,
                        "카테고리": category
                    })
                    
            except Exception as e:
                # 개별 제품 처리 중 오류 발생 시 스킵
                print(f"제품 {idx} 처리 중 오류: {str(e)}")
                continue
        
        return results
        
    except Exception as e:
        print(f"크롤링 중 오류 발생: {str(e)}")
        return []
        
    finally:
        if driver:
            driver.quit()

if __name__ == "__main__":
    # 크롤링 실행
    results = crawl_danawa_mats()
    
    # JSON 형태로 터미널에 출력
    print(json.dumps(results, ensure_ascii=False, indent=2))

