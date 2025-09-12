import { useEffect, useState } from "react";
import axiosInstance from "./axiosInstance";

export default function CreateTemplates() {
  const [templateName, setTemplateName] = useState("");
  const [headerType, setHeaderType] = useState("");
  const [header, setHeader] = useState("");
  const [headerFile, setHeaderFile] = useState(null);
  const [body, setBody] = useState("");
  const [parameters, setParameters] = useState("");
  const [footer, setFooter] = useState("");
  const [buttonType, setButtonType] = useState("");
  const [buttonText, setButtonText] = useState("");
  const [buttonValue, setButtonValue] = useState("");

  useEffect(() => {
    const matches = body.match(/{{\d+}}/g);
    if (matches) {
      const unique = [...new Set(matches)];
      setParameters(unique.map(() => ""));
    } else {
      setParameters([]);
    }
  }, [body]);

  const handleParameterChange = (index, value) => {
    const updated = [...parameters];
    updated[index] = value;
    setParameters(updated);
  };

  const handleCancelButton = () => {
    setTemplateName("");
    setHeaderType("");
    setHeader("");
    setHeaderFile(null);
    setBody("");
    setParameters("");
    setFooter("");
    setButtonType("");
    setButtonText("");
    setButtonValue("");
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    let components = [];

    // Header component
    if (headerType === "text" && header) {
      components.push({
        type: "HEADER",
        format: "TEXT",
        text: header,
      });
    } else if (["image", "video", "document"].includes(headerType)) {
      components.push({
        type: "HEADER",
        format: headerType.toUpperCase(),
      });
    }

    // Body Component
    if (body) {
      let bodyComponent = {
        type: "BODY",
        text: body,
      };
      if (parameters.length > 0) {
        bodyComponent.example = { body_text: [parameters] };
      }
      components.push(bodyComponent);
    }

    // footer component
    if (footer) {
      components.push({
        type: "FOOTER",
        text: footer,
      });
    }

    //buttons component
    if (buttonType && buttonText && buttonValue) {
      let buttonObj = {
        type: "BUTTONS",
        buttons: [],
      };

      if (buttonType === "url") {
        buttonObj.buttons.push({
          type: "URL",
          text: buttonText,
          url: buttonValue,
        });
      } else if (buttonType === "phone") {
        buttonObj.buttons.push({
          type: "PHONE_NUMBER",
          text: buttonText,
          phone_number: buttonValue,
        });
      }
      components.push(buttonObj);
    }

    // payload
    const payload = {
      name: templateName,
      category: "UTILITY",
      language: "en_US",
      components: components,
    };

    try {
      const response = await axiosInstance.post(
        "api/v1/menu/create-template/",
        payload
      );
      console.log(response);
      alert("Template created successfully");
    } catch (error) {
      console.log("Error creating template", error);
      alert("failed to create message");
    }
  };

  return (
    <div style={{ display: "flex", gap: "2rem", alignItems: "flex-start" }}>
      <form style={{ flex: 1, textAlign: "left" }}>
        <h1>Create Template</h1>
        <label> Template Name:</label> &nbsp;
        <input
          type="text"
          value={templateName}
          onChange={(e) => {
            const formattedValue = e.target.value.replace(/\s+/g, "_");
            setTemplateName(formattedValue);
          }}
          required
        />
        <br /> <br />
        {/* Template header part */}
        <div style={{ display: "flex", gap: "1rem" }}>
          <div>
            <label>Header Type: </label>
            <select
              value={headerType}
              onChange={(e) => {
                setHeaderType(e.target.value);
                setHeader("");
                setHeaderFile(null);
              }}
            >
              <option value="">None</option>
              <option value="text">Text</option>
              <option value="image">Image</option>
              <option value="video">Video</option>
              <option value="document">Document</option>
            </select>{" "}
            <br /> <br />
            <label> Header: </label>
            {headerType === "text" && (
              <input
                type="text"
                value={header}
                onChange={(e) => setHeader(e.target.value)}
                required
              />
            )}
            {["image", "video", "document"].includes(headerType) && (
              <input
                type="file"
                accept={
                  headerType === "image"
                    ? "image/*"
                    : headerType === "video"
                    ? "video/*"
                    : ".pdf,.doc,.docx"
                }
                onChange={(e) => setHeaderFile(e.target.files[0])}
                required
              />
            )}
          </div>
        </div>
        <br />
        {/* Template body part */}
        <label>Template Body:</label> <br /> <br />
        <textarea
          rows="5"
          cols="70"
          value={body}
          onChange={(e) => setBody(e.target.value)}
          placeholder="Enter message body, Use {{1}},{{2}},... for parameters"
          required
        ></textarea>
        <br /> <br />
        {/* parameters part */}
        {parameters.length > 0 && (
          <>
            <label>Parameters:</label> <br /> <br />
            {parameters.map((_, i) => (
              <div key={i}>
                <input
                  type="text"
                  placeholder={`parameter ${i + 1}`}
                  value={parameters[i]}
                  onChange={(e) => handleParameterChange(i, e.target.value)}
                  required
                />
                <br /> <br />
              </div>
            ))}
            <br />
          </>
        )}
        {/* Template footer part */}
        <label>Template Footer:</label> &nbsp;
        <input
          type="text"
          value={footer}
          onChange={(e) => setFooter(e.target.value)}
          placeholder="Optional"
        />
        <br /> <br />
        {/* Template Buttons part */}
        <label> Buttons: </label> &nbsp;
        <div style={{ display: "flex", alignItems: "center", gap: "5px" }}>
          <select
            value={buttonType}
            onChange={(e) => {
              setButtonType(e.target.value);
              setButtonText("");
              setButtonValue("");
            }}
          >
            <option value="">select</option>
            <option value="url">URL</option>
            <option value="phone">Phone Number</option>
          </select>{" "}
          <br />
          <br />
          {/* conditional fields for button type */}
          {buttonType === "url" && (
            <>
              <label>Label: </label> &nbsp;
              <input
                type="text"
                value={buttonText}
                onChange={(e) => setButtonText(e.target.value)}
                required
              />
              <br /> <br />
              <label>URL: </label> &nbsp;
              <input
                type="text"
                value={buttonValue}
                onChange={(e) => setButtonValue(e.target.value)}
                required
              />
            </>
          )}
          {buttonType === "phone" && (
            <>
              <label>Label: </label> &nbsp;
              <input
                type="text"
                value={buttonText}
                onChange={(e) => setButtonText(e.target.value)}
                required
              />
              &nbsp;
              <label>Phone Number:</label> &nbsp;
              <input
                type="text"
                value={buttonValue}
                onChange={(e) => setButtonValue(e.target.value)}
                required
              />
            </>
          )}
        </div>
        <br /> <br />
        <button type="button" onClick={handleCancelButton}>
          cancel
        </button>{" "}
        &nbsp;
        <button type="submit" onClick={handleSubmit}>
          Create
        </button>
      </form>

      {/* Preview part */}
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
        {headerType === "text" && header && (
          <p>
            <b>{header}</b>
          </p>
        )}
        {["image", "video"].includes(headerType) &&
          headerFile &&
          (headerType === "image" ? (
            <img
              src={URL.createObjectURL(headerFile)}
              alt="Preview"
              style={{ maxWidth: "100%", borderRadius: "4px" }}
            />
          ) : (
            <video
              src={URL.createObjectURL(headerFile)}
              controls
              style={{ maxWidth: "100%", borderRadius: "4px" }}
            />
          ))}

        {headerType === "document" && headerFile && (
          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: "10px",
              border: "1px solid #ccc",
              borderRadius: "6px",
              padding: "8px",
              background: "#f9f9f9",
              maxWidth: "250px",
            }}
          >
            {headerFile.name}
          </div>
        )}

        {body && (
          <p>
            {body.replace(/{{\d+}}/g, (match) => {
              const index = Number(match.replace(/[{}]/g)) - 1;
              return parameters[index] || match;
            })}
          </p>
        )}
        {footer && <p>{footer}</p>}
      </div>
    </div>
  );
}
