# dist/baidusearch/search_cli.py
import requests
from bs4 import BeautifulSoup
import argparse
import time
import random
import json
import sys

class BaiduSpider:
    """百度网页搜索爬虫"""
    def __init__(self):
        self.base_url = "https://www.baidu.com/s"
        # 改进的User-Agent列表，模拟不同浏览器
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Firefox/119.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Firefox/119.0",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/120.0.0.0"
        ]

    def get_headers(self):
        """获取随机的请求头"""
        return {
            "User-Agent": random.choice(self.user_agents),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Cache-Control": "max-age=0"
        }

    def get_real_url(self, raw_url):
        if not raw_url or not raw_url.startswith("http"):
            return raw_url
        try:
            res = requests.head(raw_url, headers=self.get_headers(), allow_redirects=False, timeout=5)
            if res.status_code in [301, 302]:
                return res.headers.get("Location", raw_url)
        except Exception:
            pass
        return raw_url

    def search(self, keyword, start_page=1, limit=5):
        page = start_page
        count = 0
        retry_count = 0
        max_retries = 3
        
        while count < limit:
            pn = (page - 1) * 10
            params = {"wd": keyword, "pn": pn}
            try:
                # 使用随机请求头
                headers = self.get_headers()
                response = requests.get(self.base_url, params=params, headers=headers, timeout=10)
                
                if response.status_code != 200:
                    retry_count += 1
                    if retry_count > max_retries:
                        print(f"[Error] 连续 {max_retries} 次请求失败，退出", file=sys.stderr)
                        break
                    time.sleep(random.uniform(2, 4))
                    continue
                
                # 检查是否被百度拦截
                if "百度安全验证" in response.text or "网络不给力" in response.text:
                    print(f"[Warning] 被百度安全验证拦截，正在重试...", file=sys.stderr)
                    retry_count += 1
                    if retry_count > max_retries:
                        print(f"[Error] 连续 {max_retries} 次被拦截，退出", file=sys.stderr)
                        break
                    # 增加延迟并重试
                    time.sleep(random.uniform(3, 6))
                    continue
                
                soup = BeautifulSoup(response.text, "html.parser")
                
                # 尝试多种选择器
                items = soup.select("div.c-container")
                if not items:
                    items = soup.select("div.result")
                if not items:
                    items = soup.select("div.t")
                if not items:
                    # 尝试找到包含搜索结果的其他容器
                    all_divs = soup.find_all("div")
                    items = []
                    for div in all_divs:
                        # 查找包含标题链接的div
                        title_tag = div.find("h3") or div.find("h2")
                        if title_tag and title_tag.find("a"):
                            items.append(div)
                
                if not items:
                    print("[Warning] 未找到搜索结果容器", file=sys.stderr)
                    break
                
                for item in items:
                    if count >= limit: break
                    
                    # 查找标题
                    title_tag = item.find("h3") or item.find("h2")
                    if not title_tag: continue
                    
                    title_link = title_tag.find("a")
                    if not title_link: continue
                    
                    title = title_link.get_text().strip()
                    link = title_link.get("href")
                    
                    # 查找描述
                    description = "暂无简介"
                    # 尝试多种描述选择器
                    desc_candidates = [
                        item.find("div", class_="c-abstract"),
                        item.find("div", class_="content-right_8Zs40"),
                        item.find("div", class_="abstract"),
                        item.find("div", class_="result-content"),
                        item.find_next_sibling("div", class_="c-abstract")
                    ]
                    
                    for desc_tag in desc_candidates:
                        if desc_tag:
                            description = desc_tag.get_text().strip()
                            break
                    
                    # 查找图片
                    img_url = ""
                    img_candidates = [
                        item.find("img", class_="c-img"),
                        item.find("img"),
                        item.find_next("img")
                    ]
                    
                    for img_tag in img_candidates:
                        if img_tag:
                            img_url = img_tag.get("src") or img_tag.get("data-src") or ""
                            if img_url.startswith("//"):
                                img_url = "https:" + img_url
                            break
                    
                    real_url = self.get_real_url(link)
                    
                    yield {
                        "rank": count + 1,
                        "title": title,
                        "url": real_url,
                        "img": img_url,
                        "description": description,
                        "source": "baidu_search",
                        "time": time.strftime("%Y-%m-%d %H:%M:%S")
                    }
                    count += 1
                    # 每获取一个结果，添加随机延迟
                    time.sleep(random.uniform(0.5, 1.5))
                
                page += 1
                retry_count = 0  # 重置重试计数
                # 每页之间添加较长延迟
                time.sleep(random.uniform(2, 4))
                
            except Exception as e:
                print(f"[Error] Baidu Search Error: {e}", file=sys.stderr)
                import traceback
                traceback.print_exc()
                retry_count += 1
                if retry_count > max_retries:
                    break
                time.sleep(random.uniform(2, 5))
        
        if count == 0:
            print(f"[Warning] 未获取到任何搜索结果", file=sys.stderr)

class BaiduNewsSpider:
    """百度新闻爬虫"""
    def __init__(self):
        self.base_url = "https://www.baidu.com/s"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
        }

    def search(self, keyword, limit=10):
        # rtt=1: 按时间排序, rtt=4: 按相关性排序
        params = {"tn": "news", "wd": keyword, "rtt": 1}
        count = 0
        try:
            res = requests.get(self.base_url, params=params, headers=self.headers, timeout=10)
            if res.status_code != 200: return
            soup = BeautifulSoup(res.text, "html.parser")
            items = soup.select(".result-op.news")
            for item in items:
                if count >= limit: break
                title_tag = item.select_one("h3 a")
                if not title_tag: continue
                title = title_tag.get_text().strip()
                url = title_tag.get("href")
                source_tag = item.select_one(".c-color-gray.c-font-normal")
                source_name = source_tag.get_text().strip() if source_tag else "百度新闻"
                desc_tag = item.select_one(".c-font-normal.c-color-text")
                description = desc_tag.get_text().strip() if desc_tag else "点击查看详情"
                img_tag = item.select_one(".c-img img")
                img_url = ""
                if img_tag:
                    img_url = img_tag.get("src") or img_tag.get("data-src") or ""
                    if img_url.startswith("//"): img_url = "https:" + img_url
                
                yield {
                    "rank": count + 1,
                    "title": title,
                    "url": url,
                    "img": img_url,
                    "description": f"[{source_name}] {description}",
                    "source": "baidu_news",
                    "time": time.strftime("%Y-%m-%d %H:%M:%S")
                }
                count += 1
        except Exception as e:
            print(f"[Error] Baidu News Error: {e}", file=sys.stderr)

class SoSpider:
    """360搜索爬虫"""
    def __init__(self):
        self.base_url = "https://www.so.com/s"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
        }

    def search(self, keyword, limit=10):
        params = {"q": keyword}
        try:
            res = requests.get(self.base_url, params=params, headers=self.headers, timeout=10)
            if res.status_code != 200: return
            soup = BeautifulSoup(res.text, "html.parser")
            items = soup.select(".res-list")
            count = 0
            for item in items:
                if count >= limit: break
                title_tag = item.select_one("h3 a")
                if not title_tag: continue
                title = title_tag.get_text().strip()
                url = title_tag.get("href")
                desc_tag = item.select_one(".res-desc") or item.select_one(".res-rich")
                description = desc_tag.get_text().strip() if desc_tag else "查看更多内容..."
                img_tag = item.select_one(".res-img img") or item.select_one("img")
                img_url = ""
                if img_tag:
                    img_url = img_tag.get("src") or img_tag.get("data-src") or ""
                    if img_url.startswith("//"): img_url = "https:" + img_url
                yield {
                    "rank": count + 1,
                    "title": title,
                    "url": url,
                    "img": img_url,
                    "description": description,
                    "source": "360_search",
                    "time": time.strftime("%Y-%m-%d %H:%M:%S")
                }
                count += 1
        except Exception as e:
            print(f"[Error] 360 Search Error: {e}", file=sys.stderr)

def main():
    parser = argparse.ArgumentParser(description="政企信息采集器")
    parser.add_argument("--wd", type=str, required=True)
    parser.add_argument("--type", type=str, default="baidu", choices=["baidu", "baidu_news", "360"])
    parser.add_argument("--limit", type=int, default=10)
    args = parser.parse_args()
    
    if args.type == "baidu":
        spider = BaiduSpider()
    elif args.type == "baidu_news":
        spider = BaiduNewsSpider()
    else:
        spider = SoSpider()
        
    results = list(spider.search(args.wd, limit=args.limit))
    print(json.dumps(results, ensure_ascii=False, indent=4))

if __name__ == "__main__":
    main()
