"""
Analyze classification results and generate metrics.
"""

import csv
from collections import defaultdict


def analyze_classification_results(csv_path: str):
    """Analyze classification results."""
    with open(csv_path, "r") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    # Confusion matrix
    confusion_matrix = defaultdict(lambda: defaultdict(int))
    type_counts = defaultdict(int)
    predicted_counts = defaultdict(int)
    correct_by_type = defaultdict(int)

    for row in rows:
        ground_truth = row["ground_truth"]
        predicted = row["predicted"]
        is_correct = row["is_correct"] == "True"

        confusion_matrix[ground_truth][predicted] += 1
        type_counts[ground_truth] += 1
        predicted_counts[predicted] += 1
        if is_correct:
            correct_by_type[ground_truth] += 1

    # Calculate metrics per type
    metrics = {}
    for doc_type in type_counts:
        tp = confusion_matrix[doc_type][doc_type]
        fp = sum(confusion_matrix[gt][doc_type] for gt in confusion_matrix if gt != doc_type)
        fn = sum(confusion_matrix[doc_type][pred] for pred in confusion_matrix[doc_type] if pred != doc_type)

        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0
        f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        accuracy = correct_by_type[doc_type] / type_counts[doc_type] if type_counts[doc_type] > 0 else 0

        metrics[doc_type] = {
            "precision": precision,
            "recall": recall,
            "f1": f1,
            "accuracy": accuracy,
            "count": type_counts[doc_type],
        }

    # Confidence distribution
    confidence_distribution = defaultdict(int)
    for row in rows:
        conf = float(row["confidence"])
        if conf >= 0.9:
            confidence_distribution["90-100%"] += 1
        elif conf >= 0.8:
            confidence_distribution["80-89%"] += 1
        elif conf >= 0.7:
            confidence_distribution["70-79%"] += 1
        elif conf >= 0.6:
            confidence_distribution["60-69%"] += 1
        elif conf >= 0.5:
            confidence_distribution["50-59%"] += 1
        else:
            confidence_distribution["<50%"] += 1

    # Misclassification reasons
    misclassifications = [row for row in rows if row["is_correct"] == "False"]
    misclassification_reasons = defaultdict(int)
    for row in misclassifications:
        reason = row["reasons"][:100]  # Truncate long reasons
        misclassification_reasons[reason] += 1

    return {
        "confusion_matrix": dict(confusion_matrix),
        "metrics": metrics,
        "confidence_distribution": dict(confidence_distribution),
        "misclassification_reasons": dict(misclassification_reasons),
        "total_files": len(rows),
        "correct_count": sum(1 for row in rows if row["is_correct"] == "True"),
    }


if __name__ == "__main__":
    stats = analyze_classification_results("/Users/ojas/Documents/ojas/crms/classification_results.csv")

    print("\n" + "=" * 80)
    print("CLASSIFICATION METRICS")
    print("=" * 80)
    print(f"\nTotal Files: {stats['total_files']}")
    print(f"Correct: {stats['correct_count']}")
    print(f"Accuracy: {stats['correct_count'] / stats['total_files']:.2%}")

    print("\n" + "-" * 80)
    print("CONFUSION MATRIX")
    print("-" * 80)
    print("Predicted ->")
    print("Actual    |", end="")
    for pred in sorted(stats["confusion_matrix"].keys()):
        print(f" {pred[:15]:<15}", end="")
    print()
    print("-" * 80)
    for actual in sorted(stats["confusion_matrix"].keys()):
        print(f"{actual[:15]} |", end="")
        for pred in sorted(stats["confusion_matrix"].keys()):
            count = stats["confusion_matrix"][actual].get(pred, 0)
            print(f" {count:<15}", end="")
        print()

    print("\n" + "-" * 80)
    print("PER-TYPE METRICS")
    print("-" * 80)
    print(f"{'Type':<20} {'Count':<8} {'Accuracy':<10} {'Precision':<10} {'Recall':<10} {'F1':<10}")
    print("-" * 80)
    for doc_type, metrics in sorted(stats["metrics"].items()):
        print(
            f"{doc_type[:20]:<20} {metrics['count']:<8} {metrics['accuracy']:<10.2%} {metrics['precision']:<10.2%} {metrics['recall']:<10.2%} {metrics['f1']:<10.2%}"
        )

    print("\n" + "-" * 80)
    print("CONFIDENCE DISTRIBUTION")
    print("-" * 80)
    for range_name, count in sorted(stats["confidence_distribution"].items()):
        print(f"  {range_name}: {count}")

    print("\n" + "-" * 80)
    print("MISCLASSIFICATION REASONS")
    print("-" * 80)
    for reason, count in sorted(stats["misclassification_reasons"].items(), key=lambda x: -x[1])[:10]:
        print(f"  {count}x: {reason}")

    print("\n" + "=" * 80)
