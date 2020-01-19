import urllib.request
import json
import urllib.request
import json
import pandas as pd
from pandas.io.json import json_normalize

##################
# e-Stat のAPIの吐き出し内容の確認用
# https://www.e-stat.go.jp/api/sample/testform/getStatsData-json.html

##################
# e-Stat APIのappId
appId = ''

#################
## APIのリクエストURL

#2001~2014
url_old = 'https://api.e-stat.go.jp/rest/2.1/app/getStatsData?appId=&lang=J&statsDataId=0003016267&metaGetFlg=Y&cntGetFlg=N&sectionHeaderFlg=1'
#2015~
url_new ='http://api.e-stat.go.jp/rest/2.1/app/getStatsData?appId=&lang=J&statsDataId=0003139654&metaGetFlg=Y&cntGetFlg=N&sectionHeaderFlg=1'

url = url_old

#URLをJSON取得用に変更
def url_json(url):
    return url.replace('/app/', '/app/json/')

#URLにappIdを設定
def set_appid(url):
    return url.replace('appId=', 'appId=' + appId)

#URLに地域の絞り込み条件を追加
def narrow_down(url):

    #時間の絞り込み条件
    """
    time_cd = ['2002000000','2003000000','2004000000',\
               '2005000000','2006000000','2007000000',\
               '2008000000','2009000000','2010000000',\
               '2011000000','2012000000','2013000000',\
               '2014000000']
    time_cd = [str(i) for i in time_cd]
    """
#    time_cd = '2010000000'

    #地域の絞り込み条件
    area_cd = ['01100','02201','03201','04100','05201','06201','07201','08201','09201','10201',\
               '11100','12100','13100','14100','15100','16201','17201','18201','19201','20201',\
               '21201','22100','23100','24201','25201','26100','27100','28100','29201','30201',\
               '31201','32201','33100','34100','35203','36201','37201','38201','39201','40130',\
               '41201','42201','43201','44201','45201','46201','47201']
    """
    札幌市,青森市,盛岡市,仙台市,秋田市,山形市,福島市,水戸市,宇都宮市,前橋市
    さいたま市,千葉市,特別区部,横浜市,新潟市,富山市,金沢市,福井市,甲府市,長野市
    岐阜市,静岡市,名古屋市,津市,大津市,京都市,大阪市,神戸市,奈良市,和歌山市
    鳥取市,松江市,岡山市,広島市,山口市,徳島市,高松市,松山市,高知市,福岡市
    佐賀市,長崎市,熊本市,大分市,宮崎市,鹿児島市,那覇市
    """
    area_cd = [str(i) for i in area_cd]

    #内容の絞り込み条件
    Cat01_cd = ['04041','04042','04043']
    """
    電気洗濯機(2槽式)(1台)
    電気洗濯機(全自動洗濯機)(1台)
    電気洗濯機(全自動洗濯乾燥機)(1台)
    """
#    return url + '&cdTime=' + ','.join(time_cd)\
    return url + '&lvTime=1'\
               + '&cdArea=' + ','.join(area_cd)\
               + '&cdCat01=' + ','.join(Cat01_cd)

#dataの取得
def get_estat_json():
    request_url = narrow_down(set_appid(url_json(url)))
    with urllib.request.urlopen(request_url) as f:
        res = json.loads(f.read().decode('utf8'))
    return res

def to_dataframe(res):
    item = [] # 品目のリスト
    pref = [] # 都道府県のリスト
    yymm = [] # 年月のリスト
    for obj in res['GET_STATS_DATA']['STATISTICAL_DATA']['CLASS_INF']['CLASS_OBJ']:
        # 分類などの出力
        if isinstance(obj['CLASS'], dict): # dict
            print(obj['@id'], obj['@name'], obj['CLASS']['@name'])
        else: #list
            id = obj['@id']
            for cat in obj['CLASS']:
                print(id, obj['@name'], cat['@name'], cat['@code'])
                if id == 'cat01': # 品目分類
                    item.append(cat['@name'])
                elif id == 'area': # 地域
                    pref.append(cat['@name'])
                elif id == 'time': # 年月
                    yymm.append(cat['@name'])


    # JSONをDataFrameに変換
    df = pd.DataFrame(res['GET_STATS_DATA']['STATISTICAL_DATA']['DATA_INF']['VALUE'])
    #df = json_normalize(res['GET_STATS_DATA']['STATISTICAL_DATA']['DATA_INF']['VALUE'])
    #df = df.loc[:, ['$', '@area', '@cat01', '@time']]
    return df


df = to_dataframe(get_estat_json())
df.drop("@tab",axis=1).pivot(index="@area", columns="@cat01")
#df = to_dataframe(get_estat_json())
#a=df[df["@time"].str[-4:]=="0000"]
#b=a[a["@time"].str[:4]=="2014"]
#print(b.drop("@time",axis=1).pivot(index="@area", columns="@cat01"))

