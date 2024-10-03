from django.conf import settings
class IdentifyDiseaseInsights:
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
    def preProcess(self):
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
        df.head()
        n_unique = len(df['symptom'].unique())
        print(n_unique)
        # TEST
        from sklearn.preprocessing import LabelEncoder
        from sklearn.preprocessing import OneHotEncoder

        label_encoder = LabelEncoder()
        integer_encoded = label_encoder.fit_transform(df['symptom'].astype(str))
        print(integer_encoded)

        onehot_encoder = OneHotEncoder(sparse=False)
        integer_encoded = integer_encoded.reshape(len(integer_encoded), 1)
        onehot_encoded = onehot_encoder.fit_transform(integer_encoded)
        print(onehot_encoded)

        onehot_encoded[0]

        len(onehot_encoded[0])
        cols = np.asarray(df['symptom'].unique())
        print(cols)
        df_ohe = pd.DataFrame(columns=cols)
        df_ohe.head()
        for i in range(len(onehot_encoded)):
            df_ohe.loc[i] = onehot_encoded[i]

        df_ohe.head()
        len(df_ohe)
        # Disease Dataframe
        df_disease = df['disease']
        df_disease.head()

        # Concatenate OHE Labels with the Disease Column
        df_concat = pd.concat([df_disease, df_ohe], axis=1)
        df_concat.head()

        df_concat.drop_duplicates(keep='first', inplace=True)
        df_concat.head()
        len(df_concat)
        cols = df_concat.columns
        #cols.dropna()
        print(cols)
        cols = cols[1:]
        # Since, every disease has multiple symptoms, combine all symptoms per disease per row
        df_concat = df_concat.groupby('disease').sum()
        df_concat = df_concat.reset_index()
        df_concat[:5]

        len(df_concat)
        df_concat.to_csv(settings.MEDIA_ROOT + "\\" +'final_data.csv', index=False)
        # One Hot Encoded Features
        #mask = dframe.Product.str.contains(word, case=False, na=False)
        print('Cols is ',type(df_concat))
        cols = cols.dropna(how='any')
        df_concat = df_concat.dropna(how='any')
        print(df_concat.head())
        X = df_concat[cols]

        # Labels
        y = df_concat['disease']
        from sklearn.model_selection import train_test_split
        from sklearn.naive_bayes import MultinomialNB
        from sklearn import tree
        from sklearn.tree import DecisionTreeClassifier, export_graphviz
        from sklearn.metrics import plot_confusion_matrix

        # Train Test Split
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=101)
        from sklearn.ensemble import RandomForestRegressor

        # create regressor object
        regressor = RandomForestRegressor(n_estimators=100, random_state=0)

        # fit the regressor with x and y data
        #regressor.fit(X_train, y_train)
        #plot_confusion_matrix(regressor, X_test, y_test)  # doctest: +SKIP
        #plt.show()

        len(X_train), len(y_train)
        len(X_test), len(y_test)
        dt = DecisionTreeClassifier()
        clf_dt = dt.fit(X, y)
        #plot_confusion_matrix(dt, X_test, y_test)  # doctest: +SKIP
        #plt.show()
        scre = clf_dt.score(X, y)
        print("Score is ",scre)

        fig = plt.figure(figsize=(25, 20))
        _ = tree.plot_tree(dt,
                           feature_names=cols,

                           filled=True)
        fig.savefig("decistion_tree.png")
        #plt.show()
        '''
        import graphviz
        # DOT data
        dot_data = tree.export_graphviz(dt, out_file=None,
                                        feature_names=cols,
                                        filled=True)

        # Draw graph
        graph = graphviz.Source(dot_data, format="png")
        print(graph)
        graph.render("decision_tree_graphivz")

        export_graphviz(dt,
                        out_file='./tree.dot',
                        feature_names=cols)

        from graphviz import Source
        from sklearn import tree

        graph = Source(export_graphviz(dt,
                                       out_file=None,
                                       feature_names=cols))

        dotfile = open('./tree1.dot', 'w')
        tree.export_graphviz(dt, out_file=dotfile, feature_names=X.columns)
        dotfile.close()

        png_bytes = graph.pipe(format='png')

        with open('tree.png', 'wb') as f:
            f.write(png_bytes)

        from IPython.display import Image
        Image(png_bytes)'''

        disease_pred = clf_dt.predict(X)
        disease_real = y.values
        predict ={}
        for i in range(0, len(disease_real)):
            if disease_pred[i] != disease_real[i]:
                print('Pred: {0} Actual:{1}'.format(disease_pred[i], disease_real[i]))
                predict.update({disease_pred[i]:disease_real[i]})

        return predict,scre

