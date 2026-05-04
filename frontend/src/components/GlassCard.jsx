import React from "react";

export default function GlassCard({ as: Tag = "section", className = "", children, id }) {
  return <Tag id={id} className={`glass-card ${className}`.trim()}>{children}</Tag>;
}
