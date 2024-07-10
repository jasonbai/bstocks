import time
import subprocess

# 定义爬虫文件列表
crawler_files = [
    r'dataloader\dailyreview_dataloader.py',
    r'dataloader\fund_price_downloader.py',
    r'dataloader\fund_rank_dataloader.py',
    r'dataloader\us_dataloader.py',
    r'dataloader\width_dataloader.py'
]

# 按顺序运行每个爬虫文件，并在每个文件运行后等待10秒钟
for crawler_file in crawler_files:
    print(f"Running {crawler_file}...")
    subprocess.run(['python', crawler_file])
    print(f"Finished running {crawler_file}. Waiting for 10 seconds before running the next one...")
    time.sleep(10)

print("All crawlers have been executed successfully.")