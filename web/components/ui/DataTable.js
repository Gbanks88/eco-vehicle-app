import { useState, useEffect } from 'react';
import { useTheme } from './CustomTheme';

export default function DataTable({
  columns,
  data,
  pagination = true,
  pageSize = 10,
  sortable = true,
  searchable = true,
  loading = false
}) {
  const { theme } = useTheme();
  const [currentPage, setCurrentPage] = useState(1);
  const [sortConfig, setSortConfig] = useState({ key: null, direction: 'asc' });
  const [searchTerm, setSearchTerm] = useState('');
  const [filteredData, setFilteredData] = useState(data);

  // Update filtered data when props change
  useEffect(() => {
    let result = [...data];

    // Apply search
    if (searchTerm) {
      result = result.filter(item =>
        Object.values(item).some(value =>
          String(value).toLowerCase().includes(searchTerm.toLowerCase())
        )
      );
    }

    // Apply sort
    if (sortConfig.key) {
      result.sort((a, b) => {
        const aValue = a[sortConfig.key];
        const bValue = b[sortConfig.key];
        
        if (aValue < bValue) return sortConfig.direction === 'asc' ? -1 : 1;
        if (aValue > bValue) return sortConfig.direction === 'asc' ? 1 : -1;
        return 0;
      });
    }

    setFilteredData(result);
    setCurrentPage(1);
  }, [data, searchTerm, sortConfig]);

  // Calculate pagination
  const totalPages = Math.ceil(filteredData.length / pageSize);
  const startIndex = (currentPage - 1) * pageSize;
  const paginatedData = pagination
    ? filteredData.slice(startIndex, startIndex + pageSize)
    : filteredData;

  const handleSort = (key) => {
    if (!sortable) return;
    
    setSortConfig(current => ({
      key,
      direction:
        current.key === key && current.direction === 'asc' ? 'desc' : 'asc'
    }));
  };

  return (
    <div className={`bg-${theme.mode === 'dark' ? 'gray-800' : 'white'} rounded-lg shadow`}>
      {/* Search Bar */}
      {searchable && (
        <div className="p-4 border-b border-gray-200">
          <input
            type="text"
            placeholder="Search..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className={`w-full px-4 py-2 rounded-lg border
              ${theme.mode === 'dark'
                ? 'bg-gray-700 border-gray-600 text-white'
                : 'bg-white border-gray-300'
              } focus:outline-none focus:ring-2 focus:ring-blue-500`}
          />
        </div>
      )}

      {/* Table */}
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className={`text-left
              ${theme.mode === 'dark' ? 'bg-gray-700' : 'bg-gray-50'}`}
            >
              {columns.map(column => (
                <th
                  key={column.key}
                  onClick={() => handleSort(column.key)}
                  className={`px-6 py-3 text-sm font-medium
                    ${sortable ? 'cursor-pointer hover:bg-opacity-80' : ''}
                    ${theme.mode === 'dark' ? 'text-gray-200' : 'text-gray-500'}`}
                >
                  <div className="flex items-center space-x-1">
                    <span>{column.label}</span>
                    {sortable && sortConfig.key === column.key && (
                      <span>
                        {sortConfig.direction === 'asc' ? '↑' : '↓'}
                      </span>
                    )}
                  </div>
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr>
                <td
                  colSpan={columns.length}
                  className="px-6 py-4 text-center text-gray-500"
                >
                  Loading...
                </td>
              </tr>
            ) : paginatedData.length === 0 ? (
              <tr>
                <td
                  colSpan={columns.length}
                  className="px-6 py-4 text-center text-gray-500"
                >
                  No data available
                </td>
              </tr>
            ) : (
              paginatedData.map((row, index) => (
                <tr
                  key={index}
                  className={`border-t border-gray-200
                    ${theme.mode === 'dark'
                      ? 'hover:bg-gray-700'
                      : 'hover:bg-gray-50'}`}
                >
                  {columns.map(column => (
                    <td
                      key={column.key}
                      className={`px-6 py-4 text-sm
                        ${theme.mode === 'dark' ? 'text-gray-300' : 'text-gray-900'}`}
                    >
                      {column.render
                        ? column.render(row[column.key], row)
                        : row[column.key]}
                    </td>
                  ))}
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      {pagination && totalPages > 1 && (
        <div className={`px-6 py-4 border-t border-gray-200
          ${theme.mode === 'dark' ? 'bg-gray-800' : 'bg-white'}`}
        >
          <div className="flex items-center justify-between">
            <button
              onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
              disabled={currentPage === 1}
              className={`px-3 py-1 rounded text-sm
                ${currentPage === 1
                  ? 'opacity-50 cursor-not-allowed'
                  : 'hover:bg-gray-100'}`}
            >
              Previous
            </button>
            <span className={`text-sm
              ${theme.mode === 'dark' ? 'text-gray-300' : 'text-gray-600'}`}
            >
              Page {currentPage} of {totalPages}
            </span>
            <button
              onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
              disabled={currentPage === totalPages}
              className={`px-3 py-1 rounded text-sm
                ${currentPage === totalPages
                  ? 'opacity-50 cursor-not-allowed'
                  : 'hover:bg-gray-100'}`}
            >
              Next
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
