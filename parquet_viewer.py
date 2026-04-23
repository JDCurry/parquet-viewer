"""
Parquet Viewer Application
A lightweight GUI for viewing and exploring parquet files

Features:
- Table view with pagination
- Schema inspector
- Column filtering and search
- Export to CSV/Excel
- Statistics panel
"""

import sys
import os
from pathlib import Path
from typing import Optional

import pandas as pd
import pyarrow.parquet as pq
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QPushButton, QFileDialog, QLabel,
    QSpinBox, QComboBox, QLineEdit, QTabWidget, QTextEdit, QMessageBox,
    QHeaderView, QSplitter, QTreeWidget, QTreeWidgetItem
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont, QColor, QIcon
from PyQt6.QtCore import pyqtSignal, QTimer


class ParquetViewer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Parquet Viewer")
        self.setGeometry(100, 100, 1400, 900)
        
        self.df = None
        self.parquet_file = None
        self.current_page = 0
        self.rows_per_page = 100
        
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout()
        
        # Toolbar
        toolbar_layout = QHBoxLayout()
        
        # File button
        self.open_btn = QPushButton("Open Parquet File")
        self.open_btn.clicked.connect(self.open_file)
        toolbar_layout.addWidget(self.open_btn)
        
        # File path label
        self.file_label = QLabel("No file loaded")
        self.file_label.setStyleSheet("color: gray; font-style: italic;")
        toolbar_layout.addWidget(self.file_label)
        
        toolbar_layout.addStretch()
        
        # Rows per page
        toolbar_layout.addWidget(QLabel("Rows per page:"))
        self.rows_spinbox = QSpinBox()
        self.rows_spinbox.setValue(100)
        self.rows_spinbox.setRange(10, 1000)
        self.rows_spinbox.valueChanged.connect(self.on_rows_changed)
        toolbar_layout.addWidget(self.rows_spinbox)
        
        main_layout.addLayout(toolbar_layout)
        
        # Tab widget
        self.tabs = QTabWidget()
        
        # Tab 1: Data View
        self.table_widget = QTableWidget()
        self.table_widget.setColumnCount(0)
        self.table_widget.setRowCount(0)
        self.tabs.addTab(self.table_widget, "Data")
        
        # Tab 2: Schema
        self.schema_tree = QTreeWidget()
        self.schema_tree.setHeaderLabels(["Column", "Type", "Null Count", "Metadata"])
        self.tabs.addTab(self.schema_tree, "Schema")
        
        # Tab 3: Statistics
        self.stats_text = QTextEdit()
        self.stats_text.setReadOnly(True)
        self.tabs.addTab(self.stats_text, "Statistics")
        
        # Tab 4: Search/Filter
        filter_layout = QVBoxLayout()
        
        filter_widget = QWidget()
        filter_inner_layout = QHBoxLayout()
        filter_inner_layout.addWidget(QLabel("Search in column:"))
        
        self.search_column = QComboBox()
        filter_inner_layout.addWidget(self.search_column)
        
        filter_inner_layout.addWidget(QLabel("Contains:"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Enter search term...")
        filter_inner_layout.addWidget(self.search_input)
        
        search_btn = QPushButton("Search")
        search_btn.clicked.connect(self.search)
        filter_inner_layout.addWidget(search_btn)
        
        reset_btn = QPushButton("Reset")
        reset_btn.clicked.connect(self.reset_view)
        filter_inner_layout.addWidget(reset_btn)
        
        filter_widget.setLayout(filter_inner_layout)
        filter_layout.addWidget(filter_widget)
        
        self.search_results = QTableWidget()
        filter_layout.addWidget(self.search_results)
        
        search_tab = QWidget()
        search_tab.setLayout(filter_layout)
        self.tabs.addTab(search_tab, "Search")
        
        main_layout.addWidget(self.tabs)
        
        # Pagination controls
        pagination_layout = QHBoxLayout()
        
        self.prev_btn = QPushButton("Previous")
        self.prev_btn.clicked.connect(self.prev_page)
        pagination_layout.addWidget(self.prev_btn)
        
        self.page_label = QLabel("Page: 0/0")
        pagination_layout.addWidget(self.page_label)
        
        self.next_btn = QPushButton("Next")
        self.next_btn.clicked.connect(self.next_page)
        pagination_layout.addWidget(self.next_btn)
        
        pagination_layout.addStretch()
        
        # Export buttons
        export_csv_btn = QPushButton("Export to CSV")
        export_csv_btn.clicked.connect(self.export_csv)
        pagination_layout.addWidget(export_csv_btn)
        
        export_excel_btn = QPushButton("Export to Excel")
        export_excel_btn.clicked.connect(self.export_excel)
        pagination_layout.addWidget(export_excel_btn)
        
        main_layout.addLayout(pagination_layout)
        
        # Status bar
        self.statusBar().showMessage("Ready")
        
        central_widget.setLayout(main_layout)
        
    def open_file(self):
        """Open a parquet file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open Parquet File",
            "",
            "Parquet Files (*.parquet);;All Files (*)"
        )
        
        if file_path:
            try:
                self.statusBar().showMessage(f"Loading: {file_path}...")
                self.parquet_file = file_path
                
                # Load parquet file
                self.df = pd.read_parquet(file_path)
                self.current_page = 0
                
                # Update UI with file info
                self.file_label.setText(f"File: {Path(file_path).name} ({len(self.df):,} rows × {len(self.df.columns)} cols)")
                
                # Update search column dropdown
                self.search_column.clear()
                self.search_column.addItems(self.df.columns)
                
                # Try to load schema
                try:
                    self.load_schema()
                except Exception as e:
                    print(f"Warning: Schema loading failed: {e}")
                    self.schema_tree.addTopLevelItem(QTreeWidgetItem(["[Schema unavailable]"]))
                
                # Try to load statistics
                try:
                    self.load_statistics()
                except Exception as e:
                    print(f"Warning: Statistics loading failed: {e}")
                    self.stats_text.setText(f"Statistics unavailable: {str(e)}\n\nFile loaded with {len(self.df)} rows × {len(self.df.columns)} columns")
                
                # Try to display data
                try:
                    self.display_page()
                    self.statusBar().showMessage(f"✓ Loaded: {file_path}")
                except Exception as e:
                    print(f"Error: Display failed: {e}")
                    self.statusBar().showMessage(f"Loaded file but display error: {str(e)}")
                    QMessageBox.warning(self, "Display Warning", f"File loaded but could not display data:\n\n{str(e)}")
                
            except Exception as e:
                print(f"Fatal error: {e}")
                self.statusBar().showMessage(f"Error: {str(e)}")
                QMessageBox.critical(self, "Error", f"Failed to load file:\n\n{str(e)}")
                
    def load_schema(self):
        """Load and display schema information"""
        if self.df is None:
            return
            
        self.schema_tree.clear()
        
        try:
            parquet_file = pq.ParquetFile(self.parquet_file)
            schema = parquet_file.schema_arrow
            
            for i, field in enumerate(schema):
                column_name = field.name
                column_type = str(field.type)
                null_count = self.df[column_name].isnull().sum()
                
                item = QTreeWidgetItem([
                    column_name,
                    column_type,
                    str(null_count),
                    ""
                ])
                self.schema_tree.addTopLevelItem(item)
                
        except Exception as e:
            self.schema_tree.addTopLevelItem(QTreeWidgetItem(["Error", str(e)]))
            
    def load_statistics(self):
        """Calculate and display statistics"""
        if self.df is None:
            return
            
        stats = f"""
DATASET STATISTICS
═══════════════════════════════════════════

Total Rows: {len(self.df):,}
Total Columns: {len(self.df.columns)}

COLUMNS
───────────────────────────────────────────
"""
        for col in self.df.columns:
            dtype = str(self.df[col].dtype)
            null_count = self.df[col].isnull().sum()
            
            stats += f"\n{col}\n"
            stats += f"  Type: {dtype}\n"
            stats += f"  Null count: {null_count}\n"
            
            # Try to count unique values, skip for unhashable types
            try:
                unique_count = self.df[col].nunique()
                stats += f"  Unique values: {unique_count}\n"
            except (TypeError, ValueError):
                stats += f"  Unique values: [complex type - unable to count]\n"
            
            # Statistics for numeric columns
            if self.df[col].dtype in ['int64', 'float64']:
                try:
                    stats += f"  Min: {self.df[col].min()}\n"
                    stats += f"  Max: {self.df[col].max()}\n"
                    stats += f"  Mean: {self.df[col].mean():.2f}\n"
                except:
                    pass
            
        self.stats_text.setText(stats)
        
    def display_page(self):
        """Display current page of data"""
        if self.df is None:
            return
            
        try:
            start = self.current_page * self.rows_per_page
            end = start + self.rows_per_page
            page_df = self.df.iloc[start:end]
            
            # Clear existing data
            self.table_widget.setRowCount(0)
            self.table_widget.setColumnCount(0)
            
            # Set dimensions
            self.table_widget.setColumnCount(len(page_df.columns))
            self.table_widget.setRowCount(len(page_df))
            self.table_widget.setHorizontalHeaderLabels(page_df.columns)
            
            # Populate table with proper data handling
            for row_idx in range(len(page_df)):
                for col_idx in range(len(page_df.columns)):
                    try:
                        value = page_df.iloc[row_idx, col_idx]
                        
                        # Handle null values
                        if pd.isna(value):
                            item = QTableWidgetItem("NULL")
                            item.setBackground(QColor(200, 200, 200))
                        else:
                            # Convert to string safely
                            value_str = str(value)
                            
                            # Truncate long strings
                            if len(value_str) > 100:
                                value_str = value_str[:97] + "..."
                            
                            item = QTableWidgetItem(value_str)
                        
                        self.table_widget.setItem(row_idx, col_idx, item)
                    except Exception as e:
                        # Handle problematic cells
                        item = QTableWidgetItem("[Error]")
                        item.setBackground(QColor(255, 200, 200))
                        self.table_widget.setItem(row_idx, col_idx, item)
                        print(f"Warning: Could not display cell [{row_idx}, {col_idx}]: {e}")
            
            # Set reasonable column widths (don't auto-resize - too slow)
            self.table_widget.setColumnWidth(0, 150)
            for col_idx in range(1, len(page_df.columns)):
                self.table_widget.setColumnWidth(col_idx, 150)
            
            # Update pagination
            total_pages = (len(self.df) + self.rows_per_page - 1) // self.rows_per_page
            self.page_label.setText(f"Page: {self.current_page + 1}/{total_pages}")
            
            self.prev_btn.setEnabled(self.current_page > 0)
            self.next_btn.setEnabled(self.current_page < total_pages - 1)
            
            self.statusBar().showMessage(f"Displayed {len(page_df)} rows")
            
        except Exception as e:
            print(f"Error in display_page: {e}")
            QMessageBox.warning(self, "Display Error", f"Could not display data: {str(e)}")
        
    def next_page(self):
        """Go to next page"""
        total_pages = (len(self.df) + self.rows_per_page - 1) // self.rows_per_page
        if self.current_page < total_pages - 1:
            self.current_page += 1
            self.display_page()
            
    def prev_page(self):
        """Go to previous page"""
        if self.current_page > 0:
            self.current_page -= 1
            self.display_page()
            
    def on_rows_changed(self):
        """Update rows per page"""
        self.rows_per_page = self.rows_spinbox.value()
        self.current_page = 0
        self.display_page()
        
    def search(self):
        """Search in selected column"""
        if self.df is None:
            return
            
        column = self.search_column.currentText()
        search_term = self.search_input.text().lower()
        
        if not search_term:
            QMessageBox.warning(self, "Warning", "Please enter a search term")
            return
            
        try:
            # Convert to string for searching
            mask = self.df[column].astype(str).str.contains(search_term, case=False, na=False)
            results = self.df[mask]
            
            self.search_results.setRowCount(len(results))
            self.search_results.setColumnCount(len(results.columns))
            self.search_results.setHorizontalHeaderLabels(results.columns)
            
            for row_idx, (_, row) in enumerate(results.iterrows()):
                for col_idx, value in enumerate(row):
                    value_str = str(value)[:100]
                    self.search_results.setItem(row_idx, col_idx, QTableWidgetItem(value_str))
                    
            self.statusBar().showMessage(f"Found {len(results)} matching rows")
        except Exception as e:
            QMessageBox.critical(self, "Search Error", f"Search failed: {str(e)}")
        
    def reset_view(self):
        """Reset to first page"""
        self.current_page = 0
        self.search_input.clear()
        self.display_page()
        
    def export_csv(self):
        """Export data to CSV"""
        if self.df is None:
            QMessageBox.warning(self, "Warning", "No file loaded")
            return
            
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save as CSV",
            "",
            "CSV Files (*.csv)"
        )
        
        if file_path:
            try:
                # Convert complex types to strings for export
                export_df = self.df.copy()
                for col in export_df.columns:
                    if export_df[col].dtype == 'object':
                        try:
                            export_df[col] = export_df[col].astype(str)
                        except:
                            pass
                
                export_df.to_csv(file_path, index=False)
                QMessageBox.information(self, "Success", f"Exported {len(export_df)} rows to {file_path}")
                self.statusBar().showMessage(f"Exported to {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Export failed: {str(e)}")
                
    def export_excel(self):
        """Export data to Excel"""
        if self.df is None:
            QMessageBox.warning(self, "Warning", "No file loaded")
            return
            
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save as Excel",
            "",
            "Excel Files (*.xlsx)"
        )
        
        if file_path:
            try:
                # Convert complex types to strings for export
                export_df = self.df.copy()
                for col in export_df.columns:
                    if export_df[col].dtype == 'object':
                        try:
                            export_df[col] = export_df[col].astype(str)
                        except:
                            pass
                
                export_df.to_excel(file_path, index=False, sheet_name="Data")
                QMessageBox.information(self, "Success", f"Exported {len(export_df)} rows to {file_path}")
                self.statusBar().showMessage(f"Exported to {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Export failed: {str(e)}")


def main():
    app = QApplication(sys.argv)
    viewer = ParquetViewer()
    viewer.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
