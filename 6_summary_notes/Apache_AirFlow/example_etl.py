from __future__ import annotations

from airflow.decorators import dag, task
from datetime import datetime
from pathlib import Path
import csv
import random
import statistics

DATA_DIR = Path("/opt/airflow/data")

@dag(
    schedule=None,                  # Manuel tetiklenecek
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=["demo", "etl"],
    default_args={"owner": "airflow"},
)
def example_etl():
    @task()
    def extract() -> str:
        """Sahte veri üret ve raw CSV'ye yaz."""
        rows = [{"id": i, "value": random.randint(1, 100)} for i in range(1, 51)]
        out = DATA_DIR / "raw" / f"data_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}.csv"
        out.parent.mkdir(parents=True, exist_ok=True)
        with out.open("w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=["id", "value"])
            w.writeheader()
            w.writerows(rows)
        return str(out)

    @task()
    def transform(raw_path: str) -> dict:
        """CSV'yi oku, istatistikleri hesapla ve değer >=50 olanları filtrele."""
        with open(raw_path, newline="") as f:
            rows = list(csv.DictReader(f))
        values = [int(r["value"]) for r in rows]
        mean_val = sum(values) / len(values)
        median_val = statistics.median(values)
        high = [r for r in rows if int(r["value"]) >= 50]

        out = DATA_DIR / "processed" / "filtered.csv"
        out.parent.mkdir(parents=True, exist_ok=True)
        with out.open("w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=["id", "value"])
            w.writeheader()
            w.writerows(high)

        return {
            "processed_path": str(out),
            "count": len(high),
            "mean": mean_val,
            "median": median_val,
        }

    @task()
    def load(info: dict) -> str:
        """Özet raporu yaz."""
        report = DATA_DIR / "reports" / "report.txt"
        report.parent.mkdir(parents=True, exist_ok=True)
        report.write_text(
            "ETL Raporu\n"
            f"----------------------\n"
            f"Toplam satır (>=50): {info['count']}\n"
            f"Ortalama: {info['mean']:.2f}\n"
            f"Medyan: {info['median']}\n"
            f"Çıktı CSV: {info['processed_path']}\n"
        )
        return str(report)

    raw_csv = extract()
    stats = transform(raw_csv)
    load(stats)

etl_dag = example_etl()
