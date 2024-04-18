import urllib.request
from selenium.common.exceptions import NoSuchElementException
from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import time


# 웹드라이버 설정
options = webdriver.ChromeOptions()
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option("useAutomationExtension", False)

#네이버 오픈 API를 이용하기 위해 발급받은 client ID와 client Secret를 입력.
client_id = "4lES1cvcJAmQlPO_waO3" 
client_secret = "laR5NceTpV" 
keyword = input("키워드 입력: ") #원하는 정보의 키워드를 입력
Key_word = urllib.parse.quote(keyword)
post_num = input("추출할 키워드 포스트 갯수: ") #포스트 갯수 입력(10개가 넘어가면 로딩 시간이 꽤 걸린다)
url = "https://openapi.naver.com/v1/search/blog?query=" + Key_word +"&display="+post_num
# openapi를 이용한 네이버 블로그 주소를 가져오는 형식이다.

request = urllib.request.Request(url)
request.add_header("X-Naver-Client-Id",client_id)
request.add_header("X-Naver-Client-Secret",client_secret)
response = urllib.request.urlopen(request)

response_body = response.read()
body = response_body.decode('utf-8')

#body를 나누기
post = body.split('\n\t\t{\n\t\t\t')
post = [i for i in post]

#블로그 제목, 링크 뽑기
import re
post_name = []
post_url = []
for i in post:
    name = re.findall('"title":"(.*?)",\n\t\t\t"link"',i)
    u_rl = re.findall('"link":"(.*?)",\n\t\t\t"description"',i)
    post_name.append(name)
    post_url.append(u_rl)
 
post_name = [k for i in post_name for k in i]
post_url = [k for i in post_url for k in i]


post_links = []
for i in post_url:
    k = i.replace('\\','')
    c = k.replace('?Redirect=Log&logNo=','/')
    post_links.append(c)

# 크롬 드라이버 설치
driver_service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=driver_service)
driver.implicitly_wait(3)

#각 포스트를 리스트로 담아 for문을 사용해 각 리스트의 정보를 수집한다
matzip_list=[]
for i in post_links:
    driver.get(i)
    time.sleep(1)
    # 네이버 블로그 특성상 iframe에 body값을 가져온다
    driver.switch_to.frame("mainFrame")
   
    se_module_map_text = driver.find_elements(By.CSS_SELECTOR, 'div.se-module.se-module-map-text')
    for i in se_module_map_text:
        se_map_title = i.find_element(By.CLASS_NAME, 'se-map-title')
        se_map_address = i.find_element(By.CLASS_NAME, 'se-map-address')
        matzip_list.append(se_map_title.text)


# 검색 결과로 블로그의 이름과 주소를 함꼐 나열
print("\n<< 검색 결과 >>")
for i in range(len(post_name)):
    print(f"{post_name[i]}\n{post_links[i]}\n")


#추출한 구글 리스트 출력
print("구글 리스트:",matzip_list)

url_list=[]
name_url_dict = {}
for name in matzip_list:
    # 검색어 URL 인코딩
    encoded_address = urllib.parse.quote(name)
    # 구글 지도 검색 URL 생성
    url = f"https://www.google.com/maps/place/{encoded_address}"
    url_list.append(url)
    name_url_dict[name] = url
    
for name, url in name_url_dict.items():
       print(f"{name}: {url}\n")
    

#위에서 가져온 구글 주소의 웹크롤링을 통해 이름,평점,주소 추출 
import requests
from bs4 import BeautifulSoup
import re
import urllib.parse

def get_google_maps_info(url):
    response = requests.get(url)
    html = response.text
    soup = BeautifulSoup(html, 'html.parser')

    name_element = soup.find('meta', itemprop='name')
    if name_element:
        name = name_element['content']
    else:
        name = None

    descript = soup.find('meta', itemprop='description')
    if descript:
        description = descript['content']
    else:
        description = None

    return name, description


for url in url_list:
    name, description = get_google_maps_info(url)

    # 정규 표현식을 사용하여 주소 부분 추출
    pattern = r'·\s+(.*)'
    match = re.search(pattern, name)

    # 주소 부분을 제거하여 가게 이름 추출
    name = name.split('·', 1)[0].strip()

    if name:
        print('가게 이름:', name)
    else:
        print('이름을 찾을 수 없습니다.')

    if match:
        address = match.group(1)
        print('주소:', address)
    else:
        print('주소를 찾을 수 없습니다.')

    if description:
        print('평점:', description)
    else:
        print('평점을 찾을 수 없습니다.')
    print(f"\n")
