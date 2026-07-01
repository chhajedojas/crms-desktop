"""
Analyze the dataset analysis CSV and generate a detailed report.
"""

import csv
from collections import defaultdict


def analyze_csv(csv_path: str):
    """Analyze the CSV and generate statistics."""
    with open(csv_path, "r") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    # Group by document type
    doc_types = defaultdict(int)
    low_confidence_by_type = defaultdict(int)
    errors_by_type = defaultdict(list)
    errors_by_reason = defaultdict(int)
    low_confidence_files = []

    for row in rows:
        doc_type = row["Document Type"]
        doc_types[doc_type] += 1

        confidence = float(row["Confidence"])
        if confidence < 0.9:
            low_confidence_by_type[doc_type] += 1
            low_confidence_files.append(
                {
                    "file": row["File Name"],
                    "type": doc_type,
                    "confidence": confidence,
                    "errors": row["Errors"],
                }
            )

        if row["Errors"]:
            errors_by_type[doc_type].append(row["Errors"])
            errors_by_reason[row["Errors"]] += 1

    # Calculate accuracy by document type
    accuracy_by_type = {}
    for doc_type, count in doc_types.items():
        low_conf = low_confidence_by_type[doc_type]
        accuracy = (count - low_conf) / count if count > 0 else 0
        accuracy_by_type[doc_type] = accuracy

    return {
        "total_files": len(rows),
        "doc_types": dict(doc_types),
        "low_confidence_by_type": dict(low_confidence_by_type),
        "errors_by_type": dict(errors_by_type),
        "errors_by_reason": dict(errors_by_reason),
        "accuracy_by_type": accuracy_by_type,
        "low_confidence_files": low_confidence_files,
    }


if __name__ == "__main__":
    stats = analyze_csv("/Users/ojas/Documents/ojas/crms/dataset_analysis.csv")

    print("\n" + "=" * 80)
    print("DATASET ANALYSIS")
    print("=" * 80)
    print(f"\nTotal Files: {stats['total_files']}")
    print("\nDocument Types:")
    for doc_type, count in sorted(stats["doc_types"].items()):
        accuracy = stats["accuracy_by_type"][doc_type]
        print(f"  {doc_type}: {count} (Accuracy: {accuracy:.2%})")

    print("\nLow Confidence by Type:")
    for doc_type, count in sorted(stats["low_confidence_by_type"].items()):
        print(f"  {doc_type}: {count}")

    print("\nError Reasons:")
    for error, count in sorted(stats["errors_by_reason"].items(), key=lambda x: -x[1])[:10]:
        print(f"  {count}x: {error[:80]}")

    print("\n" + "=" * 80)
