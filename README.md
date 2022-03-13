# iCook-RecipeCrawler

## 目的

該程式為爬取「愛料理」（iCook）網頁之食譜所開發，將資料分組後存入 MongoDB 資料庫

## 流程

> ### link_crawler.py
> 該程式將爬取所有分類中的食譜網址，並存入資料庫

> ### recipe_crawler.py
> 該程式取出資料庫中的食譜網址，並依序爬取後將內容存入資料庫

> ### connection.py
> 該程式負責資料庫的操作
