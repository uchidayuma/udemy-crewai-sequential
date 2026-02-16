import pandas as pd


def import_csv(file_path):
    df = pd.read_csv(file_path)

    # NULL補完
    df.fillna({
        'last_purchase_date': '1970-01-01',
        'total_purchase': 0.0
    }, inplace=True)

    # 重複排除（company_name を基準）
    df.drop_duplicates(subset='company_name', inplace=True)

    return df
