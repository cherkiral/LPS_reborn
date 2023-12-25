import React, { useState, useEffect } from 'react';
import { COLUMNS } from './constants';
import './App.css';

function ColumnSelector() {
    const [selectedColumns, setSelectedColumns] = useState([]);
    const [filters, setFilters] = useState({});
    const [isDistinct, setIsDistinct] = useState(false);

    useEffect(() => {
        const initialFilters = COLUMNS.reduce((acc, column) => {
            acc[column] = [];
            return acc;
        }, {});
        setFilters(initialFilters);
    }, []);

    const handleCheckboxChange = (column) => {
        setSelectedColumns(prevSelectedColumns =>
            prevSelectedColumns.includes(column)
                ? prevSelectedColumns.filter(col => col !== column)
                : [...prevSelectedColumns, column]
        );
    };

    const handleAddFilter = (column) => {
        setFilters(prevFilters => ({
            ...prevFilters,
            [column]: [...(prevFilters[column] || []), { type: 'eq', value: '' }]
        }));
    };

    const handleFilterTypeChange = (column, index, filterType) => {
        setFilters(prevFilters => ({
            ...prevFilters,
            [column]: prevFilters[column].map((filter, i) =>
                i === index ? { ...filter, type: filterType } : filter
            )
        }));
    };

    const handleFilterValueChange = (column, index, value) => {
        setFilters(prevFilters => ({
            ...prevFilters,
            [column]: prevFilters[column].map((filter, i) =>
                i === index ? { ...filter, value: value } : filter
            )
        }));
    };

    const handleDownloadReport = async () => {
        try {
            const orderedSelectedColumns = COLUMNS.filter(column => selectedColumns.includes(column));
            const preparedFilters = Object.keys(filters).reduce((acc, key) => {
                if (orderedSelectedColumns.includes(key)) {
                    acc[key] = filters[key].reduce((filterAcc, currentFilter) => {
                        return {...filterAcc, [currentFilter.type]: currentFilter.value};
                    }, {});
                }
                return acc;
            }, {});

            const transformers = {};
            if (isDistinct) {
                transformers.distinct = true; // Apply distinct to all selected columns
            }

            const response = await fetch('http://localhost:8000/filter_data', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({selected_columns: orderedSelectedColumns, filters: preparedFilters, transformers})
            });

            if (!response.ok) throw new Error('Error fetching data');
            const data = await response.json();
            const filteredData = data.data;

            const reportResponse = await fetch('http://localhost:8000/create_report', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({data: filteredData, names: orderedSelectedColumns})
            });

            if (!reportResponse.ok) throw new Error('Error generating report');
            const fileBlob = await reportResponse.blob();
            const fileURL = URL.createObjectURL(fileBlob);
            const link = document.createElement('a');
            link.href = fileURL;
            link.download = 'report.xlsx';
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            URL.revokeObjectURL(fileURL);
        } catch (error) {
            console.error('Error:', error);
        }
    };

    return (
        <div className="column-selector">
            <div className="scroll-container">
                {COLUMNS.map(column => (
                    <div key={column} className="column-item">
                        <label className="checkbox-container">
                            {column}
                            <input
                                type="checkbox"
                                checked={selectedColumns.includes(column)}
                                onChange={() => handleCheckboxChange(column)}
                            />
                        </label>
                        {selectedColumns.includes(column) && (
                            <div>
                                {filters[column]?.map((filter, index) => (
                                    <div key={index}>
                                        <select
                                            value={filter.type}
                                            onChange={e => handleFilterTypeChange(column, index, e.target.value)}
                                        >
                                            <option value="eq">Equals</option>
                                            <option value="neq">Not Equals</option>
                                            <option value="contains">Contains</option>
                                            <option value="ncontains">Does Not Contain</option>
                                            <option value="begins_with">Begins With</option>
                                            <option value="nbegins_with">Does Not Begin With</option>
                                            <option value="ends_with">Ends With</option>
                                            <option value="nends_with">Does Not End With</option>
                                            <option value="is_empty">Is Empty</option>
                                            <option value="is_not_empty">Is Not Empty</option>
                                        </select>
                                        <input
                                            type="text"
                                            value={filter.value}
                                            onChange={e => handleFilterValueChange(column, index, e.target.value)}
                                        />
                                    </div>
                                ))}
                                <button onClick={() => handleAddFilter(column)}>Add Filter</button>
                            </div>
                        )}
                    </div>
                ))}
            </div>
            <button onClick={() => setIsDistinct(!isDistinct)}>
                {isDistinct ? "Undo Distinct" : "Apply Distinct"}
            </button>
            <button onClick={handleDownloadReport} className="submit-button">Download Report</button>
        </div>
    );
}

export default ColumnSelector;