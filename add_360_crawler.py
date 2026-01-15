#!/usr/bin/env python3
import sqlite3
import os

def add_360_crawler():
    # 获取数据库路径
    db_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'data.db')
    
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        
        # 检查是否已有360爬虫
        cursor = conn.execute("SELECT * FROM crawlers WHERE type = '360_search' OR name LIKE '%360%'")
        existing = cursor.fetchone()
        
        if existing:
            print(f"360爬虫已存在: ID={existing['id']}, 名称={existing['name']}")
        else:
            # 插入360搜索爬虫
            conn.execute(
                "INSERT INTO crawlers (name, type, status) VALUES (?, ?, ?)",
                ('360搜索爬虫', '360_search', '可用')
            )
            conn.commit()
            print("已添加360搜索爬虫")
        
        # 检查是否已有百度新闻爬虫
        cursor = conn.execute("SELECT * FROM crawlers WHERE type = 'baidu_news' OR name LIKE '%新闻%'")
        existing = cursor.fetchone()
        
        if existing:
            print(f"百度新闻爬虫已存在: ID={existing['id']}, 名称={existing['name']}")
        else:
            # 插入百度新闻爬虫
            conn.execute(
                "INSERT INTO crawlers (name, type, status) VALUES (?, ?, ?)",
                ('百度新闻爬虫', 'baidu_news', '可用')
            )
            conn.commit()
            print("已添加百度新闻爬虫")
        
        # 检查百度搜索爬虫的类型是否正确
        cursor = conn.execute("SELECT * FROM crawlers WHERE name = '百度搜索爬虫'")
        baidu_crawler = cursor.fetchone()
        
        if baidu_crawler and baidu_crawler['type'] != 'baidu_search':
            # 更新类型
            conn.execute(
                "UPDATE crawlers SET type = 'baidu_search' WHERE id = ?",
                (baidu_crawler['id'],)
            )
            conn.commit()
            print("已更新百度搜索爬虫的类型为 'baidu_search'")
        
        # 重新查询所有爬虫
        print("\n所有爬虫配置:")
        cursor = conn.execute("SELECT * FROM crawlers")
        crawlers = cursor.fetchall()
        for crawler in crawlers:
            print(f"ID: {crawler['id']}, 名称: {crawler['name']}, 类型: {crawler['type']}, 状态: {crawler['status']}")
        
        conn.close()
        
    except Exception as e:
        print(f"数据库操作失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    add_360_crawler()
