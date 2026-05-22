# Python爬虫
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. 爬虫概述

网络爬虫（Web Crawler）是一种自动获取网页内容的程序。Python提供了丰富的爬虫库：
- **requests**：HTTP请求库
- **BeautifulSoup**：HTML解析库
- **Scrapy**：专业的爬虫框架
- **Selenium**：浏览器自动化工具

## 2. requests库

### 2.1 基本使用

```python
import requests

# GET请求
response = requests.get('https://www.example.com')
print(response.status_code)  # 状态码
print(response.text)         # 响应内容
print(response.headers)      # 响应头
print(response.cookies)      # Cookie

# POST请求
data = {'key': 'value'}
response = requests.post('https://httpbin.org/post', data=data)
```

### 2.2 请求头设置

```python
import requests

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8'
}

response = requests.get('https://www.example.com', headers=headers)
```

### 2.3 Cookie处理

```python
import requests

# 发送Cookie
cookies = {'name': 'value'}
response = requests.get('https://www.example.com', cookies=cookies)

# 使用会话保持Cookie
session = requests.Session()
session.get('https://www.example.com/login', params={'user': 'admin', 'pass': '123'})
response = session.get('https://www.example.com/dashboard')
```

### 2.4 代理设置

```python
import requests

proxies = {
    'http': 'http://proxy.example.com:8080',
    'https': 'https://proxy.example.com:8080'
}

response = requests.get('https://www.example.com', proxies=proxies)
```

## 3. BeautifulSoup

### 3.1 安装

```bash
pip install beautifulsoup4 lxml
```

### 3.2 基本使用

```python
from bs4 import BeautifulSoup
import requests

# 获取网页
response = requests.get('https://www.example.com')
html = response.text

# 解析HTML
soup = BeautifulSoup(html, 'lxml')

# 查找元素
title = soup.title
print(title.text)

# 查找所有链接
links = soup.find_all('a')
for link in links:
    print(link.get('href'))
```

### 3.3 查找元素

```python
from bs4 import BeautifulSoup

html = '''
<html>
<body>
    <div class="content">
        <h1>标题</h1>
        <p class="text">段落1</p>
        <p class="text">段落2</p>
    </div>
</body>
</html>
'''

soup = BeautifulSoup(html, 'lxml')

# 通过标签名查找
div = soup.find('div')
print(div)

# 通过class查找
div = soup.find('div', class_='content')
texts = soup.find_all('p', class_='text')

# 通过id查找
element = soup.find(id='my-id')

# 通过属性查找
link = soup.find('a', href='https://www.example.com')

# CSS选择器
elements = soup.select('.content p')
element = soup.select_one('#my-id')
```

### 3.4 提取数据

```python
from bs4 import BeautifulSoup

soup = BeautifulSoup(html, 'lxml')

# 获取文本
text = soup.find('p').text
text = soup.find('p').get_text()

# 获取属性
href = soup.find('a').get('href')
href = soup.find('a')['href']

# 获取所有属性
attrs = soup.find('a').attrs
```

## 4. 爬虫实战

### 4.1 简单爬虫示例

```python
import requests
from bs4 import BeautifulSoup

def crawl_page(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'lxml')
    
    # 提取标题
    title = soup.find('title').text
    
    # 提取所有链接
    links = []
    for link in soup.find_all('a'):
        href = link.get('href')
        if href:
            links.append(href)
    
    return {
        'title': title,
        'links': links
    }

result = crawl_page('https://www.example.com')
print(result)
```

### 4.2 多线程爬虫

```python
import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
import time

def crawl_page(url):
    try:
        response = requests.get(url, timeout=5)
        soup = BeautifulSoup(response.text, 'lxml')
        title = soup.find('title').text
        return {'url': url, 'title': title}
    except Exception as e:
        return {'url': url, 'error': str(e)}

urls = [
    'https://www.example.com',
    'https://www.python.org',
    'https://www.github.com'
]

# 使用线程池
with ThreadPoolExecutor(max_workers=3) as executor:
    results = list(executor.map(crawl_page, urls))

for result in results:
    print(result)
```

### 4.3 异步爬虫

```python
import aiohttp
from bs4 import BeautifulSoup
import asyncio

async def crawl_page(session, url):
    try:
        async with session.get(url) as response:
            html = await response.text()
            soup = BeautifulSoup(html, 'lxml')
            title = soup.find('title').text
            return {'url': url, 'title': title}
    except Exception as e:
        return {'url': url, 'error': str(e)}

async def main():
    urls = [
        'https://www.example.com',
        'https://www.python.org',
        'https://www.github.com'
    ]
    
    async with aiohttp.ClientSession() as session:
        tasks = [crawl_page(session, url) for url in urls]
        results = await asyncio.gather(*tasks)
    
    for result in results:
        print(result)

asyncio.run(main())
```

## 5. Scrapy框架

### 5.1 安装

```bash
pip install scrapy
```

### 5.2 创建项目

```bash
scrapy startproject myproject
cd myproject
scrapy genspider example www.example.com
```

### 5.3 编写爬虫

```python
import scrapy

class ExampleSpider(scrapy.Spider):
    name = 'example'
    allowed_domains = ['www.example.com']
    start_urls = ['https://www.example.com']
    
    def parse(self, response):
        # 提取标题
        title = response.css('title::text').get()
        
        # 提取链接
        links = response.css('a::attr(href)').getall()
        
        yield {
            'title': title,
            'links': links
        }
        
        # 跟进链接
        for link in links:
            if link.startswith('http'):
                yield response.follow(link, self.parse)
```

### 5.4 运行爬虫

```bash
scrapy crawl example
scrapy crawl example -o output.json
scrapy crawl example -o output.csv
```

### 5.5 数据管道

```python
# pipelines.py
class MyProjectPipeline:
    def process_item(self, item, spider):
        # 数据处理逻辑
        return item

# settings.py
ITEM_PIPELINES = {
    'myproject.pipelines.MyProjectPipeline': 300,
}
```

## 6. Selenium

### 6.1 安装

```bash
pip install selenium
# Selenium 4.6+ 自带 Selenium Manager，会自动下载并管理 ChromeDriver/GeckoDriver 等驱动，无需单独配置
# <!-- 修复于 2026-05-22: Selenium 4.6 起内置 Selenium Manager，原"还需要下载浏览器驱动"已过时 -->
```

### 6.2 基本使用

```python
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# 创建浏览器驱动
driver = webdriver.Chrome()

# 访问网页
driver.get('https://www.example.com')

# 查找元素
element = driver.find_element(By.ID, 'my-id')
element = driver.find_element(By.CLASS_NAME, 'my-class')
element = driver.find_element(By.XPATH, '//div[@class="content"]')

# 操作元素
element.click()
element.send_keys('text')
text = element.text

# 等待元素
wait = WebDriverWait(driver, 10)
element = wait.until(EC.presence_of_element_located((By.ID, 'my-id')))

# 执行JavaScript
driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')

# 关闭浏览器
driver.quit()
```

### 6.3 无头浏览器

```python
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

options = Options()
options.add_argument('--headless')  # 无头模式
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')

driver = webdriver.Chrome(options=options)
driver.get('https://www.example.com')
print(driver.title)
driver.quit()
```

## 7. 数据存储

### 7.1 保存到文件

```python
import json
import csv

# JSON格式
data = {'title': 'Example', 'url': 'https://www.example.com'}
with open('data.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

# CSV格式
import csv
with open('data.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(['title', 'url'])
    writer.writerow(['Example', 'https://www.example.com'])
```

### 7.2 保存到数据库

```python
import sqlite3

conn = sqlite3.connect('data.db')
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS pages (
        id INTEGER PRIMARY KEY,
        title TEXT,
        url TEXT
    )
''')

cursor.execute('INSERT INTO pages (title, url) VALUES (?, ?)', 
                ('Example', 'https://www.example.com'))
conn.commit()
conn.close()
```

## 8. 反爬虫对策

### 8.1 常见反爬虫机制

1. **User-Agent检测**：设置合理的User-Agent
2. **IP限制**：使用代理IP
3. **验证码**：使用OCR或打码平台
4. **JavaScript渲染**：使用Selenium或Playwright
5. **Cookie验证**：维护会话状态

### 8.2 应对策略

```python
import requests
import time
import random

# 设置随机User-Agent
user_agents = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
]

headers = {
    'User-Agent': random.choice(user_agents)
}

# 随机延迟
time.sleep(random.uniform(1, 3))

# 使用代理
proxies = {
    'http': 'http://proxy.example.com:8080',
    'https': 'https://proxy.example.com:8080'
}

response = requests.get('https://www.example.com', 
                       headers=headers, 
                       proxies=proxies)
```

## 9. 最佳实践

1. **遵守robots.txt**：尊重网站的爬虫协议
2. **控制请求频率**：避免对服务器造成压力
3. **异常处理**：网络请求可能失败，需要适当的异常处理
4. **数据去重**：避免重复爬取相同内容
5. **合法合规**：遵守相关法律法规，不爬取敏感信息

## 10. 总结

Python爬虫工具链：
- **requests + BeautifulSoup**：简单快速的爬虫方案
- **Scrapy**：专业的爬虫框架，适合大型项目
- **Selenium**：处理JavaScript渲染的页面

选择合适的工具可以高效地完成爬虫任务。

## 11. 2026 年 AI 爬虫新工具

<!-- version-check: Crawl4AI 0.8.x, Crawlee-Python 0.6.x, Scrapy 2.14.0, checked 2026-05-22 -->

> 🔄 更新于 2026-05-22 <!-- 修复于 2026-05-22: Scrapy 实际最新稳定版是 2.14.0，2.15.x 尚未发布 -->

2026 年爬虫生态最大的变化是 **AI Agent 驱动的爬虫工具**兴起，传统的 HTML 解析正在被 LLM 结构化提取补充。

### 11.1 Crawl4AI — LLM 友好的异步爬虫

Crawl4AI 是专为 AI/LLM 工作流设计的开源爬虫框架，基于 Playwright，将网页转换为干净的 Markdown、HTML 或结构化 JSON。

```python
from crawl4ai import AsyncWebCrawler

async def main():
    async with AsyncWebCrawler() as crawler:
        # 基础爬取：自动转换为 Markdown
        result = await crawler.arun(url="https://example.com")
        print(result.markdown)  # 干净的 Markdown 输出

        # CSS 结构化提取（无需 LLM）
        from crawl4ai.extraction_strategy import JsonCssExtractionStrategy
        import json

        schema = {
            "name": "产品列表",
            "baseSelector": "div.product",
            "fields": [
                {"name": "title", "selector": "h2", "type": "text"},
                {"name": "price", "selector": ".price", "type": "text"},
                {"name": "link", "selector": "a", "type": "attribute", "attribute": "href"},
            ]
        }
        strategy = JsonCssExtractionStrategy(schema)
        result = await crawler.arun(
            url="https://example.com/products",
            extraction_strategy=strategy
        )
        products = json.loads(result.extracted_content)
```

**核心优势**：
- 自动将网页转为 LLM 友好的 Markdown（适合 RAG 管道）
- CSS 结构化提取（无需 LLM，零成本）
- 支持 LLM 提取（OpenAI / DeepSeek / 本地模型）
- 会话管理、JS 执行、截图
- MCP Server 模式（供 AI Agent 调用）

来源：[Crawl4AI 文档](https://docs.crawl4ai.com/)

### 11.2 Crawlee-Python — Apify 的生产级爬虫库

```python
from crawlee.playwright_crawler import PlaywrightCrawler, PlaywrightCrawlingContext

crawler = PlaywrightCrawler()

@crawler.router.default_handler
async def handler(context: PlaywrightCrawlingContext):
    title = await context.page.title()
    await context.push_data({"title": title, "url": context.request.url})
    await context.enqueue_links()

await crawler.run(["https://example.com"])
```

**核心优势**：自动代理轮换、请求队列持久化、错误重试、headful/headless 切换。

来源：[Crawlee-Python GitHub](https://github.com/apify/crawlee-python)

### 11.3 2026 年 Python 爬虫工具选型表

| 工具 | 适用场景 | JS 渲染 | AI 集成 | 学习曲线 |
| ---- | -------- | ------- | ------- | -------- |
| **requests + BS4** | 简单静态页面 | ❌ | ❌ | 低 |
| **Scrapy 2.14** | 大规模结构化爬取 | ❌ | ❌ | 中 |
| **Playwright** | JS 渲染页面 | ✅ | ❌ | 中 |
| **Crawl4AI** | AI/RAG 数据管道 | ✅ | ✅ | 低 |
| **Crawlee** | 生产级可靠爬取 | ✅ | ❌ | 中 |
| **Selenium** | 遗留项目维护 | ✅ | ❌ | 中 |

