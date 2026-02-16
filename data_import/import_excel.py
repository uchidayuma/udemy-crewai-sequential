import pandas as pd


def import_excel(file_path):
    df = pd.read_excel(file_path)

    # 必要なカラムのみを抽出
    necessary_columns = ['customer_name', 'company_name']
    return df[necessary_columns]
