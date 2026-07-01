"""
Validate document type detection on the 608-document dataset.
"""

import csv
import os
from classifier.document_type_detector import DocumentTypeDetector, DocumentType


def extract_text_from_pdf(file_path: str) -> str:
    """Extract text from PDF file."""
    try:
        import PyPDF2

        with open(file_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return text
    except Exception as e:
        return f"ERROR: {str(e)}"


def extract_text_from_excel(file_path: str) -> str:
    """Extract text from Excel file."""
    try:
        import openpyxl

        wb = openpyxl.load_workbook(file_path, data_only=True)
        text = ""
        for sheet in wb.worksheets:
            for row in sheet.iter_rows(values_only=True):
                row_text = " ".join(str(cell) if cell is not None else "" for cell in row)
                text += row_text + "\n"
        return text
    except Exception as e:
        return f"ERROR: {str(e)}"


def get_ground_truth_type(file_path: str) -> DocumentType:
    """Get ground truth document type from file path."""
    path_lower = file_path.lower()
    if "tax_invoice" in path_lower or "invoice" in path_lower:
        return DocumentType.TAX_INVOICE
    elif "salary" in path_lower:
        return DocumentType.SALARY_SLIP
    elif "statement" in path_lower:
        return DocumentType.BANK_STATEMENT
    elif "ledger" in path_lower:
        return DocumentType.LEDGER
    else:
        return DocumentType.UNKNOWN


def validate_classification(dataset_path: str):
    """Validate document type detection on the dataset."""
    detector = DocumentTypeDetector()

    results = []
    total_files = 0
    correct_count = 0
    error_count = 0

    for root, dirs, files in os.walk(dataset_path):
        # Skip .DS_Store files
        files = [f for f in files if not f.startswith(".")]

        for file in files:
            file_path = os.path.join(root, file)
            file_ext = os.path.splitext(file)[1].lower()

            # Only process PDF and Excel files
            if file_ext not in [".pdf", ".xlsx", ".xls"]:
                continue

            total_files += 1
            print(f"Processing {total_files}: {file_path}")

            # Get ground truth
            ground_truth = get_ground_truth_type(file_path)

            # Extract text
            if file_ext == ".pdf":
                text = extract_text_from_pdf(file_path)
            elif file_ext in [".xlsx", ".xls"]:
                text = extract_text_from_excel(file_path)
            else:
                text = ""

            # Classify
            try:
                result = detector.classify(file_path, text)

                # Check if correct
                is_correct = result.document_type == ground_truth
                if is_correct:
                    correct_count += 1

                results.append(
                    {
                        "file": file,
                        "ground_truth": ground_truth.value,
                        "predicted": result.document_type.value,
                        "confidence": result.confidence,
                        "is_correct": is_correct,
                        "reasons": "; ".join(result.reasons),
                    }
                )
            except Exception as e:
                error_count += 1
                results.append(
                    {
                        "file": file,
                        "ground_truth": ground_truth.value,
                        "predicted": "ERROR",
                        "confidence": 0.0,
                        "is_correct": False,
                        "reasons": str(e),
                    }
                )

    # Calculate metrics
    accuracy = correct_count / total_files if total_files > 0 else 0

    # Print summary
    print("\n" + "=" * 80)
    print("CLASSIFICATION VALIDATION SUMMARY")
    print("=" * 80)
    print(f"Total Files: {total_files}")
    print(f"Correct: {correct_count}")
    print(f"Errors: {error_count}")
    print(f"Accuracy: {accuracy:.2%}")
    print("=" * 80)

    # Write results to CSV
    with open("/Users/ojas/Documents/ojas/crms/classification_results.csv", "w", newline="") as f:
        fieldnames = ["file", "ground_truth", "predicted", "confidence", "is_correct", "reasons"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print(f"Results written to: /Users/ojas/Documents/ojas/crms/classification_results.csv")

    return results, accuracy


if __name__ == "__main__":
    dataset_path = "/Users/ojas/Documents/ojas/CRMS_DEV_DATASET"
    results, accuracy = validate_classification(dataset_path)
