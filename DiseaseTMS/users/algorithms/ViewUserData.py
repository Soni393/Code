from django.conf import settings
class GetCleanedData:
    # Process Disease and Symptom Names
    def process_data(self,data):
        data_list = []
        data_name = data.replace('^', '_').split('_')
        n = 1
        for names in data_name:
            if (n % 2 == 0):
                data_list.append(names)
            n += 1
        return data_list
    def viewCleanedData(self):
        print("Hello Dude Working Great")
        test_data = settings.MEDIA_ROOT + "\\" + "test_data.csv"
        training_data = settings.MEDIA_ROOT + "\\" + "training_data.csv"
        raw_data = settings.MEDIA_ROOT + "\\" + "raw_data.xlsx"
        import csv
        import pandas as pd
        import numpy as np
        from collections import defaultdict
        import seaborn as sns
        import matplotlib.pyplot as plt
        df = pd.read_excel(raw_data)
        print(df.head())
        data = df.fillna(method='ffill')
        print(data.head())
        list(data)
        disease_list = []
        disease_symptom_dict = defaultdict(list)
        disease_symptom_count = {}
        count = 0

        for idx, row in data.iterrows():

            # Get the Disease Names
            if (row['Disease'] != "\xc2\xa0") and (row['Disease'] != ""):
                disease = row['Disease']
                disease_list = self.process_data(data=disease)
                count = row['Count of Disease Occurrence']

            # Get the Symptoms Corresponding to Diseases
            if (row['Symptom'] != "\xc2\xa0") and (row['Symptom'] != ""):
                symptom = row['Symptom']
                symptom_list = self.process_data(data=symptom)
                for d in disease_list:
                    for s in symptom_list:
                        disease_symptom_dict[d].append(s)
                    disease_symptom_count[d] = count
        # See that the data is Processed Correctly
        print(disease_symptom_dict)
        # Count of Disease Occurence w.r.t each Disease
        print(disease_symptom_count)

        f = open(settings.MEDIA_ROOT + "\\" +'cleaned_data.csv', 'w')

        with f:
            writer = csv.writer(f)
            for key, val in disease_symptom_dict.items():
                for i in range(len(val)):
                    writer.writerow([key, val[i], disease_symptom_count[key]])

        # Read Cleaned Data
        df = pd.read_csv(settings.MEDIA_ROOT + "\\" +'cleaned_data.csv',encoding='cp1252')
        df.columns = ['disease', 'symptom', 'occurence_count']
        print(df.head())
        df.to_csv(settings.MEDIA_ROOT + "\\" +'data.csv', index=False)
        from sklearn import preprocessing
        df = pd.read_csv(settings.MEDIA_ROOT + "\\" +'data.csv',encoding='cp1252')
        return df