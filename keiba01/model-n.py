import pandas as pd
import datetime
res = pd.read_csv("keiba1.csv")
results = res.fillna(0)
def preprocessing(results):
    df = results.copy()
    # 着順に数字以外の文字列が含まれているものを取り除く
    df = df[~(df["着順"].astype(str).str.contains("\D"))]
    df["着順"] = df["着順"].astype(int)
    # 性齢を性と年齢に分ける
    df["性"] = df["性齢"].map(lambda x: str(x)[0])
    df["年齢"] = df["性齢"].map(lambda x: str(x)[1:]).astype(int)
    # 馬体重を体重と体重変化に分ける
    df["体重"] = df["馬体重（増減）"].str.split("(", expand=True)[0].astype(int)
    df["体重変化"] = df["馬体重（増減）"].str.split("(", expand=True)[1].str[:-1].astype(int)
    # データをint, floatに変換
    df["単勝オッズ"] = df["単勝オッズ"].astype(float)
    # 不要な列を削除
    df.drop(["タイム", "着差", "性齢","後3F", "馬体重（増減）"], axis=1, inplace=True)
    #df["date"] = pd.to_datetime(df["date"], format="%Y年%m月%d日")
    return df
results_p = preprocessing(results)
def split_data(df, test_size=0.3):
    sorted_id_list = df.sort_values("date").index.unique()
    train_id_list = sorted_id_list[: round(len(sorted_id_list) * (1 - test_size))]
    test_id_list = sorted_id_list[round(len(sorted_id_list) * (1 - test_size)) :]
    train = df.loc[train_id_list].drop(['date'], axis=1)
    test = df.loc[test_id_list].drop(['date'], axis=1)
    return train, test
results_p.drop(["馬名"], axis=1, inplace=True)

results_d = pd.get_dummies(results_p)
_labels = results_d.columns #ダミー変数返還後の列ラベルを格納
results_d["rank"] = results_d["着順"].map(lambda x: 1 if x < 4 else 0)
results_d.drop(['着順'], axis=1, inplace=True)
import lightgbm as lgb
from sklearn.model_selection import train_test_split
train, test= train_test_split(results_d,test_size=0.3)
X_train = train.drop(["rank"],axis=1)
y_train = train["rank"]
X_test = train.drop(["rank"],axis=1)
y_test = train["rank"]
print(X_train.columns) #列ラベル確認用(=入力変数の数)

params = {
    "num_leaves": 4,
    "n_estimators": 80,
    "class_weight": "balanced",
    "random_state": 100,
}
lgb_clf = lgb.LGBMClassifier(**params)
lgb_clf.fit(X_train.values, y_train.values)
from sklearn.metrics import roc_auc_score
y_pred_train = lgb_clf.predict_proba(X_train)[:, 1]
y_pred = lgb_clf.predict_proba(X_test)[:, 1]
print(roc_auc_score(y_train, y_pred_train))
print(roc_auc_score(y_test, y_pred))
importances = pd.DataFrame(
    {"features": X_train.columns,"importance": lgb_clf.feature_importances_}
)
imp = importances.sort_values("importance", ascending=False)[:20]
print(imp)
results_test = pd.read_csv("keiba_test8.csv")
result_t = preprocessing(results_test)
result_t.drop(["馬名"],axis=1,inplace=True)
_labels1=result_t.columns #テストに用いる列ラベルの確認用
#新たにデータフレームを作成 テスト用列ラベル＋学習用列ラベル(ダミー変数増加分)
result_tp=pd.DataFrame(result_t,columns=_labels1)
data = pd.DataFrame(index=range(result_t.shape[0]), columns=_labels[9:])
result_tp=pd.concat([result_tp,data],axis=1)

result_tp=result_tp.fillna(0) #NaNを0に変換
import re
for _x,_label in enumerate(_labels):
    for _y in range(result_tp.shape[0]):
        if result_tp.at[_y,_label] == 0:
            for _x1 in range(_x + 1):
                if re.search(str(result_tp.iat[_y,_x1]),_label) != None:
                    result_tp.at[_y,_label] = 1
print(result_tp)
#共通でない要素を出力
l1_l2_sym_diff = set(X_train.columns) ^ set(result_tp.columns)
print(l1_l2_sym_diff)
for _diff in l1_l2_sym_diff:
    result_tp.drop(_diff,axis=1,inplace=True)
print(result_tp.head())
y_pred_test = lgb_clf.predict_proba(result_tp)[:,1]
print(y_pred_test)


df = pd.DataFrame(y_pred_test,columns=["勝率"],index=results_test["馬名"])
df = df.sort_values("勝率",ascending=False)
print(df)

import pickle
file = "model3.pkl"
clf = pickle.dump(lgb_clf,open(file,"wb"))
