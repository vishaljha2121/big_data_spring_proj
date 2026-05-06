import React from "react";

export default function Card({ title, eyebrow, action, children, className = "" }) {
  return (
    <section className={`product-card ${className}`.trim()}>
      {(title || action) && (
        <div className="card-header">
          <div>
            {eyebrow ? <p className="card-eyebrow">{eyebrow}</p> : null}
            {title ? <h3>{title}</h3> : null}
          </div>
          {action ? <div className="card-action">{action}</div> : null}
        </div>
      )}
      {children}
    </section>
  );
}
