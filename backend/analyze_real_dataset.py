"""
Real dataset analysis script.

This script scans the CRMS_DEV_DATASET, runs metadata extraction,
and produces a CSV report with extraction results.
"""

import os
import csv
from pathlib import Path
from datetime import datetime
from accounting.accounting_extractor import AccountingMetadataExtractor


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


def get_document_type(file_path: str) -> str:
    """Determine document type from file path."""
    path_lower = file_path.lower()
    if "tax_invoice" in path_lower or "invoice" in path_lower:
        return "Tax Invoice"
    elif "salary" in path_lower:
        return "Salary Slip"
    elif "statement" in path_lower:
        return "Bank Statement"
    elif "ledger" in path_lower:
        return "Ledger"
    else:
        return "Unknown"


def analyze_dataset(dataset_path: str, output_csv: str):
    """Analyze the CRMS_DEV_DATASET."""
    extractor = AccountingMetadataExtractor()

    # Initialize CSV output
    with open(output_csv, "w", newline="", encoding="utf-8") as csvfile:
        fieldnames = [
            "File Name",
            "Document Type",
            "Invoice Number",
            "GSTIN",
            "PAN",
            "Customer",
            "Vendor",
            "Invoice Date",
            "Amount",
            "Confidence",
            "Errors",
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        # Process all files
        total_files = 0
        success_count = 0
        low_confidence_count = 0
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

                # Extract text
                if file_ext == ".pdf":
                    text = extract_text_from_pdf(file_path)
                elif file_ext in [".xlsx", ".xls"]:
                    text = extract_text_from_excel(file_path)
                else:
                    text = "ERROR: Unsupported format"

                # Check for extraction errors
                if text.startswith("ERROR:"):
                    error_count += 1
                    row = {
                        "File Name": file,
                        "Document Type": get_document_type(file_path),
                        "Invoice Number": None,
                        "GSTIN": None,
                        "PAN": None,
                        "Customer": None,
                        "Vendor": None,
                        "Invoice Date": None,
                        "Amount": None,
                        "Confidence": 0.0,
                        "Errors": text,
                    }
                    writer.writerow(row)
                    continue

                # Extract metadata
                try:
                    fields = extractor.extract_all(text)

                    # Calculate average confidence
                    confidences = [f.confidence for f in fields.values() if f is not None]
                    avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0

                    # Check if confidence is below 90%
                    if avg_confidence < 0.9:
                        low_confidence_count += 1

                    # Get field values
                    invoice_number = fields.get("invoice_number")
                    gstin = fields.get("gstin")
                    pan = fields.get("pan")
                    customer = fields.get("customer_name")
                    vendor = fields.get("vendor_name")
                    invoice_date = fields.get("invoice_date")
                    amount = fields.get("amount")

                    # Collect errors
                    errors = []
                    for field_name, field in fields.items():
                        if field and field.validation_status.value == "invalid":
                            errors.append(f"{field_name}: {field.validation_errors}")

                    success_count += 1

                    row = {
                        "File Name": file,
                        "Document Type": get_document_type(file_path),
                        "Invoice Number": invoice_number.value if invoice_number else None,
                        "GSTIN": gstin.value if gstin else None,
                        "PAN": pan.value if pan else None,
                        "Customer": customer.value if customer else None,
                        "Vendor": vendor.value if vendor else None,
                        "Invoice Date": invoice_date.value.isoformat() if invoice_date and hasattr(invoice_date.value, 'isoformat') else str(invoice_date.value) if invoice_date else None,
                        "Amount": amount.value if amount else None,
                        "Confidence": round(avg_confidence, 2),
                        "Errors": "; ".join(errors) if errors else "",
                    }
                    writer.writerow(row)

                except Exception as e:
                    error_count += 1
                    row = {
                        "File Name": file,
                        "Document Type": get_document_type(file_path),
                        "Invoice Number": None,
                        "GSTIN": None,
                        "PAN": None,
                        "Customer": None,
                        "Vendor": None,
                        "Invoice Date": None,
                        "Amount": None,
                        "Confidence": 0.0,
                        "Errors": f"EXTRACTION ERROR: {str(e)}",
                    }
                    writer.writerow(row)

    # Print summary
    print("\n" + "=" * 80)
    print("ANALYSIS SUMMARY")
    print("=" * 80)
    print(f"Total Files Processed: {total_files}")
    print(f"Successful Extractions: {success_count}")
    print(f"Errors: {error_count}")
    print(f"Low Confidence (<90%): {low_confidence_count}")
    print(f"Output CSV: {output_csv}")
    print("=" * 80)


if __name__ == "__main__":
    dataset_path = "/Users/ojas/Documents/ojas/CRMS_DEV_DATASET"
    output_csv = "/Users/ojas/Documents/ojas/crms/dataset_analysis.csv"

    analyze_dataset(dataset_path, output_csv)
