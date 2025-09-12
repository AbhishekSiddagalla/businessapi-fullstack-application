import { AgGridReact } from "ag-grid-react";
import { ModuleRegistry, AllCommunityModule } from "ag-grid-community";
import { useEffect, useState } from "react";
import axiosInstance from "./axiosInstance";

ModuleRegistry.registerModules([AllCommunityModule]);

export default function Reports() {
  const [rowData, setRowData] = useState([]);

  useEffect(() => {
    const fetchReport = async () => {
      try {
        const response = await axiosInstance.get("api/v1/menu/report/");
      } catch (error) {
        console.error("Error Fetching reports", error);
      }
    };
    fetchReport;
  }, []);

  const columnDefs = [
    { headerName: "Template ID", field: "" },
    { headerName: "Phone number", field: "" },
    { headerName: "Category", field: "" },
    { headerName: "Charges", field: "" },
  ];
  return (
    <>
      <h1> Reports </h1>
      <div className="ag-theme-alpine" style={{ height: 300, width: "80%" }}>
        <AgGridReact rowData={rowData} columnDefs={columnDefs}></AgGridReact>
      </div>
    </>
  );
}
