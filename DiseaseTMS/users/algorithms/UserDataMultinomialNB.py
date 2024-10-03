from django.conf import settings
class DiseaseDiagnosis:
    # Process Disease and Symptom Names
    def process_name(self,data):
        data_list = []
        data_name = data.replace('^', '_').split('_')
        n = 1
        for names in data_name:
            if n % 2 == 0:
                data_list.append(names)
            n += 1
        return data_list
    def startNBProcess(self):
        import csv
        import numpy as np
        import pandas as pd
        import pickle
        from collections import defaultdict
        from sklearn.naive_bayes import MultinomialNB
        # read in the raw scrapped data
        path = settings.MEDIA_ROOT + "\\" + "raw_data.xlsx"
        data = pd.read_excel(path)
        print(data.head())
        data = data.fillna(method='ffill')
        data.head()
        list(data)
        disease_list = []
        disease_symptom_dict = defaultdict(list)
        disease_symptom_count = {}
        count = 0

        for idx, row in data.iterrows():

            # Get the Disease Names
            if (row['Disease'] != "\xc2\xa0") and (row['Disease'] != ""):
                disease = row['Disease']
                disease_list = self.process_name(data=disease)
                count = row['Count of Disease Occurrence']

            # Get the Symptoms Corresponding to Diseases
            if (row['Symptom'] != "\xc2\xa0") and (row['Symptom'] != ""):
                symptom = row['Symptom']
                symptom_list = self.process_name(data=symptom)
                for d in disease_list:
                    for s in symptom_list:
                        disease_symptom_dict[d].append(s)
                    disease_symptom_count[d] = count

        # Saving the cleaned data
        dataset_path = settings.MEDIA_ROOT + "\\" + "dataset_clean.csv"
        with open(dataset_path, 'w') as csvfile:
            writer = csv.writer(csvfile)
            for key, value in disease_symptom_dict.items():
                for v in value:
                    key = str.encode(key).decode('utf-8')
                    writer.writerow([key, v, disease_symptom_count[key]])

        columns = ['Source', 'Target', 'Weight']
        data = pd.read_csv(dataset_path, names=columns, encoding='ISO-8859-1')
        print(data.head())
        data.to_csv(dataset_path, index=False)
        unique_diseases = data['Source'].unique()
        print('No. of diseases:', len(unique_diseases))
        print('Disease:')
        for disease in unique_diseases:
            print(disease)

        unique_symptoms = data['Target'].unique()
        print('No. of symptoms', len(unique_symptoms))
        print('Symptoms:')
        for symptom in unique_symptoms:
            print(symptom)

        df_1 = pd.get_dummies(data.Target)
        df_1.head()
        df_s = data['Source']
        df_pivoted = pd.concat([df_s, df_1], axis=1)
        df_pivoted.drop_duplicates(keep='first', inplace=True)
        df_pivoted = df_pivoted.groupby('Source', sort=False).sum()
        df_pivoted = df_pivoted.reset_index()
        df_pivoted.head()
        len(df_pivoted)

        df_pivoted_path = settings.MEDIA_ROOT + "\\" + "df_pivoted.csv"
        df_pivoted.to_csv(df_pivoted_path)
        x = df_pivoted[df_pivoted.columns[1:]]
        y = df_pivoted['Source']
        print(x[:5])
        print(y[:5])

        # Computing prior probabilities of classes from weights
        weights = np.fromiter(disease_symptom_count.values(), dtype=float)
        total = sum(weights)
        prob = weights / total
        print(prob)

        mnb_tot = MultinomialNB()
        mnb_tot = mnb_tot.fit(x, y)
        score_NB = mnb_tot.score(x, y)
        print("Nb Score ",score_NB)
        # finding where the model fails
        disease_pred = mnb_tot.predict(x)

        disease_real = y.values
        score_NB_dict = {}
        for i in range(0, len(disease_real)):
            if disease_pred[i] != disease_real[i]:
                print('Pred:', disease_pred[i])
                print('Actual:', disease_real[i])
                score_NB_dict.update({disease_pred[i]:disease_real[i]})
                print('##########################')

        # Using class prior prob
        mnb_prob = MultinomialNB(class_prior=prob)
        mnb_prob = mnb_prob.fit(x, y)
        score_prob = mnb_prob.score(x, y)
        print("Score is ",score_prob)

        disease_pred = mnb_prob.predict(x)
        score_Prob_dict = {}
        for i in range(0, len(disease_real)):
            if disease_pred[i] != disease_real[i]:
                print('Pred:', disease_pred[i])
                print('Actual:', disease_real[i])
                score_Prob_dict.update({disease_pred[i]:disease_real[i]})
                print('##########################')

        ## Saving the Naive Bayes Model
        filename = settings.MEDIA_ROOT + "\\" + 'NB_model.sav'
        pickle.dump(mnb_tot, open(filename, 'wb'))
        # Load model and predict
        model = pickle.load(open(filename, 'rb'))
        # model.predict([100*[1]+100*[0]+204*[0]])
        symptoms = df_pivoted.columns[1:].values
        print(symptoms)
        # test_input = [0] * 404
        # user_symptoms = list(input().split(','))
        # for symptom in user_symptoms:
        #     test_input[np.where(symptoms == symptom)[0][0]] = 1
        # print('Most probable disease:', model.predict([test_input]))
        return score_NB, score_prob, score_NB_dict, score_Prob_dict






