import streamlit as st
import pandas as pd
from fpdf import FPDF
import io
import tempfile
import os
import numpy as np

st.set_page_config(page_title="Heat Generator", layout="wide")

st.title("Heat Generator and Exporter")

# Required fields for heat generation
REQUIRED_FIELDS = {
    'Name': 'Athlete Name',
    'Bib Number': 'Bib Number',
    'Affiliation': 'Affiliation',
    'Event': 'Event',
    'Category': 'Category',
    'Date of Birth': 'Date of Birth'
}

# Standard column order for display and export
STANDARD_COLUMNS = ['SL', 'Name', 'Bib Number', 'Affiliation']

def transform_events(df):
    """
    Transform dataframe to handle comma-separated events.
    Creates separate rows for each event while maintaining other athlete information.
    """
    # Create a list to store the transformed rows
    transformed_rows = []
    
    # Iterate through each row in the dataframe
    for _, row in df.iterrows():
        # Split the events string into a list
        events_str = str(row['Event'])
        # Replace & with comma for consistent splitting
        events_str = events_str.replace('&', ',')
        events = [event.strip() for event in events_str.split(',')]
        
        # Create a new row for each event
        for event in events:
            if event == '':
                continue
            new_row = row.copy()
            new_row['Event'] = event
            transformed_rows.append(new_row)
    
    # Create a new dataframe from the transformed rows
    transformed_df = pd.DataFrame(transformed_rows)
    return transformed_df

def generate_heats(df, athletes_per_heat=8):
    """
    Generate heats based on the data.
    Returns a dictionary with event categories as keys and list of heats as values.
    """
    heats = {}
    
    # Group by event and category
    for (event, category), group in df.groupby(['Event', 'Category']):
        # Sort by affiliation
        group = group.sort_values('Affiliation')
        
        # Calculate number of heats needed
        n_athletes = len(group)
        n_heats = (n_athletes + athletes_per_heat - 1) // athletes_per_heat
        
        # Initialize empty heats
        heat_list = [pd.DataFrame() for _ in range(n_heats)]
        
        # Distribute athletes in round-robin fashion
        for i, (_, athlete) in enumerate(group.iterrows()):
            heat_number = i % n_heats  # This creates the round-robin distribution
            heat_list[heat_number] = pd.concat([heat_list[heat_number], pd.DataFrame([athlete])], ignore_index=True)
        
        # Add heat numbers and athlete numbers to each heat's dataframe
        for i, heat_df in enumerate(heat_list):
            heat_df['heat_number'] = i + 1  # Heat numbers start from 1
            heat_df['SL'] = range(1, len(heat_df) + 1)  # Athlete numbers start from 1
        
        key = f"{category} - {event}"
        heats[key] = heat_list
    
    return heats

def display_heats(heats):
    """Display heats in an organized way using Streamlit"""
    for event_category, heat_list in heats.items():
        st.subheader(event_category)
        
        for i, heat_df in enumerate(heat_list, 1):
            st.write(f"Heat {i}")
            # Use standard column order
            display_columns = STANDARD_COLUMNS + \
                            [col for col in heat_df.columns if col not in STANDARD_COLUMNS + ['heat_number']]
            st.dataframe(
                heat_df[display_columns],
                use_container_width=True
            )

def export_heats_to_excel(heats):
    """Export heats to Excel format with proper spacing and headers"""
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        for event_category, heat_list in heats.items():
            # Create a sheet for each event category
            sheet_name = event_category[:31]  # Excel sheet names limited to 31 chars
            
            # Create a list to store all dataframes with spacing
            formatted_heats = []
            
            for i, heat_df in enumerate(heat_list, 1):
                # Add heat header
                heat_header = pd.DataFrame([f"Heat {i}"], columns=['Heat'])
                formatted_heats.append(heat_header)
                
                # Add the heat data using standard column order
                export_columns = STANDARD_COLUMNS + \
                               [col for col in heat_df.columns if col not in STANDARD_COLUMNS + ['heat_number']]
                formatted_heats.append(heat_df[export_columns])
                
                # Add spacing (empty rows)
                spacing = pd.DataFrame([[''] * len(export_columns)], columns=export_columns)
                formatted_heats.append(spacing)
                formatted_heats.append(spacing)
            
            # Combine all formatted heats
            final_df = pd.concat(formatted_heats, ignore_index=True)
            
            # Write to Excel
            final_df.to_excel(writer, sheet_name=sheet_name, index=False)
            
            # Get the worksheet to adjust column widths
            worksheet = writer.sheets[sheet_name]
            for idx, col in enumerate(final_df.columns):
                max_length = max(
                    final_df[col].astype(str).apply(len).max(),
                    len(str(col))
                )
                worksheet.column_dimensions[chr(65 + idx)].width = max_length + 2
    
    output.seek(0)
    return output

def export_heats_to_pdf(heats):
    """Export heats to PDF format"""
    pdf = FPDF()
    
    for event_category, heat_list in heats.items():
        pdf.add_page()
        
        # Add title
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, event_category, ln=True, align="C")
        pdf.ln(10)
        
        for i, heat_df in enumerate(heat_list, 1):
            # Add heat number
            pdf.set_font("Arial", "B", 12)
            pdf.cell(0, 10, f"Heat {i}", ln=True)
            pdf.ln(5)
            
            # Add headers using standard column names
            pdf.set_font("Arial", "B", 10)
            headers = ['SL', 'Name', 'Bib Number', 'Affiliation', 'Date of Birth']
            col_width = [15, 55, 30, 50, 30]  

            for header, width in zip(headers, col_width):
                pdf.cell(width, 10, header, 1)
            pdf.ln()
            
            # Add data
            pdf.set_font("Arial", "", 10)
            for _, row in heat_df.iterrows():
                pdf.cell(col_width[0], 10, str(row['SL']), 1)
                pdf.cell(col_width[1], 10, str(row['Name']), 1)
                pdf.cell(col_width[2], 10, str(row['Bib Number']), 1)
                pdf.cell(col_width[3], 10, str(row['Affiliation']), 1)
                pdf.cell(col_width[4], 10, str(row['Date of Birth']), 1)
                pdf.ln()
            
            pdf.ln(10)
    
    # Save to temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
        pdf.output(tmp.name)
        tmp_path = tmp.name
    
    # Read the PDF file
    with open(tmp_path, 'rb') as f:
        pdf_bytes = f.read()
    
    # Clean up
    os.unlink(tmp_path)
    return pdf_bytes

def map_columns(df):
    """Create column mapping interface and return mapped dataframe"""
    st.subheader("Map Excel Columns")
    st.write("Please map your Excel columns to the required fields:")
    
    # Get all columns from the uploaded file
    available_columns = df.columns.tolist()
    
    # Create column mapping
    column_mapping = {}
    for field, display_name in REQUIRED_FIELDS.items():
        selected_column = st.selectbox(
            f"Select column for {display_name}",
            options=[''] + available_columns,
            key=f"map_{field}"
        )
        if selected_column:
            column_mapping[field] = selected_column
    
    # Check if all required fields are mapped
    if len(column_mapping) == len(REQUIRED_FIELDS):
        # Create new dataframe with mapped columns
        mapped_df = pd.DataFrame()
        for field, column in column_mapping.items():
            if field == 'Date of Birth':
                # Convert Date of Birth to YYYY-MM-DD format
                try:
                    # First convert to datetime to ensure proper formatting
                    mapped_df[field] = pd.to_datetime(df[column]).dt.strftime('%Y-%m-%d')
                except:
                    # If conversion fails, keep as string
                    mapped_df[field] = df[column].astype(str)
            else:
                mapped_df[field] = df[column]
        
        # Add any additional columns that weren't mapped
        unmapped_columns = [col for col in available_columns if col not in column_mapping.values()]
        for col in unmapped_columns:
            mapped_df[col] = df[col]
        
        return mapped_df
    else:
        st.warning("Please map all required fields to continue.")
        return None

# File uploader
uploaded_file = st.file_uploader("Choose an Excel file", type=['xlsx', 'xls'])

if uploaded_file is not None:
    try:
        # Read the Excel file
        df = pd.read_excel(uploaded_file)
        
        # Show column mapping interface
        mapped_df = map_columns(df)
        
        if mapped_df is not None:
            # Transform comma-separated events into separate rows
            st.subheader("Transforming Events")
            transformed_df = transform_events(mapped_df)
            
            # Show the transformed data
            st.write("Preview of transformed data (one row per event):")
            st.dataframe(transformed_df, use_container_width=True)
            
            # Export transformed data
            st.subheader("Export Options")
            st.write("Download Transformed Data:")
            transformed_output = io.BytesIO()
            with pd.ExcelWriter(transformed_output, engine='openpyxl') as writer:
                transformed_df.to_excel(writer, index=False)
            transformed_output.seek(0)
            st.download_button(
                label="Download Transformed Excel",
                data=transformed_output,
                file_name="transformed_data.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            
            st.write("---")
            st.write("Download Generated Heats:")
            
            # Generate heats
            heats = generate_heats(transformed_df)
            
            # Export buttons for heats
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("Export Heats to Excel"):
                    output = export_heats_to_excel(heats)
                    st.download_button(
                        label="Download Heats Excel",
                        data=output,
                        file_name="heats.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
            
            with col2:
                if st.button("Export Heats to PDF"):
                    pdf_bytes = export_heats_to_pdf(heats)
                    st.download_button(
                        label="Download Heats PDF",
                        data=pdf_bytes,
                        file_name="heats.pdf",
                        mime="application/pdf"
                    )
            
            # Display the heats after export options
            st.subheader("Generated Heats")
            display_heats(heats)
    
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
else:
    st.info("Please upload an Excel file to begin.") 