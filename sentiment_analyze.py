import random

from transformers import TFBertForSequenceClassification
from transformers import BertConfig
from transformers import pipeline
import transformers

import numpy as np
import pandas as pd

class SA_Model:
    def __init__(self, path):
        # 加载模型配置
        config = BertConfig.from_pretrained(f'{path}/trained_model')

        # 创建模型并加载权重
        model = TFBertForSequenceClassification.from_pretrained(f'{path}/trained_model', config=config)
        model.summary()

        tokenizer = transformers.BertTokenizer.from_pretrained(f"{path}/vocab.txt")
        self.classifier = pipeline('sentiment-analysis', model=model, tokenizer=tokenizer)

    def sentiment_analyze(self, text):
        scores = []
        sub_len = len(text) // 400 + 1
        for i in range(sub_len):
            sub_text = text[i * 400:(i + 1) * 400]
            res = self.classifier(sub_text)[0]
            s = res['score']
            if res['label'] == 'LABEL_0':  # neg
                s = -s
            scores.append(s)

        return np.mean(scores)


def run():
    MODEL_PATH = "."
    sa = SA_Model(MODEL_PATH)

    # 创建一个线程安全的队列来收集处理后的数据
    flag = []
    value = []

    df = pd.read_csv("data/comments.csv")
    # id = 0
    L = 0               #id * 45000
    R = len(df)         #min((id + 1) * 45000, len(df))
    df = df.iloc[L:R]
    print(f"process segment[{L}:{R}]")
    for index, row in df.iterrows():
        if index % 500 == 0:
            print("analyzing", index)
        text = row['content']
        v = sa.sentiment_analyze(text)
        value.append(v)
        flag.append(1 if v >= 0 else 0)

    df['popularity'] = flag
    df['precise_value'] = value

    df.to_csv(f"data/sentiment.csv", index=False)


if __name__ == "__main__":
    run()
    # MODEL_PATH = "."
    # sa = SA_Model(MODEL_PATH)
    # text = '2024年以来，启迪环境已连发4次关于其全资子公司、子公司收到《行政处罚决定书》的公告'
    # print(sa.sentiment_analyze(text))