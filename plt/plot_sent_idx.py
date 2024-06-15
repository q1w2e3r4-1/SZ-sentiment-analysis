
import pandas as pd
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
mpl.rcParams['axes.unicode_minus'] = False

if __name__ == '__main__':
    plt.rcParams['font.sans-serif'] = ['SimHei']  # 设置默认字体
    plt.rcParams['axes.unicode_minus'] = False  # 解决保存图像时负号’-‘显示为方块的问题

    df = pd.read_csv('merged_sentiment_idx.csv', parse_dates=['date'])
    df.set_index(df.date, inplace=True)
    df = df.loc['2023-6-13':'2024-6-13']

    fig, ax1 = plt.subplots(figsize=(10, 6))
    ax2 = ax1.twinx()

    line1, = ax1.plot(df.index.to_numpy(), df['BI_MA'].to_numpy(), color='#FFA500', linestyle=':')
    line2, = ax2.plot(df.index.to_numpy(), df['close'].to_numpy(), color='#87CEFA')

    ax1.legend([line1, line2], ['BI指标', '上证指数'], loc='upper left')

    ax1.set_xlabel('日期')
    ax1.set_ylabel('BI指标')
    ax2.set_ylabel('上证指数')

    plt.tight_layout()
    plt.savefig('image.png')
    plt.show()

