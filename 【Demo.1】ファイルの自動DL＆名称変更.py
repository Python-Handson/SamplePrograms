
import pandas as pd
import time
import PyPDF2
import datetime
import urllib.request
import re

import sys
import os
import requests
import dateutil.parser
from bs4 import BeautifulSoup


#----- プロキシサーバー -----
# 社内環境やPulseSecure使用の場合はコメントアウトを外す
#os.environ["https_proxy"] = "http://g3.konicaminolta.jp:8080"

#----- 入力ファイル -----
# Excel
READ_FILE_DIR = r'C:\Users\e12135\Downloads\DL2'
CTRL_PORTABLE = True if not os.path.isdir(READ_FILE_DIR) else False
READ_FILE_DIR = os.getcwd() if CTRL_PORTABLE else READ_FILE_DIR # READ_FILE_DIRが存在しないときはカレントフォルダをREAD_FILE_DIRに設定

TARGET_URL = 'https://www.mhlw.go.jp/stf/seisakunitsuite/bunya/kenkou_iryou/iryou/rinsyo/index_00014.html'

PROVCODE = {
    '北海道': 1, '青森県': 2, '岩手県': 3, '宮城県': 4, '秋田県': 5, '山形県': 6, '福島県': 7, 
    '茨城県': 8, '栃木県': 9, '群馬県': 10, '埼玉県': 11, '千葉県': 12, '東京都': 13, '神奈川県': 14, 
    '新潟県': 15, '富山県': 16, '石川県': 17, '福井県': 18, '山梨県': 19, '長野県': 20, 
    '岐阜県': 21, '静岡県': 22, '愛知県': 23, '三重県': 24, '滋賀県': 25, 
    '京都府': 26, '大阪府': 27, '兵庫県': 28, '奈良県': 29, '和歌山県': 30, 
    '鳥取県': 31, '島根県': 32, '岡山県': 33, '広島県': 34, '山口県': 35, 
    '徳島県': 36, '香川県': 37, '愛媛県': 38, '高知県': 39, 
    '福岡県': 40, '佐賀県': 41, '長崎県': 42, '熊本県': 43, '大分県': 44, '宮崎県': 45, '鹿児島県': 46, '沖縄県': 47
}


#================================================================
# main()
#================================================================
def main():
    
    #--------------------------------------------
    # ダウンロードリスト（辞書型）作成
    #  [I] TARGET_URL, PROVCODE
    #  [O] dict_pdf_link
    #--------------------------------------------
    global dict_pdf_link
    dict_pdf_link = dict()
    # TARGET_URLからドメイン部を抽出 -> [base_url]
    str_temp1 = re.split(r'//', TARGET_URL) # '//'で分割
    str_temp2 = str_temp1[1].split('/') # '/'で分割
    base_url = str_temp1[0] + '//' + str_temp2[0]
    
    headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:57.0) Gecko/20100101 Firefox/57.0",}
    rr = requests.get(TARGET_URL, headers=headers)
    html = rr.content
    try:
        soup = BeautifulSoup(html, "html.parser")
        list_pref = list(PROVCODE.keys()) # 都道府県名のリスト(PROVCODEからKeyを抽出してリスト化)
        # HTMLの<a>タグを抽出
        for aa in soup.find_all('a'):
            # リンク先とリンクの表示名を取得（リンク表示名は都道府県名になっている）
            name = aa.get_text()
            link = base_url + aa.get('href')
            if '.pdf' in link and list_pref.count(name) == 1:
                # 辞書に要素を追加 Key:表示名(=都道府県名)、Value=リンク先のURL
                dict_pdf_link[name] = link
    except Exception as ee:
        print(str(ee.__class__.__name__) + ' : ' + str(ee))

    #--------------------------------------------
    # PDFをダウンロード
    #  [I] dict_pdf_link
    #  [O] dict_file_name
    #--------------------------------------------
    global dict_file_name
    time_start = time.perf_counter()
    count = 0
    print('[PDFをダウンロード]')
    dict_file_name = dict()
    for pref, link in dict_pdf_link.items(): # 都道府県でループ
        # ダウンロード
        file = '{0:02}_{1}.pdf'.format(PROVCODE[pref], pref)
        urllib.request.urlretrieve(link, READ_FILE_DIR + "\\" + file)
        dict_file_name[pref] = file
        print('  {0}'.format(file))
        # サーバーに負荷を掛けすぎないようにするためにスリープ
        time.sleep(0.5)
        #----- 進捗表示 -----
        count += 1
    print("完了 ---> time:{0:.3f}".format(time.perf_counter() - time_start) + "[sec]")

    #--------------------------------------------
    # PDFのファイル名にファイル作成日を追加
    #  [I] dict_file_name
    #--------------------------------------------
    for pref, file in dict_file_name.items():
        with open(READ_FILE_DIR + '\\' + file, mode='rb') as f:
            reader = PyPDF2.PdfFileReader(f)
            docinfo = reader.getDocumentInfo()
            pdf_date = docinfo['/CreationDate']
        new_path = READ_FILE_DIR+'\\'+pdf_date[2:10]+'_'+file
        os.rename(READ_FILE_DIR+'\\'+file, new_path)
        print('{0} {1}'.format(file, new_path))
        

if __name__ == "__main__":
    main_time_start = time.perf_counter()
    main()
    print ("\n===> 正常終了 (処理時間:{0:.3f}[sec])".format(time.perf_counter() - main_time_start ))


