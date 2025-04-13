# #!/usr/bin/env python
# """Django's command-line utility for administrative tasks."""
# import os
# import sys
#
#
# def main():
#     """Run administrative tasks."""
#     os.environ.setdefault("DJANGO_SETTINGS_MODULE", "fashion_analytics.settings")
#     try:
#         from django.core.management import execute_from_command_line
#     except ImportError as exc:
#         raise ImportError(
#             "Couldn't import Django. Are you sure it's installed and "
#             "available on your PYTHONPATH environment variable? Did you "
#             "forget to activate a virtual environment?"
#         ) from exc
#     execute_from_command_line(sys.argv)
#
#
# if __name__ == "__main__":
#     main()
import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import json


def get_beijing_subway_transfer_stations():
    # 从维基百科获取北京地铁信息
    url = "https://zh.wikipedia.org/wiki/%E5%8C%97%E4%BA%AC%E5%9C%B0%E9%93%81%E8%BD%A6%E7%AB%99%E5%88%97%E8%A1%A8"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        # 找到包含地铁站信息的表格
        tables = soup.find_all('table', {'class': 'wikitable'})

        all_stations = []
        transfer_stations = {}

        # 处理每个表格
        for table in tables:
            rows = table.find_all('tr')
            header = rows[0].text.strip()

            # 确认这是包含地铁站点的表格
            if '站名' in header and '线路' in header:
                for row in rows[1:]:
                    cols = row.find_all(['td', 'th'])
                    if len(cols) >= 3:
                        # 获取站名和线路信息
                        station_name = cols[0].text.strip().replace('\n', '')
                        lines = cols[1].text.strip().replace('\n', '')

                        # 添加到所有站点列表
                        all_stations.append({
                            "station": station_name,
                            "lines": lines
                        })

        # 识别换乘站点（出现在多条线路上的站点）
        station_lines = {}
        for station in all_stations:
            name = station["station"]
            if name not in station_lines:
                station_lines[name] = set()

            # 提取线路信息
            lines = re.findall(r'[^\d](\d+)[^\d]|[^\d](\d+)号线', station["lines"])
            for line_match in lines:
                for line in line_match:
                    if line:
                        station_lines[name].add(line + "号线")

            # 处理特殊线路名称
            special_lines = ["机场线", "大兴机场线", "亦庄线", "房山线", "昌平线", "亦庄线", "燕房线", "S1线", "西郊线"]
            for special in special_lines:
                if special in station["lines"]:
                    station_lines[name].add(special)

        # 筛选换乘站点（有多条线路的站点）
        for station, lines in station_lines.items():
            if len(lines) > 1:
                transfer_stations[station] = list(lines)

        # 保存结果到JSON和CSV
        with open('beijing_subway_transfer_stations.json', 'w', encoding='utf-8') as f:
            json.dump(transfer_stations, f, ensure_ascii=False, indent=4)

        # 创建DataFrame并保存为CSV
        transfer_data = []
        for station, lines in transfer_stations.items():
            transfer_data.append({
                "站点名称": station,
                "换乘线路": "、".join(lines),
                "换乘线路数量": len(lines)
            })

        df = pd.DataFrame(transfer_data)
        df.sort_values(by="换乘线路数量", ascending=False, inplace=True)
        df.to_csv('beijing_subway_transfer_stations.csv', index=False, encoding='utf-8-sig')

        return {
            "total_transfer_stations": len(transfer_stations),
            "transfer_stations": transfer_stations,
            "files_saved": ["beijing_subway_transfer_stations.json", "beijing_subway_transfer_stations.csv"]
        }

    except Exception as e:
        return {"error": str(e)}


if __name__ == "__main__":
    result = get_beijing_subway_transfer_stations()
    print(f"找到 {result.get('total_transfer_stations', 0)} 个换乘站点")
    print("数据已保存到文件中: beijing_subway_transfer_stations.json 和 beijing_subway_transfer_stations.csv")