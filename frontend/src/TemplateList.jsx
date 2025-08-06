import { useEffect, useState } from "react";
import { AgGridReact } from "ag-grid-react";

import { ModuleRegistry, AllCommunityModule } from "ag-grid-community";
import axiosInstance from "./axiosInstance";

ModuleRegistry.registerModules([AllCommunityModule]);

export default function TemplateList() {
  const [rowData, setRowData] = useState([]);

  const columnDefs = [
    { headerName: "Template Name", field: "name" },
    { headerName: "Status", field: "status" },
    { headerName: "category", field: "category" },
  ];

  useEffect(() => {
    const fetchTemplates = async () => {
      try {
        const response = await axiosInstance.get("api/v1/menu/templates-list/");

        if (response.status === 200) {
          setRowData(response.data.templates_table);
        }
      } catch (error) {
        console.error("Error fetching templates", error);
      }
    };
    fetchTemplates();
  }, []);
  return (
    <>
      <h1> Templates List </h1>
      <div className="ag-theme-alpine" style={{ height: 300, width: "60%" }}>
        <AgGridReact rowData={rowData} columnDefs={columnDefs} />
      </div>
    </>
  );
}
