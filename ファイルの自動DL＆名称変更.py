
import pandas as pd
import time
import PyPDF2
import datetime
import urllib.request

import sys
import os
import requests
import dateutil.parser
from bs4 import BeautifulSoup



#----- 入力ファイル -----
# Excel
READ_FILE_DIR = r'C:\Users\e12135\Downloads\DL2'
CTRL_PORTABLE = True if not os.path.isdir(READ_FILE_DIR) else False
READ_FILE_DIR = os.getcwd() if CTRL_PORTABLE else READ_FILE_DIR # フォルダが存在しないときはカレントフォルダ

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
    global temp1, temp2, temp3

    #
    base_url = 'https://www.mhlw.go.jp'
    url = 'https://www.mhlw.go.jp/stf/seisakunitsuite/bunya/kenkou_iryou/iryou/rinsyo/index_00014.html'
    headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:57.0) Gecko/20100101 Firefox/57.0",}
    
    # ダウンロードリスト作成
    global dict_pdf_link
    list_pref = list(PROVCODE.keys())
    dict_pdf_link = dict()
    try:
        rr = requests.get(url, headers=headers)
        html = rr.content
        try:
            soup = BeautifulSoup(html, "html.parser")
            for aa in soup.find_all("a"):
                link = base_url + aa.get("href")
                name = aa.get_text()
                if '.pdf' in link and list_pref.count(name) == 1:
                    dict_pdf_link[name] = link
        except Exception as ee:
            sys.stderr.write("*** error *** in BeautifulSoup ***\n")
            sys.stderr.write(str(ee) + "\n")
    except Exception as ee:
        sys.stderr.write("*** error *** in requests.get ***\n")
        sys.stderr.write(str(ee) + "\n")

    # PDFをダウンロード
    global dict_file_name
    time_start = time.perf_counter()
    count = 0
    dict_file_name = dict()
    for pref, link in dict_pdf_link.items():
        # ダウンロード
        file = '{0:02}_{1}.pdf'.format(PROVCODE[pref], pref)
        urllib.request.urlretrieve(link, READ_FILE_DIR + "\\" + file)
        dict_file_name[pref] = file
        # サーバーに負荷を掛けすぎないようにするためにスリープ
        time.sleep(0.5)
        #----- 進捗表示 -----
        count += 1
        print('\r[PDFをダウンロード] {0}/{1}'.format(count, len(dict_pdf_link)), end="")
    print(" ---> time:{0:.3f}".format(time.perf_counter() - time_start) + "[sec]")

    # PDFのファイル名にファイル作成日を追加
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


