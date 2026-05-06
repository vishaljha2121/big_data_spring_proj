import React from "react";

export default function DataTable({ columns, rows, selectedIndex = -1, onSelect }) {
  return (
    <div className="data-table-wrap">
      <table className="data-table">
        <thead>
          <tr>{columns.map((column) => <th key={column}>{column}</th>)}</tr>
        </thead>
        <tbody>
          {rows.map((row, rowIndex) => (
            <tr
              key={row.key || rowIndex}
              className={selectedIndex === rowIndex ? "selected" : ""}
              onClick={() => onSelect && onSelect(rowIndex)}
            >
              {row.cells.map((cell, cellIndex) => <td key={cellIndex}>{cell}</td>)}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
