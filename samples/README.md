# Sample Documents

This directory contains sample documents for testing and development purposes.

## Important Security Notice

**Never commit real business documents to this repository.**

Only store:
- Synthetic or generated documents
- Sanitized documents with all sensitive data removed
- Publicly available sample documents

## Directory Structure

```
samples/
├── invoices/           # Sample invoice documents
├── bank/              # Sample bank statements
├── gst/               # Sample GST-related documents
├── ledger/            # Sample ledger entries
├── salary/            # Sample salary slips
├── quotation/         # Sample quotations
├── purchase/          # Sample purchase orders
└── delivery_challan/  # Sample delivery challans
```

## Guidelines

### What to Include
- Synthetic documents generated for testing
- Documents with fictional companies and data
- Publicly available document templates
- Sanitized documents with all PII removed

### What NOT to Include
- Real business documents
- Documents with actual company names
- Documents with personal information
- Documents with financial data
- Documents with GSTINs or PANs
- Any sensitive or confidential information

### Sanitization Checklist

Before adding a document to this directory, ensure:

- [ ] All company names are fictional
- [ ] All addresses are fictional
- [ ] All phone numbers are fictional
- [ ] All email addresses are fictional
- [ ] All GSTINs are invalid/test numbers
- [ ] All PANs are invalid/test numbers
- [ ] All monetary amounts are test data
- [ ] No personal information present
- [ ] No confidential information present

## Creating Sample Documents

### Invoices
```python
# Use fictional company names
- Acme Corporation
- Example Industries
- Test Company Pvt Ltd
```

### GST Numbers
```python
# Use test GSTIN format (never real)
- 27AAAC1234F1Z5 (invalid checksum)
- Test format only
```

### Addresses
```python
# Use fictional addresses
- 123 Test Street, Example City
- 456 Sample Road, Test District
```

## Contributing Samples

When adding sample documents:

1. Ensure complete sanitization
2. Add a README to each subdirectory explaining the sample
3. Document the purpose of each sample
4. Include expected extraction results if applicable
5. Update this README with new additions

## Automated Testing

Samples in this directory are used for:
- Automated test cases
- Extraction accuracy testing
- OCR quality testing
- Classification testing
- Integration testing

## Privacy Commitment

This repository is committed to privacy and data protection. All sample documents must be completely sanitized before inclusion.

## Contact

For questions about sample document policies, please open an issue in the repository.
