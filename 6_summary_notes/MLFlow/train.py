import mlflow
import mlflow.sklearn
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report
import pandas as pd
import numpy as np
from mlflow.models.signature import infer_signature

# KAYIT YERİ: /app/mlruns  (host: C:\Users\yusuf\mlruns)
mlflow.set_tracking_uri("file:/app/mlruns")
mlflow.set_experiment("Iris-Classification")

# Veri
data = load_iris(as_frame=True)
X = data.data.copy()
y = data.target

# Bilerek biraz gürültü ekleyelim ki accuracy 1.0 olmasın
rng = np.random.RandomState(7)
rows = rng.choice(X.index, size=10, replace=False)
X.loc[rows, :] = X.loc[rows, :] + rng.normal(0, 0.6, size=(len(rows), X.shape[1]))

# Train/Test
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.7, random_state=42, stratify=y
)

with mlflow.start_run(run_name="logreg_liblinear"):
    params = {"C": 0.3, "solver": "liblinear", "max_iter": 200}
    clf = LogisticRegression(**params)
    clf.fit(X_train, y_train)
    y_pred = clf.predict(X_test)

    acc = accuracy_score(y_test, y_pred)
    print("Accuracy:", round(acc, 4))
    print(classification_report(y_test, y_pred, target_names=data.target_names))

    # Logla
    mlflow.log_params(params)
    mlflow.log_metric("accuracy", float(acc))

    sig = infer_signature(X_test, clf.predict(X_test))
    mlflow.sklearn.log_model(clf, artifact_path="model",
                             input_example=X_test.iloc[:5], signature=sig)

    # Raporu artifact olarak ekle
    report_txt = classification_report(y_test, y_pred, target_names=data.target_names)
    with open("/app/report.txt", "w") as f:
        f.write(report_txt)
    mlflow.log_artifact("/app/report.txt")

print("Tracking URI =>", mlflow.get_tracking_uri())
