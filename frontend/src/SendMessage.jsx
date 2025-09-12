import { useEffect, useState } from "react";
import axiosInstance from "./axiosInstance";

export default function SendMessage() {
  const [templates, setTemplates] = useState([]);
  const [templateName, setTemplateName] = useState("");
  const [previewText, setPreviewText] = useState("");
  const [parameterPlaceholders, setParameterPlaceholders] = useState([]);
  const [headerType, setHeaderType] = useState("");
  const [headerValue, setHeaderValue] = useState(""); // holds the header value
  const [bodyValues, setBodyValues] = useState([]); // holds the placeholder values
  const [to, setTo] = useState(""); // to phone number value

  useEffect(() => {
    const fetchTemplates = async () => {
      try {
        const response = await axiosInstance.get("api/v1/menu/templates-list/");

        if (response.status === 200) {
          setTemplates(response.data.templates.data);
        }
      } catch (error) {
        console.log("Error fetching template", error);
      }
    };
    fetchTemplates();
  }, []);

  const handleTemplateNameChange = (e) => {
    const value = e.target.value;

    setTemplateName(value);

    const selectedTemplate = templates.find((t) => t.name === value);

    if (selectedTemplate) {
      const headerComponent = selectedTemplate.components.find(
        (c) => c.type === "HEADER"
      );

      const bodyComponent = selectedTemplate.components.find(
        (c) => c.type === "BODY"
      );

      setHeaderType(headerComponent ? headerComponent.format : "");
      setHeaderValue("");

      setPreviewText(bodyComponent ? bodyComponent.text : "");

      // Extracting placeholders from the body text
      const matches =
        (bodyComponent && bodyComponent.text.match(/{{\d+}}/g)) || [];
      setParameterPlaceholders(matches);

      setBodyValues(
        matches.length > 0 ? new Array(matches.length).fill("") : []
      );
    } else {
      setPreviewText("");
      setHeaderType("");
      setHeaderValue("");
      setParameterPlaceholders([]);
      setBodyValues([]);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    let headerBlock = null;

    if (headerType === "TEXT" && headerValue.trim()) {
      headerBlock = {
        type: "header",
        parameters: [{ type: "text", text: headerValue.trim() }],
      };
    } else if (headerType === "IMAGE" && headerValue.trim()) {
      headerBlock = {
        type: "header",
        parameters: [
          {
            type: "image",
            image: { link: headerValue.trim() },
          },
        ],
      };
    } else if (headerType === "VIDEO" && headerValue.trim()) {
      headerBlock = {
        type: "header",
        parameters: [
          {
            type: "video",
            video: { link: headerValue.trim() },
          },
        ],
      };
    } else if (headerType === "DOCUMENT" && headerValue.trim()) {
      headerBlock = {
        type: "header",
        parameters: [
          {
            type: "document",
            document: { link: headerValue.trim() },
          },
        ],
      };
    }

    const bodyParams = bodyValues
      .filter((val) => val && val.trim() !== "")
      .map((val) => ({
        type: "text",
        text: val.trim(),
      }));

    // payload
    const payload = {
      messaging_product: "whatsapp",
      to: to,
      type: "template",
      template: {
        name: templateName,
        language: {
          code: "en_US",
        },
        components: [
          ...(headerBlock ? [headerBlock] : []),

          ...(bodyParams.length > 0
            ? [{ type: "body", parameters: bodyParams }]
            : []),
        ],
      },
    };

    try {
      const response = await axiosInstance.post(
        "api/v1/menu/send-message/",
        payload
      );
      console.log(response);
    } catch (error) {
      console.log("error in payload", error);
    }
  };

  return (
    <div style={{ display: "flex", gap: "2rem", alignItems: "flex-start" }}>
      <form onSubmit={handleSubmit} style={{ flex: 1, textAlign: "left" }}>
        <h1>Send Message</h1>
        <div>
          <label>Template Name:</label> &nbsp;
          <input
            type="text"
            value={templateName}
            onChange={handleTemplateNameChange}
          />
          <br />
          <br />
          {parameterPlaceholders.map((placeholder, index) => (
            <div key={index}>
              <label>Parameter {index + 1}:</label> &nbsp;
              <input
                type="text"
                value={bodyValues[index] || ""}
                onChange={(e) => {
                  const newValues = [...bodyValues];
                  newValues[index] = e.target.value;
                  setBodyValues(newValues);
                }}
              />
            </div>
          ))}
          <br />
          <br />
          <label>To Numbers:</label> &nbsp;
          <input
            type="text"
            value={to}
            onChange={(e) => setTo(e.target.value)}
          />
        </div>
        <br />
        <br />
        <button>cancel</button> &nbsp;
        <button>Send</button>
      </form>
      <div
        style={{
          flex: "0 0 30%",
          border: "1px solid gray",
          padding: "1rem",
          borderRadius: "5px",
          background: "#f9f9f9",
        }}
      >
        <h3>Preview</h3>
        <p>{previewText}</p>
      </div>
    </div>
  );
}
