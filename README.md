# Heat Generator and Exporter

A Streamlit-based web application for generating and managing competition heats from athlete registration data. This tool is particularly useful for sports events and competitions where you need to organize athletes into heats based on their events and categories.

## Features

- **Excel File Processing**: Upload and process athlete registration data from Excel files
- **Smart Event Handling**: Automatically splits comma-separated events into individual entries
- **Heat Generation**: Creates balanced heats based on affiliations
- **Multiple Export Options**:
  - Export transformed data (comma-separated events split into rows)
  - Export heats to Excel with proper formatting and spacing
  - Export heats to PDF with professional layout
- **Column Mapping**: Flexible column mapping interface for different input file formats
- **Date of Birth Handling**: Consistent date formatting (YYYY-MM-DD)

## Prerequisites

- Python 3.7 or higher
- Required Python packages (install using `pip install -r requirements.txt`):
  - streamlit
  - pandas
  - fpdf
  - openpyxl
  - numpy

## Installation

1. Clone the repository or download the source code
2. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. **Start the Application**:
   ```bash
   streamlit run app.py
   ```

2. **Upload Data**:
   - Click "Choose an Excel file" to upload your athlete registration data
   - The Excel file should contain columns for athlete information

3. **Map Columns**:
   - Map your Excel columns to the required fields:
     - Athlete Name
     - Bib Number
     - Affiliation
     - Event
     - Category
     - Date of Birth
   - Any additional columns will be preserved in the output

4. **View and Export Data**:
   - Preview the transformed data (events split into separate rows)
   - Download the transformed data as Excel
   - Generate and view heats
   - Export heats to Excel or PDF

## Input File Format

Your Excel file should contain the following information (column names can be mapped):
- Athlete Name
- Bib Number
- Affiliation
- Event (can be comma-separated)
- Category
- Date of Birth

## Output Formats

### Transformed Data Excel
- Contains all athlete information
- Events are split into separate rows
- Maintains all original data

### Heats Excel
- Organized by event and category
- Each heat is clearly separated with headers
- Includes proper spacing for readability
- Column widths are automatically adjusted

### Heats PDF
- Professional layout with proper formatting
- Organized by event and category
- Clear heat headers
- Optimized column widths for readability

## Features in Detail

### Event Transformation
- Handles comma-separated events (e.g., "100m, 200m")
- Also handles events separated by '&' (e.g., "100m & 200m")
- Creates separate rows for each event while maintaining athlete information

### Heat Generation
- Automatically calculates number of heats based on athletes per heat (default: 8)
- Distributes athletes in round-robin fashion
- Sorts by affiliation for balanced heats
- Assigns sequential numbers to athletes within each heat

## Tips for Best Results

1. **Input File Preparation**:
   - Ensure all required information is present
   - Use consistent formatting for events
   - Include clear column headers

2. **Column Mapping**:
   - Map all required fields for proper heat generation
   - Additional columns will be preserved in the output

3. **Export Options**:
   - Use transformed data export to verify event splitting
   - Use Excel export for further editing
   - Use PDF export for final distribution

## Troubleshooting

1. **File Upload Issues**:
   - Ensure the file is in .xlsx or .xls format
   - Check file permissions
   - Verify file is not corrupted

2. **Column Mapping Issues**:
   - Verify all required columns are present
   - Check for duplicate column names
   - Ensure proper data types

3. **Export Issues**:
   - Check available disk space
   - Verify write permissions
   - Ensure no other program is using the output file

## Contributing

Feel free to submit issues, fork the repository, and create pull requests for any improvements.

Developed by Mohit Dhillon

## License

This project is licensed under the MIT License - see the LICENSE file for details. 